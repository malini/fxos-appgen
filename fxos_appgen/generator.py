from marionette import Marionette
import mozdevice

import json
from optparse import OptionParser
import os
import pkg_resources
import sys
from zipfile import ZipFile

APP_TYPES = ["certified", "web", "privileged"]

def cli():
    parser = OptionParser(usage="usage: %prog [options] app_name " \
                                "permission_file", description="app_name "\
                                "is the name of the app you want to generate " \
                                "and permission_file is the path to the " \
                                "permissions file.")
    # TODO: take in device serial and marionette port, though likely won't be useful
    parser.add_option("--adb-path", dest="adb_path",
                        help="path to adb executable. If not passed, we assume"\
                        " that 'adb' is on the path")
    parser.add_option("--app-path", dest="app_path",
                        help="If passed, the app's zip file will be stored at" \
                        " the given filepath. Otherwise, it will be in the"\
                        " current working directory as app.zip")
    parser.add_option("--install", dest="install", default=False,
                        action="store_true", help="If passed, the app will be" \
                        " installed on your phone")
    parser.add_option("--type", dest="type", default="certified",
                        help="Application type, either 'certified'," \
                        " 'privileged' or 'web'. Defaults to 'certified'")
    parser.add_option("--version", dest="version", default="1.3",
                        help="FxOS version. Defaults to 1.3")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print "Please pass in the app_name and permission_file"
        print "Run with --help for more information"
        sys.exit(1)

    app_name = args[0]
    permissions = None
    permissions_file = args[1]
    with open(permissions_file, "r") as f:
        permissions = json.load(f)

    manifest = None
    manifest_path = "%s/manifest.webapp" % (options.version)
    manifest_path = pkg_resources.resource_filename(__name__,
                                                    os.path.sep.join(
                                                    ["resources",
                                                    manifest_path]))
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    print "Creating manifest"
    manifest = create_manifest(app_name, permissions, manifest, options.type,
                               options.version)

    #TODO : ask for workingdir for temp files
    print "Creating the application's zip file"
    app_path = package_app(manifest, options.app_path)

    if options.install:
        print "Installing the app"
        install_app(app_name, app_path, options.adb_path)
        print "The application should be on your phone"
    print "Done."

def create_manifest(app_name, permissions, manifest, app_type, version):
    manifest["name"] = app_name
    app_type = app_type.lower()
    if app_type not in APP_TYPES:
        raise Exception("Need to pass in one of the following app types: %s" % 
                  APP_TYPES)
        sys.exit(1)
    manifest["type"] = app_type
    if "description" in permissions:
        manifest["description"] = permissions["description"]
    manifest["permissions"] = permissions["permissions"]
    # Check if user provided messages
    if "messages" in permissions:
        manifest["messages"] = permissions["messages"]
    else:
        launch_path = manifest["launch_path"]
        all_messages = None
        messages_path = "%s/messages.json" % (version)
        messages_path = pkg_resources.resource_filename(__name__,
                                                        os.path.sep.join(
                                                        ["resources",
                                                          messages_path]))

        with open(messages_path, "r") as f:
            all_messages = json.load(f)

        def add_messages(messages, manifest):
            for message in messages:
                manifest["messages"].append({message: launch_path})

        # Add general messages for the default case
        add_messages(all_messages["general"], manifest)

        for permission in manifest["permissions"]:
            related_messages = all_messages[permission]
            # If we have a dictionary, then we should apply the messages if
            # we have the appropriate access level
            if type(related_messages) is dict:
                level = manifest["permissions"][permission]["access"]
                for key in related_messages:
                    # use "in" to allow us to use "read" key on both 
                    # "readwrite", "readonly" and "read".
                    if key in level:
                        messages = related_messages[key]
                        add_messages(messages, manifest)
                        break
            else:
                add_messages(related_messages, manifest)
                
    if "datastores-access" in permissions:
        manifest["datastores-access"] = permissions["datastores-access"]
    if "datastores-owned" in permissions:
        manifest["datastores-owned"] = permissions["datastores-owned"]

    return manifest


def package_app(manifest, path):
    # create the manifest.webapp file
    manifest_path = os.path.sep.join([os.getcwd(), "manifest.webapp"])
    manifest_file = open(manifest_path, "w")
    manifest_file.write(json.dumps(manifest, 
                        indent=4, separators=(",", ": ")))
    manifest_file.close()

    index_html = pkg_resources.resource_filename(__name__,
                                                 os.path.sep.join(
                                                 ["resources",
                                                  "index.html"]))
    # create the app.zip
    app_path = path
    if not app_path:
        app_path = os.path.sep.join([os.getcwd(), "app.zip"])
    with ZipFile(app_path, "w") as zip_file:
        zip_file.write(index_html, "index.html")
        zip_file.write(manifest_path, "manifest.webapp")
    os.remove(manifest_path)

    return app_path

def install_app(app_name, app_path, adb_path=None):
    dm = None
    if adb_path:
        dm = mozdevice.DeviceManagerADB(adbPath=adb_path)
    else:
        dm = mozdevice.DeviceManagerADB()

    #TODO: replace with app name
    installed_app_name = app_name.lower()
    installed_app_name = installed_app_name.replace(" ", "-")
    if dm.dirExists("/data/local/webapps/%s" % installed_app_name):
        raise Exception("%s is already installed" % app_name)
        sys.exit(1)
    app_zip = os.path.basename(app_path)
    dm.pushFile("%s" % app_path, "/data/local/%s" % app_zip)
    # forward the marionette port
    ret = dm.forward("tcp:2828", "tcp:2828")
    if ret != 0:
        raise Exception("Can't use localhost:2828 for port forwarding." \
                        "Is something else using port 2828?")

    # install the app
    install_js = pkg_resources.resource_filename(__name__,
                                                 os.path.sep.join([
                                                   'app_install.js']))
    f = open(install_js, "r")
    script = f.read()
    f.close()
    script = script.replace("YOURAPPID", installed_app_name)
    script = script.replace("YOURAPPZIP", app_zip)
    m = Marionette()
    m.start_session()
    m.set_context("chrome")
    m.set_script_timeout(5000)
    m.execute_async_script(script)
    m.delete_session()

if __name__ == "__main__":
    cli()
