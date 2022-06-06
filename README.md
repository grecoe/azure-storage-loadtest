# Azure Storage Load Testing
<sub>Dan Grecoe - a Microsoft employee</sub>

As an Azure customer, you want to get your data into the Azure platform for any number of reasons. Storae capacity, utilize a different service, the list goes on. 

Some customers start with data collection in Azure and others will start with data in their own data centers. 

This project assumes that data already exists in Azure, however that will not neccesarily be the case for all users. There are options, however, in moving data to Azure. 

1. [Databox](https://azure.microsoft.com/en-us/services/databox/) in which the customer requests this service and generates an Azure Storage account to load.
    - Customer has an Azure Subscrpition and a storage account.
    - Customer recieves the hardware and loads the data.
    - Customer returns the hardware and the data is loaded into the storage account. 
2. Manually uploading using any of the various API's or tools such as azcopy. 

This repository currently does not cover either of the above scenarios but instead, focuses on moving large amounts of data around the Azure service itself. Why, you might as? 

Consider the OSDU platform as it exists today. You use REST API's to request an upload URL for a new file, upload the file to that URL, add in metadata and now your OSDU platform can work with that file (making it searchable/etc.)

In an OSDU deployment in Azure, the Upload URL is actually a signed url to an Azure Blob Storage account. This makes moving data relatively easy with the use of the [azcopy](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) tool without a lot of additional overhead.  

This repository can be used to perform just such a test to validate parallelization of data movement using [azcopy](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) alongside other Azure services. 


# Document Sections

- [Pre-requisities](#pre-requisities)

# Additional Documents

- [Repository description and getting started](/docs/repo_layout.md)
- [Data Movement Test Layout](/docs/data_movement.md)
- [Observations](./docs/observations.md)
- [Learnings](./docs/knowledge.md)

## Pre-requisities

- An Azure Subscription in which you can create
    - Azure Storage Accounts
    - Azure Container Instances
- [Docker desktop](https://www.docker.com/products/docker-desktop/) to build docker images.
- [Docker Hub account](https://hub.docker.com/) for hosting docker images to seed into the Azure Container Instances.
- Large data files, such as those found in this [open source](https://wiki.seg.org/wiki/Open_data#Poseidon_3D_seismic.2C_Australia) project for the Energy sector. 
- [Anaconda](https://www.anaconda.com/python-r-distribution?utm_campaign=python&utm_medium=online-advertising&utm_source=google&utm_content=anaconda-download&gclid=CjwKCAjwy_aUBhACEiwA2IHHQE2fomeTLs5b4APwKO5zZ3rCmvQbRE6fE9uagS6e2BX5aDcBDHJ2sBoCqZkQAvD_BwE) installed on your machine to test the application before generating Docker images.


