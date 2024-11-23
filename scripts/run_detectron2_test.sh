#!/bin/bash

modeldir="/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2"
for dataset in $(ls -d /data/mtmoore/school/CSiML_AI395T/final_project/dataset/test-set*_coco/); do
    testdatasetname=$(basename $dataset | cut -d'_' -f1 | cut -d'-' -f '3-')

    # list models trained on the dataset
    for modelpath in $(ls -d ${modeldir}/faster_rcnn_*/); do
        model=$(basename $modelpath)
        modelname=$(basename $model | awk -F'_' 'BEGIN { OFS = "_"}; { print $1, $2, $3, $4, $5, $6  }')   # "faster_rcnn_R_50_FPN_3x" "faster_rcnn_R_101_FPN_3x"; do
        traindataset=$(basename $model | awk -F'_' 'BEGIN { OFS = "_"}; { print $7 }')   # "faster_rcnn_R_50_FPN_3x" "faster_rcnn_R_101_FPN_3x"; do

        echo "modelname: $modelname, model: $model"
        echo "traindatasetname: $traindataset"
        echo "testdatasetname: $testdatasetname"
        echo "dataset (test-dataset-dir): $dataset"
        
        python /data/mtmoore/school/CSiML_AI395T/final_project/src/deer-detector/detectron2_faster_rcnn_test.py \
            --model=${modelname} \
            --model-dir=${modelpath} \
            --train-dataset-dir=/data/mtmoore/school/CSiML_AI395T/final_project/dataset/IP8M-H-NW_coco \
            --train-dataset-name=IP8M-H-NW \
            --test-dataset=${testdatasetname} \
            --test-dataset-dir=${dataset} \
            --output-dir="${modeldir}/test/" 2>&1 \
                | tee ${modeldir}/test/${model}_$(date +%s).log
    done
done
