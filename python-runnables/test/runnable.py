# This file is the actual code for the Python runnable test
from dataiku.runnables import Runnable
import dataiku
from dataiku.runnables import utils


client = dataiku.api_client()

# Get the identity of the end DSS user
user_client = dataiku.api_client()
user_auth_info = user_client.get_auth_info()
# Automatically create a privileged API key and obtain a privileged API client
# that has administrator privileges.
admin_client = utils.get_admin_dss_client("creation1", user_auth_info)

admin_client.list_connections().items()

class MyRunnable(Runnable):
    """The base interface for a Python runnable"""

    def __init__(self, project_key, config, plugin_config):
        """
        :param project_key: the project in which the runnable executes
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        self.project_key = project_key
        self.config = config
        self.plugin_config = plugin_config
        
    def get_progress_target(self):
        """
        If the runnable will return some progress info, have this function return a tuple of 
        (target, unit) where unit is one of: SIZE, FILES, RECORDS, NONE
        """
        return None

    def run(self, progress_callback):
        var1 = self.config['parameter1']
        
        print(var1)
        """
        Do stuff here. Can return a string or raise an exception.
        The progress_callback is a function expecting 1 value: current progress
        """
        #raise Exception("unimplemented")
        return var1
        