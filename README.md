# Release integration for Servicenow Change Tasks developed by Catalink
# You can package the plugin for adding to Release by following the below steps

# 1. Download the code 
# 2. Extract the code zip file and perform "cd xlr_servicenow-main"
# 3. Package the plugin using the following command  "zip -r ../xlr-catalink-servicenow-1.0.0.jar ."
# 4. Using the upload plugin interface in Release : upload the plugin and restart your Release server
# 5. You will see the task " Find one or many Change Tasks by Parent" under ServiceNow
# 6. Under Connections, You will see a seperate Server connection called CatalinkServicenow : Server for providing Server connection related information.
# 7. The plugin is now ready for use in the Release templates
