# azcopy - Massive Files

[Return to observations](./observations.md)

There comes a need when a customer needs to move in a massive dataset to Azure for storage/processing. This repo folder contains some information and a process of using azcopy to see what kinds of throughput can be acheived. 

Using standard HTTP(s) calls to move data is not sustainable because the process takes far too long. For example, setting up a dowload from Google Docs to a folder which was an Azure File Share for a 101GB file took > 7 hours. 

Moving the same file internal to Azure (storage 1 -> storage 2) can be moved in approximately 3.8 minutes. 

However, this would still require 2 things:
- Original data set exists in Azure (Databox?)
- It still takes approximately 27 days to move 1PB within Azure with the azcopy utility.

<b>Content</b>
- [Source Data](#source---google-docs)
- [Moving Data](#moving-them-around)
    - [SAS Tokens](#sas)
    - [Applications](#applications)
- [Observations File Share](#observations---file-to-file-shares)
    - [Single Files](#single-files)
        - Single large files
    - [Batch - Python](#batch-with-parallel-from-one-machine)
        - Batch large files with python
    - [Pseudo Batch - Cloud Shell](#manual-batch-cloud-shell)
        - Batch large files with Cloudshell
    - [Batch - Cloud Shell](#cloudshell-batch)
        - Move entire directory with 5 - 101 GB files
    - [Datasets](#datasets)
        - Multiple smaller files
- [Observations Blob Storage](#observations---file-to-blob-storage)
- [Observations Blob to Blob](#observations---blob-to-blob-storage)
- [Petabyte Goal](#average-throughputs--to-pb)
    - [Petabyte move error](#massive-move)

# Source - Google Docs

Load files from [google docs](https://wiki.seg.org/wiki/Open_data#Poseidon_3D_seismic.2C_Australia) by creating a file share, mount it to laptop, then change download location to the share. 

# Moving them around

Note that creating a SAS token that works has been a challenge that I've not focused on when it wasn't working. Collect SAS tokens for your storage account(s) using the Azure Portal. 

## Manual
- Use CloudShell azcopy
- Create SAS on account with source file share then build URL:
    - https://[ACCOUNT].file.core.windows.net/[SHARE]/[PATH]/[FILE]?[ACCOUNT_SAS]
- Create a SAS on the desitnation share
    - https://[ACCOUNT].file.core.windows.net/[SHARE]/[PATH]/[FILE]?[ACCOUNT_SAS]
    - You can change file name to make multiple copies
    - You can also NOT provide a name and it will use the name of the source file. 
- Run az copy
    - azcopy cp "SOURCE" "DESTINATION"

## movesingle.py
This is similar to above but you put in the URL to the file and the SAS token into the variables towards the top of the file. 

## SAS

This source has the ability to generate SAS tokens, but they don't seem to be taken in by azcopy. I resorted to generating SAS tokens using the Azure Portal and placing them into the ini file to process. 

- Object neded to move file
- Object and Container needed on source if moving a folder. 

## Applications
- movesingle.py
    - Provide information in this one file to move one file
- movebatch.py
    - Add settings to config.ini for source folder and destination folder
    - Also used in a container to fan out execution

# Observations - File to File Shares
Approaches have varied widely to determine if there was a better way of maximizing throughput from one storage account to another, but relying on the underlying azcopy tool to do so. 

|Name|Method|Files|Errors|Size(GB)|Time(min)|Throughput (GB/MIN)|
|---|---|---|---|---|---|----|
|[Single 1](#single-files)|CloudShell|1|0|15.7|0.75|20.93|
|[Single 2](#single-files)|CloudShell|1|0|101|3.95|25.56|
|[Single 3](#cloudshell-batch)|CloudShell|5|0|505|20.31|24.86|
|Single 4|Docker Local(1)|5|0|505|22.60|22.34|
|[Batch 1](#batch-with-parallel-from-one-machine)|joblib.Parallel|2|0|202|6.64|30.37|
|Batch 2|2 instances python script|2|0|202|6.61|30.55|
|Batch 3|2 instances python script|10|0|1010|40.73|24.79|
|[Batch 4](#4-aci-containers)|4 instances ACI Container|20|0|2020|67|30.14|
|Batch 5|8 instances ACI Container|40|7|3434[*]|149|23.04|
|Batch 6|2 instances ACI Container - 20 files each|40|0|4040|134.38|30.06|
|Batch 7|4 instances ACI Container - 20 files each|80|31|4949[**]|160|30.93|
|Batch 7|4 instances ACI Container - 11 files each|44|0|4444|159.52|27.85|
|[Dataset](#datasets)|Move TNO Data|44573|0|1.15|7.45|0.15|

[*] This included a bad fail as there was actuall 34 not 33 files.
[**] Share sized reached after 49 files

# Observations - File to Blob Storage
Source File Share, destination BLob Storage

NOTE: Not seeing any long tail copies when destination was File Share. 

|Name|Method|Files|Errors|Size(GB)|Time(min)|Throughput (GB/MIN)|
|---|---|---|---|---|---|----|
|Batch 1|4 instances ACI Container - 11 files each|44|0|4444|33.76|131.63|
|Batch 1|4 instances ACI Container - 20 files each|80|0|8080|79.98|101.02[*]|


# Observations - Blob to Blob Storage
Source Blob, destination BLob Storage

NOTE: Not seeing any long tail copies when destination was File Share. 

## Same Region
|Name|Method|Files|Errors|Size(GB)|Time(min)|Throughput (GB/MIN)|
|---|---|---|---|---|---|----|
|Batch 1|4 instances ACI Container - 20 files each|80|0|8080|27.77|290.96|
|Batch 2|4 instances ACI Container - 20 files each|80|0|8080|27.60|292.75|
|Batch 3[*]|3 instances ACI Container - 10 files each|30|0|3030|19.93|152.00|
|Batch 4[*]|4 instances ACI Container - 10 files each|40|0|4040|19.08|200.71|


[*] Two storage accounts same region but different subscripitons. 

## Massive Move
Attempt to move 1000 files per 10 ACI instances equalling approximately 1PB of data. 

- Attempt 1 - Moved approximately 3186 files (~314TB) before failures in move occured. Logs were full of reporting failures but there were so many that the log ran over and couldn't tell. Second run had it fail with an auth header so re-attempting with new SAS tokens, which may be the cause. 
- Attempt 3 - Update SAS tokens but still seeing failure trying to get source blob. 
    - Took URL from ACI and attempt to retrieve, Auth failure (below)
    - Went to portal, got URL of blob (doesn't work along because no public access)
        - Generate new SAS and append to URL, Auth Failure as noted below. 
    - <b>Appears that I broke the account in some way</b>
        - Why is this a problem? Have I hit a limit? 
        - If a limit, would premium have solved the problem? 

```xml
<Error>
<Code>AuthenticationFailed</Code>
<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature. RequestId:eeef7192-001e-0000-57a0-75692e000000 Time:2022-06-01T10:14:25.8670350Z</Message>
<AuthenticationErrorDetail>Signature did not match. String to sign used was segyshare rwdlacupitfx bfqt co 2022-06-01T10:14:15Z 2022-06-01T18:14:15Z https 2021-06-08 </AuthenticationErrorDetail>
</Error>
```

# Cross Region
Source: East US, Destination: West US 2

Performance falls off a cliff in this scenario. A single 101GB file run locally tool 18.57 minutes - 5.44GB/min. Given that, only a single multi container run was done to see if this initial run held true for multiple copies. 

The multi approach was seen to be the fastest in the previous tests, but from observation, this scenario only gets slower with multiple processes (ACI instances), going at it. Looking at the logs while executing it's taking each container 40-60 minutes to move a single file. That would run it down to about (average 50 minutes) to 2.02 GB/min

Given that there was only one test, times were averaged. 

|Name|Method|Files|Errors|Size(GB)|Time(min)|Throughput (GB/MIN)|
|---|---|---|---|---|---|----|
|Batch 1|4 instances ACI Container - 5 files each|20|0|2020|281.77|7.16|




# Average Throughputs / To PB
Taking the averages above, single file vs. batch approaches to move 1PB of data

|Approach|Destination|Average GB/Min|Avg Daily (TB)|Days to PB|
|----|----|----|----|----|
|Singles|File Share - File Share|23.78|33.44|30.61|
|Batch|File Share - File Share|28.96|40.72|25.14|
|Batch|File Share - Blob Storage|130|182.81|5.60|
|Batch|Blob Storage - Blob Storage|290.96|409.16|2.50|
|Batch|Blob Storage - Blob Storage(region2)|7.16|10.08|79.24|


However, this approach seems to be able to handle 

- 1 101 GB file in ~ 3.75 minutes (3:45)
- Since it seems parallel this translates to, a constant running copy process
    - 1440/3.75 = 384 files = 38,784 GB == ~37.87 TB / Day
    - ~37.87 TB / Day -> 1024 / 37.87 -> 1PB == 27 days


## Single Files
- 15.72 GB
- MBPS AVG 5
- TotalBytesTransferred: 16879190016
- Number of File Transfers: 1
- Elapsed Time (Minutes): 0.7007
- Elapsed Time (Minutes): 0.8069
- Elapsed Time (Minutes): 0.6428

100.99GB
- MBPS AVG > 3300 (3000-6500)
- TotalBytesTransferred: 108440556884Elapsed - Number of File Transfers: 1
- Elapsed Time (Minutes): 4.2702
    - 23.65 GB/Min
- Elapsed Time (Minutes): 3.9409
    - 25.63 GB/Min
- Elapsed Time (Minutes): 3.837
    - 26.32 GB/Min

## Datasets 
- TNO Data 1.15 GB
- MBPS AVG: 5
- Elapsed Time (Minutes): 7.447
- Number of File Transfers: 44573
- TotalBytesTransferred: 1241924419


## Batch with parallel from one machine
2 101GB Files - Per File
- {'success': True, 'minutes': 6.5692}
- {'success': True, 'minutes': 6.5358}
    - 30.75 GB/Min
2 101GB Files - Per File
- {'success': True, 'minutes': 7.7696}
- {'success': True, 'minutes': 5.7022}
    - 26 GB / Min
1 101GB Files - Per File
- {'success': True, 'minutes': 3.6376}
    - 27.77 GB/Min

## Manual Batch (Cloud Shell) 
Fire two copies (different 101GB files) from 2 different cloud shell instances.

- Elapsed Time (Minutes): 7.9368
- Elapsed Time (Minutes): 5.2767

## Cloudshell batch
Copy the whole directory of 5 101GB files

- Elapsed Time (Minutes): 20.3089
- Number of File Transfers: 5
- Number of Folder Property Transfers: 1
- TotalBytesTransferred: 542202784420 (504.96 GB)
- 24.86 GB/Min (so very close to those marked above)


<b>Why this won't work for OSDU</b>

When adding files to OSDU, you first have to get an upload URL. This is a Signed (SAS) URL to the location to put the file. 

In this scenario, we are just blindly dropping files into another Azure Storage Account without regard to an actual location. 

So, the reality is, each file needs to be processed individually (after getting the upload url).

## 4 ACI Containers

movetest2
Starting  2022-05-24 14:18:00.628085
Total Run Time:  2022-05-24 15:11:08.897787  =  53.13782796666667
Long tail was a 30 minute copy

movetest3
Starting  2022-05-24 14:20:41.581492
Total Run Time:  2022-05-24 14:55:42.877083  =  35.021592766666664

movetest1
Starting  2022-05-24 14:16:34.349103
Total Run Time:  2022-05-24 15:20:29.758781  =  63.92349413333333
Long tail was a 30 minute copy

movetest4
Starting  2022-05-24 14:22:02.757290
Total Run Time:  2022-05-24 15:25:12.589662  =  63.16387248333333
Long tail was a 30 minute copy

[Return to observations](./observations.md)

