#!/bin/bash

modeldir="/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2"
for dataset in $(ls -d /data/mtmoore/school/CSiML_AI395T/final_project/dataset/test-set*_coco/); do
    # list models trained on the dataset
    for modelpath in $(ls -d ${modeldir}/faster_rcnn_*/); do
        model=$(basename $modelpath)
        modelname=$(basename $model | awk -F'_' 'BEGIN { OFS = "_"}; { print $1, $2, $3, $4, $5, $6, $7 }')   # "faster_rcnn_R_50_FPN_3x" "faster_rcnn_R_101_FPN_3x"; do

        echo "$dataset, $modelname"

        
#        python /data/mtmoore/school/CSiML_AI395T/final_project/src/deer-detector/detectron2_faster_rcnn_eval.py \
#            --model=${modelname} --dataset=${dataset} \
#            --model-dir=${modelpath} \
#            --dataset-dir="/data/mtmoore/school/CSiML_AI395T/final_project/dataset" \
#            --output-dir="${modeldir}/validation/" 2>&1 \
#                | tee ${modeldir}/validation/${model}_$(date +%s).log
    done
done
