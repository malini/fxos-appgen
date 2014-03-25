==================
FxOS App Generator
==================

A tool to generate, and optionally install, an FxOS application with any given
permissions

Requirements
============

Your phone must have Marionette installed on it and running on port 2828.

You must also have 'adb' installed.

If you need to install adb, see
https://developer.mozilla.org/en-US/Firefox_OS/Debugging/Installing_ADB.

Once installed, add adb to your PATH in your ~/.bashrc
or equivalent file, by adding the following line to the file
(replacing $SDK_HOME with the location of the android sdk):

    PATH=$SDK_HOME:$PATH

Setup
=====

You should set up and run this tool inside a virtual environment.  From the
root directory of your source checkout, run::

    virtualenv venv

Then activate the virtualenv::

    source bin/activate

To install::

    python setup.py install

Usage
=====

Once installed, you will have access to 'fxos_appgen' from the command line.

You can run it like so::

    fxos_appgen [options] app_name details_file

By default, it assumes 'adb' is on your path and will generate a v1.3 certified
app named 'app.zip' in your current working directory. It will not install the
app by default.

To modify this behaviour, use the options listed here::

    fxos_appgen --help

Details File
================

The details_file must contain the permissions, and may contain the optional
data.

This file is required, unless you use the --all-permissions option. If you use 
--all-permissions, then you may pass in this file to define the other optional
fields, but the 'permissions' section of the details_file will be ignored.

Permissions (required unless --all-permissions option is used)
----------------------

To set permissions on your application, you need to pass in a JSON file 
containing the permissions you wish to include.

Under the reference/ folders, you'll find complete_permissions.json files.
These files contain the full list of permissions available for their respective
FxOS versions. Use these files as references for your own permissions file.

For example, if I wanted to have an app with only "read" access to "contacts"
for v1.3, my permissions file will only contain this::
  {
    "permissions": {
      "contacts":{ "access": "readonly" },
    }
  }

The "access" options take either "readonly", "readwrite", "readcreate" and
"createonly".

For more information on permissions, please see 
https://developer.mozilla.org/en-US/Apps/Build/App_permissions

System Messages (optional)
-------------------------

Certain permissions require you to direct system messages to a particular page
in your app. For example, if you have "sms" as a permission, then you likely
want your app to listen for "sms-delivery-success", which will tell your app
that the sms was sent successfully.

By default, if you specify a permission that has related system messages,
the app generated will assigned its messages to be received at the
launch_path. If you would like to change where the messages get received,
then you can add a "messages" section to your permissions file and direct
the messages the way you like. Here's an example::

  {
    "permissions": {
      "sms": {}
    },
    "messages": [
      { "sms-delivery-success": "/index.html" }
    ]
  }

For v1.3 builds:
https://mxr.mozilla.org/mozilla-b2g28_v1_3/source/dom/messages/SystemMessagePermissionsChecker.jsm#29

For trunk builds:
https://mxr.mozilla.org/mozilla-central/source/dom/messages/SystemMessagePermissionsChecker.jsm#29 

Datastore Access (optional)
--------------------------

If your app needs access to a datastore, please add it to your permissions
file as either "datastore-owned" or "datastore-access" as needed, like so::

  {
    "permissions": {
      "sms": {}
    },
    "messages": [
      { "sms-delivery-success": "/index.html" }
    ],
    "datastores-owned": {
        "download_store": {
          "access": "readwrite",
          "description": "Stores successful downloads"
        }
    }
  }

Description (optional)
----------------------

You may customize the description of your app. Add a "description" section
to your permissions file with the desired text. Example::
  {
    "permissions": {
      "sms": {}
    },
    "description": "My test application"
  }

By default, we provide the description for your app as "Generated app".
