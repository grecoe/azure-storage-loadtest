##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

import os
from utils.commandline import CmdUtils
import json

class CopyResult:
    def __init__(self, success:bool=False, copy_time:float = 0.0):
        self.success = success
        self.minutes = copy_time

class StorageCopy:

    @staticmethod
    def copy_storage_file(azcopy_path:str, source:str, destination:str) -> CopyResult:
        copied = CopyResult()

        try:
            print("AZ COPY START")
            print("SOURCE:", source)
            print("DESTINATION:", destination)

            output = CmdUtils.get_command_output(
                [
                    azcopy_path, 
                    "copy", 
                    source, 
                    destination
                ], 
            False, 
            False)

            output = output.split(os.linesep)
            print("AZ COPY COMPLETE")
            print(json.dumps(output, indent=4))

            target = [x for x in output if "Total Number of Transfers" in x]
            result = [x for x in output if "Number of Transfers Completed" in x]
            time = [x for x in output if "Elapsed Time (Minutes)" in x]

            expected = StorageCopy._parse_result(target)
            moved = StorageCopy._parse_result(result)
            minutes = StorageCopy._parse_result(time, float)

            if expected != moved:
                print(json.dumps(output, indent=4))

            copied.success = (expected == moved)
            copied.minutes = minutes

        except Exception as ex:
            print("Copy Error: ", str(ex))

        return copied 

    @staticmethod
    def _parse_result(result:str, klass = int) -> int:
        return_val = None
        if len(result):
            result = result[0].split(":")
            if len(result) == 2:
                return_val = klass(result[1].strip())

        return return_val        
