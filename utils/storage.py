##########################################################
# Copyright (c) Microsoft Corporation.
##########################################################

from datetime import datetime, timedelta
import typing
import os
from utils.configuration import Storage
from azure.storage.fileshare import (
    ShareDirectoryClient,
    generate_account_sas, 
    ResourceTypes, 
    AccountSasPermissions
)
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient
)

class StorageUtil:

    @staticmethod
    def get_account_sas(
        storage:Storage, 
        read:bool = False, 
        write:bool = False, 
        list_content:bool = False, 
        create:bool = False, 
        add:bool = False) -> str:

        start = datetime.utcnow()
        storage.account_sas = generate_account_sas(
            account_name= storage.account ,
            account_key= storage.account_key,
            resource_types=ResourceTypes(object=True, container=True),
            permission=AccountSasPermissions(
                read=read, 
                write=write, 
                list=list_content, 
                create=create, 
                delete=True
                ),
            start=start,
            expiry=datetime.utcnow() + timedelta(hours=24),
            protocol="https"
        )

        return storage.account_sas

    @staticmethod
    def get_file_url(storage:Storage, file_name:str) -> str:
        file_url = "https://{}.{}.core.windows.net/{}".format(
            storage.account,
            storage.type, 
            storage.share_name
        )

        file_location = os.path.join(
            file_url, 
            storage.path,
            file_name)

        if "\\" in file_location:
            file_location = file_location.replace("\\", "/")            

        file_location += "?{}".format(storage.account_sas)

        return  file_location

    @staticmethod 
    def get_files(storage:Storage) -> typing.List[typing.Tuple[str, str]]:
        return_uris = []
        
        # TODO - Split attempt to read blobs and files, this doesn't work for blob storage
        # at the moment. 

        file_url = "https://{}.{}.core.windows.net/{}".format(
            storage.account,
            storage.type,
            storage.share_name
        )

        if storage.type.lower() == "file":
            """Get a list of directory children and files in a directory"""
            parent_dir:ShareDirectoryClient = ShareDirectoryClient.from_connection_string(
                conn_str= storage.connection_str, 
                share_name=storage.share_name, 
                directory_path=storage.path)

            content = list(parent_dir.list_directories_and_files())        

            if content:
                file_list = [x for x in content if not x.is_directory] 
                for share_file in file_list:
                
                    file_location = os.path.join(
                        file_url, 
                        storage.path,
                        share_file.name)

                    # Windows path breaks URL pattern
                    if "\\" in file_location:
                        file_location = file_location.replace("\\", "/")            
                    file_location += "?{}".format(storage.account_sas)

                    return_uris.append( (share_file.name, file_location) )
        else:
            parent_container:BlobServiceClient = BlobServiceClient.from_connection_string(
                conn_str=storage.connection_str
            )

            container:ContainerClient = parent_container.get_container_client(storage.share_name)
            content = list(container.list_blobs())

            for blob in content:
                path = os.path.split(blob.name)
                if path[0].lower() == storage.path.lower():
                    file_location = os.path.join(
                        file_url, 
                        blob.name)

                    # Windows path breaks URL pattern
                    if "\\" in file_location:
                        file_location = file_location.replace("\\", "/")            
                    file_location += "?{}".format(storage.account_sas)

                    return_uris.append( (path[1], file_location) )

        return return_uris