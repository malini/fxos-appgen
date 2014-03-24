from marionette import Marionette
import mozdevice

import json
from optparse import OptionParser
import os
import sys


def main(options, args):
    app_name = args[0]
    permissions_file = args[1]
    permissions = None
    manifest = None

    with open(permissions_file, "r") as f:
        permissions = json.load(f)

    manifest_path = "%s/manifest.webapp" % (options.version)
    manifest_path = os.path.sep.join([os.getcwd(),
                                      'references',
                                      manifest_path])
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    manifest["permissions"] = permissions["permissions"]
    # Check if user provided messages
    if "messages" in permissions:
        manifest["messages"] = permissions["messages"]
    else:
        launch_path = manifest["launch_path"]
        all_messages = None
        messages_path = "%s/messages.json" % (options.version)
        messages_path = os.path.sep.join([os.getcwd(),
                                          'references',
                                           messages_path])

        with open(messages_path, "r") as f:
            all_messages = json.load(f)

        def add_messages(messages, manifest):
            for message in messages:
                manifest["messages"].append({message: launch_path})

        # Add general messages for the default case
        add_messages(all_messages["general"], manifest)

        #TODO: readwrite should be accounted for in settings!
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
    import pdb;pdb.set_trace()

def install_app():
    print "Pushing app to device"
    dm = None
    if options.adb_path:
        dm = mozdevice.DeviceManagerADB(adbPath=options.adb_path)
    else:
        dm = mozdevice.DeviceManagerADB()
    #TODO: replace with app name
    if dm.dirExists("/data/local/webapps/certtest-app"):
        print "CertTest app is already installed"
        return
    dm.pushFile("certtest_app.zip", "/data/local/certtest_app.zip")
    # forward the marionette port
    print "Forwarding marionette port"
    ret = dm.forward("tcp:2828", "tcp:2828")
    if ret != 0:
        #TODO: right thing here is to keep trying local ports and pass that value in our config
        raise Exception("Can't use localhost:2828 for port forwarding. Is something else using port 2828?")
    # install the app
    print "installing the app"
    f = open("app_install.js", "r")
    script = f.read()
    f.close()
    m = Marionette()
    m.start_session()
    m.set_context("chrome")
    m.set_script_timeout(5000)
    m.execute_async_script(script)
    m.delete_session()

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog [options] app_name " \
                                "permission_file", description="app_name "\
                                "is the name of the app you want to generate " \
                                "and permission_file is the path to the " \
                                "permissions file.")
    # TODO: take in device serial and marionette port, though likely won't be useful
    parser.add_option("--adb-path", dest="adb_path",
                        help="path to adb executable. If not passed, we assume"\
                        " that 'adb' is on the path")
    parser.add_option("--install", dest="install", default=False,
                        action="store_true", help="If passed, the app will be" \
                        " installed on your phone")
    parser.add_option("--certified", dest="cert", default=False,
                        action="store_true", help="If passed, the app will be" \
                        " marked as a 'certified' app.")
    parser.add_option("--app-path", dest="appzip",
                        help="If passed, the app's zip file will be stored at" \
                        " the given filepath. Otherwise, it will be in the"\
                        " current working directory as app.zip")
    parser.add_option("--version", dest="version", default="1.3",
                        help="FxOS version. Default is 1.3")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print "Please pass in the app_name and permission_file"
        print "Run with --help for more information"
        sys.exit(1)
    main(options, args)
