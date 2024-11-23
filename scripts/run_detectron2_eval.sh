#!/bin/bash

modeldir="/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2"
#for dataset in "IP8M-H-NW" "IP8M-H-SW" "combined"; do
for dataset in "IP8M-H-SW"; do
    # list models trained on the dataset
    for modelpath in $(ls -d ${modeldir}/faster_rcnn_*${dataset}*1/); do
        model=$(basename $modelpath)
        modelname=$(basename $model | awk -F'_' 'BEGIN { OFS = "_"}; { print $1, $2, $3, $4, $5, $6 }')   # "faster_rcnn_R_50_FPN_3x" "faster_rcnn_R_101_FPN_3x"; do
        
        python /data/mtmoore/school/CSiML_AI395T/final_project/src/deer-detector/detectron2_faster_rcnn_eval.py \
            --model=${modelname} --dataset=${dataset} \
            --model-dir=${modelpath} \
            --dataset-dir="/data/mtmoore/school/CSiML_AI395T/final_project/dataset" \
            --output-dir="${modeldir}/validation/" 2>&1 \
                | tee ${modeldir}/validation/${model}_$(date +%s).log
    done
done
