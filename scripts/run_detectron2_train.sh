#!/bin/bash

for model in "faster_rcnn_R_50_FPN_3x" "faster_rcnn_R_101_FPN_3x"; do
    #for dataset in "IP8M-H-NW" "IP8M-H-SW" "combined"; do
    for dataset in "IP8M-H-SW"; do
        python /data/mtmoore/school/CSiML_AI395T/final_project/src/deer-detector/detectron2_faster_rcnn_train.py \
            --model=${model} --dataset=${dataset} \
            --dataset-dir="/data/mtmoore/school/CSiML_AI395T/final_project/dataset" \
            --output-dir="/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2" \
                | tee /data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2/${model}_${dataset}_$(date +%s).log
    done
done
