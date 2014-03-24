==================
FxOS App Generator
==================

A tool to generate an FxOS application with any given permissions

Requirements
============

Your phone must have Marionette installed on it and running on port 2828

FIXME: more detail needed

Setup and Usage
===============

TBA

Declaring Permissions
---------------------

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

System Messages
---------------

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
