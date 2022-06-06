##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

import configparser
import os

class Storage:
    def __init__(self):
        self.subscription = None
        self.account = None
        self.account_key = None
        self.share_name = None
        self.path = None
        self.account_sas = None
        self.connection_str = None
        self.type = None

    def set_connection_string(self):
        self.connection_str = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net".format(
            self.account,
            self.account_key
        )


    @staticmethod
    def load_storage(config_parser:configparser.RawConfigParser, section:str) -> object:
        return_obj = Storage()
        return_obj.subscription = config_parser.get(section, "subscription")
        return_obj.account = config_parser.get(section, "account")
        return_obj.account_key = config_parser.get(section, "key")
        return_obj.share_name = config_parser.get(section, "share")
        return_obj.path = config_parser.get(section, "path")
        return_obj.type = config_parser.get(section, "type")
        sas = config_parser.get(section, "sas")
        if sas:
            return_obj.account_sas = sas
        return_obj.set_connection_string()
        return return_obj

class Configuration:
    def __init__(self, ini_file:str):
        self.ini_file = ini_file
        self.az_copy_location:str = None
        self.source:Storage = None
        self.destination:Storage = None
        self.file_count = -1


        # Get the INI settings
        if not os.path.exists(ini_file):
            raise Exception("Settings file is invalid - {}".format(ini_file))

        config = configparser.RawConfigParser()
        config.read(ini_file)

        self.az_copy_location = config.get("AZCOPY", "azcopy")
        self.file_count = config.get("LOAD", "files", fallback=None)
        if not self.file_count:
            self.file_count = -1
        else:
            self.file_count = int(self.file_count)
            
        self.source = Storage.load_storage(config, "SOURCE")
        self.destination = Storage.load_storage(config, "DESTINATION")
