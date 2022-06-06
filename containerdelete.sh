#!/bin/bash

##############################################################
# Search for containers created with movecontainers.sh and
# check if they have completed. If they have
#   1. Download the log locally
#   2. Delete teh ACI instance
##############################################################

# Your sub to deploy containers
AZURE_SUB="YOUR_AZURE_SUB_ID"
# Your RG for container deployments
AZURE_RG="containermove"

# Make this pattern the same as containers created with movecontainers.sh so you can 
# easily figure out if a container in the batch is still running.
TEMPLATE="movetest"

az account set -s $AZURE_SUB

CONTAINERS=$(az resource list -g $AZURE_RG --resource-type Microsoft.ContainerInstance/containerGroups --query [].name -otsv)

echo "Scanning ${#CONTAINERS[@]} in group $AZURE_RG"
count=1
for cont in $CONTAINERS
do

    state=$(az container show -n $cont -g $AZURE_RG --query instanceView.state -otsv)
    
    if [[ $state = "Running" ]]; then
        echo "$count $cont is running"
    else
        echo "$count $cont is stopped"
        if [[ $cont == *"$TEMPLATE"* ]]; then
            echo "$cont matches the format $TEMPLATE and will be deleted"
            log=$(az container logs -n $cont -g $AZURE_RG)
            log_name="$cont.log"
            echo "$log" > $log_name 

            az container delete -n $cont -g $AZURE_RG -y > /dev/null
        fi
    fi

    count=$((count + 1))
done

