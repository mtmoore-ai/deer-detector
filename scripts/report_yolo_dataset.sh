#!/bin/bash

DATASET_PATH=$1

if [ -z "${DATASET_PATH}" ]; then
    echo "usage: $0 <YOLO_DATASET_PATH>"
    exit 1
fi

train_count=$(wc -l --total=only ${DATASET_PATH}/train.txt)
val_count=$(wc -l --total=only ${DATASET_PATH}/val.txt)
image_count=$((train_count+val_count))

train_instances=$(wc -l --total=only ${DATASET_PATH}/train/labels/*.txt)
val_instances=$(wc -l --total=only ${DATASET_PATH}/val/labels/*.txt)
instance_count=$((train_instances+val_instances))

echo "#### $DATASET_PATH ####"
echo "Images: ${image_count}"
echo "Instance Count: ${instance_count}"

exit
