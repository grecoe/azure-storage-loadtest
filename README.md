# Azure Storage Load Testing
<sub>Dan Grecoe - a Microsoft employee</sub>

This repository is used for testing large file data movement within Azure.

The flow of the test is to use Azure Container Instances to move data from a source Azure Storage account to a destination Azure Storage account. Containers executed in Azure contain running information at the end of the log - within the ACI system. 

# Document Sections

- [Pre-requisities](#pre-requisities)

# Additional Documents

- [Test 1](/docs/massive_files.md)

## Pre-requisities

- An Azure Subscription in which you can create
    - Azure Storage Accounts
    - Azure Container Instances
- [Docker desktop](https://www.docker.com/products/docker-desktop/) to build docker images.
- [Docker Hub account](https://hub.docker.com/) for hosting docker images to seed into the Azure Container Instances.
- Large data files, such as those found in this [open source](https://wiki.seg.org/wiki/Open_data#Poseidon_3D_seismic.2C_Australia) project for the Energy sector. 

Problem Statement

This repository covers initial research into moving large datasets around Azure Storage accounts. 

Data used was collected from an [open source](https://wiki.seg.org/wiki/Open_data#Poseidon_3D_seismic.2C_Australia) project containing large data files from the Energy sector. 

The [azcopy](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) tool was used to perform the data move in various scenarios. 

- On a local command line / Cloud Shell
- Multiple local command lines / Cloud Shell instances
- Packaged into Azure Container Instances

The tests consisted of moving these large files between Azure Storage File Share and Azure Storage Blob Containers. 

|Configuration|Source|Source Azure Region|Destination|Destination Azure Region|
|----|----|----|----|----|
|1|File Share|East US|File Share|East US|
|2|File Share|East US|Blob Storage|East US|
|3|Blob Storage|East US|Blob Storage[*]|East US|
|4|Blob Storage|East US|Blob Storage[**]|East US|
|5|Blob Storage|East US|Blob Storage|West US2|

[*] Same subscripton, same region

[**] Different subscriptons, same region

Observations after performing multiple tests for the above configurations are as follows: 

|Configuration|Average Throughput(GB/Min)|Average Throughput(TB/Day)|Estimated PB Days|
|----|----|----|----|
|1|28.96|40.72[*]|25.14[*]|
|2|130|182.81[*]|5.60[*]|
|> 3|290.96|409.16[*]|2.50[*]|
|4|176|247.5[*]|4.13[*]|
|5|7.16|10.08[*]|79.24[*]|

[*] Calculated from GB/Min numbers

<b>Notes:</b>

- <sub>In-region = Source and Destination storage accounts reside in a single Azure region.</sub>

- <sub>In-region, blob storage source and destination is most performant.</sub>

- <sub>Due to obsesrvations of in-region testing, cross region File Shares were not tested.</sub> 

- <sub>An open dataset in the energy sector - TNO - was also tested. It is comprised of >40,000 small files. While this move showed that throughput dramatically drops off with regards to total volume of bytes moved, it is unknown at this time if data sets will be comprised of large files, small files, or a mixture of the two. Given that, focus was given to 101GB files. Details on a dataset move can be found [here](./massive_files.md/#datasets) </sub>

- <sub>More details on all of the above results can be found in the [massive_files.md](./massive_files.md) document.</sub>


## Summary

Azure Storage, S3 and Azure Stack Storage can be used as sources for the azcopy utility so data must reside in one of these services. 

Testing was performed ONLY using the Azure Storage service. 

[Azure Storage File Shares](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-scale-targets) are limited in size to 5TiB for standard services and can be upgraded to 100TiB for premium deployments. 

[Azure Storage Blob Storage](https://docs.microsoft.com/en-us/azure/storage/common/scalability-targets-standard-account) has a limit of 5PiB which would be the appropriate source and destination service type for large dataset movment within Azure. 

The results show that in-region data movement between two Blob Storage accounts is the most efficient way to move data. Even if given a smaller than 5TiB dataset, this would be the configuration of choice, however, for these smaller sets Azure File Share copy would perform sufficiently fast enough for most scenarios. 

Cross region data movement should be avoided, if possible, as the time to move data increases exponentially. 

