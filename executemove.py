##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

"""
Copy files from one source (File Share/Blob Storage) to another (File Share/Blob Storage)

Information of source and desitnation are located in the config.ini file. 

This can be run locally, as a normal python script OR containerized to run as an ACI to
fan out execution to multiple processes.
"""

from utils.configuration import Configuration, Storage
from utils.storage import StorageUtil
from utils.copyutil import StorageCopy
from datetime import datetime
import uuid

config:Configuration = Configuration("./config.ini")

"""
Current issues with generating an appropriate account SAS, so SAS is collected manually and placed
in the config.ini file before starting. If/when figured out, generate SAS here in the code instead
"""
if not config.source.account_sas:
    StorageUtil.get_account_sas(
        config.source,
        read=True,
        write=True,
        create=True,
        add=True,
        list_content=True
    )


"""
Current issues with generating an appropriate account SAS, so SAS is collected manually and placed
in the config.ini file before starting. If/when figured out, generate SAS here in the code instead
"""
if not config.destination.account_sas:
    StorageUtil.get_account_sas(
        config.destination,
        read=True,
        write=True,
        list_content=True,
        create=True,
        add=True
    )


start = datetime.utcnow()
print("Starting ", start)

try:
    # Get URI's of the files in the source location blob or file
    files = StorageUtil.get_files(config.source)


    current_file = 1

    process_results = []
    if len(files) == 0 :
        print("No files in source location")
    else:

        targets = []
        for file in files:
            location = StorageUtil.get_file_url(config.destination, "{}.test".format(str(uuid.uuid4()))) #file[0])
            print("Captured file", file[0])
            targets.append((file[1], location))

        # Setting config.file_count will just move whatever it finds in the source location 
        # to the destination location. Any other value will copy a single file from the source location
        # the number of times identified by this value. 
        if config.file_count == -1:
            # Just grab what's there. 

            print("Move contents of path")
            total_files = len(targets)
            for target in targets:
                try:
                    print("Record {} of {}".format(current_file, total_files))
                    current_file += 1

                    # Use target as it has source/destination information
                    result = StorageCopy.copy_storage_file(config.az_copy_location, target[0], target[1]) 
                    process_results.append(result)
                    if not result.success:
                        print("FAILED")
                        break
                except Exception as ex:
                    print("Generic Exception")
                    print(type(ex))
        else:

            total_files = config.file_count

            for idx in range(config.file_count):
                print("Record {} of {}".format(current_file, total_files))
                current_file += 1

                # Generate a unique target location for each call since we are using the same file
                location = StorageUtil.get_file_url(config.destination, "{}.test".format(str(uuid.uuid4()))) #file[0])
                try:
                    result = StorageCopy.copy_storage_file(config.az_copy_location, targets[0][0], location) 
                    process_results.append(result)
                    if not result.success:
                        print("FAILED")
                        break
                except Exception as ex:
                    print("Generic Exception")
                    print(type(ex))

except Exception as ex:
    pass

end = datetime.utcnow()
delta = end - start
print("Start Time (UTC):", start)
print("End Time (UTC):", end)
print("Run Time Minutes:",  delta.total_seconds()/60)
print("Total Processed Results:", len(process_results))
failed = [x for x in process_results if x.success == False]
print("Total Failed:", len(failed))
