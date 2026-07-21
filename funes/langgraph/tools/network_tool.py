import datetime
import json
from funes.Storage import storage_manager
from funes.utils.utils import remove_json_strings

from funes.langgraph.tools.base_tool import BaseTool


class NetworkTool(BaseTool):
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    @property
    def name(self):
        return "network_tool"

    def run(self, query):

        result = self.storage_manager.get_network_data()
        return result
