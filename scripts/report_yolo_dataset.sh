#!/bin/bash

DATASET_PATH=$1

if [ -z "${DATASET_PATH}" ]; then
    echo "usage: $0 <YOLO_DATASET_PATH>"
    exit 1
fi

train_count=$(wc -l --total=only ${DATASET_PATH}/train.txt 2>/dev/null)
val_count=$(wc -l --total=only ${DATASET_PATH}/val.txt 2>/dev/null)
image_count=$((train_count+val_count))

train_instances=$(wc -l --total=only ${DATASET_PATH}/train/labels/*.txt 2>/dev/null)
val_instances=$(wc -l --total=only ${DATASET_PATH}/val/labels/*.txt 2>/dev/null)
instance_count=$((train_instances+val_instances))

echo "#### $DATASET_PATH ####"
echo "Train Images: ${train_count}, Train Instances: ${train_instances}"
echo "Val Images: ${val_count}, Val Instances: ${val_instances}"
echo "All Images: ${image_count}, All Instances: ${instance_count}"
exit
