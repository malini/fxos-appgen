==================
FxOS App Generator
==================

A tool to generate an FxOS application with any given permissions

Requirements
============

TBA

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
for v1.3, my permissions file will only contain this: 

{
  "permissions": {
    "alarms": {}
   }
}

That's all that is needed
