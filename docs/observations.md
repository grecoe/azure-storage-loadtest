# Observations

[Return to main documentation](../README.md)

This page either contains or links to observation documentation. 

While maybe not terribly useful for the general reader, the raw notes taken duing the testing can be found [here](./massive_files.md). A transient problem found when moving PB sized data can be found [here](./massive_move.md).

The tests performed covered a wide range of configuratons

- Azure File Share to Azure File Share 
- Azure File Share to Azure Blob Storage
- Azure Blob Storage to Azure Blob Storage
    - Source and destination storage accounts in two Azure Subscriptions, but in the same Azure Region.
    - Source and destination storage accounts in two Azure Regions

Aside from the configuration of the services, the data moved was 

- A 44k file set comprised of files <10MB in size, with a majority of the files ~10KB in size. 
- A combination of 16GB and 101GB file sizes. 
- Bulk (PB scale) loading using only 101GB files. 

> <b>Note:</b> Azure File Shares performed quite poorly in comparison to Azure Blob Storage. Further, even in premium mode, an Azure File Share can only be 100TiB in size, therefore observations exclude results found with Azure File Share as a source or destination storage solution. 

# Testing Results

- [Large Dataset Testing](#large-dataset-testing)
- [Terrabyte Testing](#terrabyte-testing)
- [Petabyte Testing](#petabyte-testing)

## Large Dataset Testing

With other testing, tests determine the volume of data in bytes that is transferred, however in the large dataset testing an open dataset in the Energy Sector - TNO - was used. 

It is comprised of 44573 files and instead of moving files individually, azcopy was simply aimed at the blob storage container with the dataset and set loose to move the whole thing at once.

The dataset is comprised mostly of 10KB files with only a smattering of files >1MB and <10MB.

This exhibited how many smaller files could be moved using the tool. 

- TNO Data 1.15 GB
- Elapsed Time (Minutes): 7.447
- Number of File Transfers: 44573
- Files Per Minute: 5,985

## Terrabyte Testing

This testing initially started out using a combination of 16GB and 101GB files, however, to keep tests consistent only results using the 101GB files were captured. 

These initial tests used 4 ACI instances and each instance moved between 10-20 files each, this was a relatively small test of 4-8TB of data.

|Configuration|Source|Source Azure Region|Destination|Destination Azure Region|
|----|----|----|----|----|
|1|Blob Storage|East US|Blob Storage[*]|East US|
|2|Blob Storage|East US|Blob Storage[**]|East US|
|3|Blob Storage|East US|Blob Storage|West US2|

[*] Same subscripton, same region

[**] Different subscriptons, same region

Observations after performing multiple tests for the above configurations are as follows: 

|Configuration|Average Throughput(GB/Min)|Average Throughput(TB/Day)|Estimated PB Days|
|----|----|----|----|
|> 1|290.96|409.16[*]|2.50[*]|
|2|176|247.5[*]|4.13[*]|
|3|7.16|10.08[*]|79.24[*]|

[*] Calculated from GB/Min numbers


It's important to note that for tests 1 and 2 these numbers do not reflect any of the Azure Storage documentation. In fact, when moving to [petabayte](#petabyte-testing) these numbers were not seen, so it's unclear how these numbers could possibly acheived. 

However, the throughput numbers were simple calculations of number of GB sent during a test run and the number of minutes it took for the test to run. It's possible that we were able to obtain these results because the total load of the data was relatively small. 

Notes from these tests can be found [here](./massive_files.md).


## Petabyte Testing

This testing was a bit more comprehensive in volume of data. There were two tests run with the following configuration.

- Data File: 100.99GB
- ACI Count: 10
- Files per instance: 1000
- Total Test Size: 986TB

The first test was run using standard storage accounts and the second was run using premium storage accounts. 

These tests were run to completion so gueswork calculations were needed.

|Type|GB/Min|Total Time: Hours|
|---|---|---|
|Standard|69.27|24.29|
|Premium|31.73|53.04|

The throughput on these tests were more in line with the advertised througput rates from the storage service itself. 

One more test was run, using only standard storage, but a fewer number of container instances.
- Data File: 100.99GB
- ACI Count: 4
- Files per instance: 2500
- Total Test Size: 986TB

|Type|GB/Min|Total Time: Hours|
|---|---|---|
|Standard|69.27|24.29|


[Return to main documentation](../README.md)
