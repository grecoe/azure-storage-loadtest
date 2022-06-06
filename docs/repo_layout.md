# Repository Layout and Getting Started

[Return to main documentation](../README.md#additional-documents)

The repository consists of a Python application to actuate the move of files from one storage account to another. 

The files contained in this file are complete for testing locally, creating local docker images, and for generating Azure Container Instances. 


## Overall Structure

|File/Folder|Description|
|----|----|
|docs/|Folder containing detailed documentation and images for this repository.|
|utils/|Folder containing the main Python code for the application.|
|[azcopy_linux_amd64_10.14.1.tar.gz](#unzip-azcopy)|A local copy of the azcopy utility. Un-tar this file into this directory so that azcopy and NOTICE.txt are direct descendants of the azure-storage-loadtest/ folder.|
|[config.ini](#configini-description)|Initialization file used by the application code, locally or in an ACI, describing the actions to take.|
|[containercreate.sh](#containercreatesh-settings)|Shell script used for generating a new Docker image, pushing it to Docker Hub and creating ACI instances.|
|[containerdelete.sh](#containerdeletesh-settings)|Shell script used for scanning for generated ACI instances using containercreate.sh.<br><br>If a container is found that is stopped, it's log is downloaded locally and the container is deleted.|
|Dockerfile|The Dockerfile for creating the container to run the application code in an ACI instance.|
|environment.yml|YML file for generating the [conda](#local-python-environment) environment locally for testing purposes.|
|executemove.py|The main Python application.|
|requirements.txt|The virtual environment settings to be used in the generated Docker container.|

# Steps

- [Create Azure Storage Accounts](#create-azure-storage-accounts)
- [Locally unzip azcopy](#unzip-azcopy)
- [Create local conda environment](#local-python-environment)
- [Create application configuration](#configini-description)
- [Create ACI Instanes](#containercreatesh-settings)
- [Cleanup ACI Instances](#containerdeletesh-settings)

## Create Azure Storage Accounts

1. Go to the Azure Portal and create 2 Azure Storage accounts in the same region*
2. In each storage account, create a Blob Container
3. In the account destined to be the source account, upload at least one large file.
    - An [open source](https://wiki.seg.org/wiki/Open_data#Poseidon_3D_seismic.2C_Australia) project with large seismic files is useful if you need something very large. The majority of tests were done using a 100.99 GB file.

<sub>*Cross region testing was performed and showed that cross region, due to network transmissions, is not the best approach. However, there is no reason this will NOT work.</sub>

## Unzip azcopy
Run this command in a bash shell:

```bash
tar -xzvf azcopy_linux_amd64_10.14.1.tar.gz --strip-components=1
```

## Local Python Environment
Set up your [Anaconda](../README.md#pre-requisities) environment for local testing:

```bash
conda env create -f environment.yml
conda activate Datamovement
```

Once an environment has been created, update the [config.ini](#configini-description) with information 


## config.ini Description

The config.ini initialization file is used by the application to determine what to do and where to do it. 

This section describes the settings required

|Section|Setting|Purpose|
|----|----|----|
|AZCOPY|azcopy|Location of azcopy tool either running locally or in the ACI container. This should not be modified unless you move azcopy to a different location.|
|LOAD|files|The number of files that each running instance of the application (including each ACI instance) should process.<br><br>- Value is -1, process all the files in the source location.<br>- Value is N where N > 1, process the first file found in the source location N times.<br><br>In the latter case, it does not matter how many files are in the source location.|
|SOURCE|subscription|The subscription ID of the source storage account. Note that source and destination storage accounts may live in different subscriptions.|
||account|The name of the storage account.|
||key|The access key for the storage account (acquired via the Azure Portal)|
||share|Either a file share name or a blob container name.|
||path|The additional path information into the share/container. <b>This has not been tested coming from the root of the container/share, so start with some directory.</b>|
||sas|The account SAS token for the storage container/share. There were some issues in early June when getting the token from the Azure Portal panel for the Storage Account. When that happened, getting the SAS token from the Container panel was succesful.<br><br><b>NOTE:</b> Make sure you give sufficent time on your SAS token so that it does not expire.<br><br>Copy the sas token AFTER the question mark (do not include ?) and paste into this field.|
||type|Either "blob" for a Blob Container or "file" for a File Share.|
|DESTINATION||This is the exact same as SOURCE above, but for the destination storage account.|


## containercreate.sh settings

This file is used in a bash shell to create the Azure Container Instances with the source code in this repository. 

1. Create a resource group for the ACI instances, preferably in the same Azure region as your storage accounts. 
2. Open containercreate.sh and modify
    - AZURE_SUB - This is the subscripition ID of where the Azure Resource Group for the container instances is from 1.. 
    - AZURE_RG - This is the resource group name from 1. 
    - LOAD_IMAGE - This is the name of the public image to be created in your DockerHub account. 
3. On line 24, modify the number of container instances that you want to create. 
4. Execute the script.

## containerdelete.sh settings

This file is used to check the container instances that have been run. When a container is in a stopped state:

- The log from the instance is downloaded into the local folder.
- The ACI instance is deleted from your resource group.

1. Open containerdelete.sh and modify
    - AZURE_SUB - This is the subscripition ID of where the Azure Resource Group for the container instances is from [creating ACI instances](#containercreatesh-settings). 
    - AZURE_RG - This is the resource group name from [creating ACI instances](#containercreatesh-settings). 
    - TEMPLATE - This is the first part of the container name from containercreate.sh on or around line 24. 
2. Run the script.





[Return to main documentation](../README.md#additional-documents)