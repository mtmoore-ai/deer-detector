#!/bin/bash

if [ "$#" -lt "2" ]; then
    echo "usage: $0 full-path-to-all-images relative-path-in-zip-to-label-txts <filterin>"
    echo "$# arguments passed instead of 2"
    exit
fi

orig_img_location="$1"
orig_label_dir="$2"
filter_in="$3"

# if the dataset contents are already in the directory
# don't remove labels and images
DATASET_EXTRACTED=1

# cleanup previous contents
if [ "${DATASET_EXTRACTED}" -lt "1" ]; then
    rm -rf data.yaml labels train val 2>/dev/null
fi
rm -rf train val train.txt val.txt 2>/dev/null

# if dataset has images and labels don't unzip 
if [ "${DATASET_EXTRACTED}" -lt "1" ]; then
    unzip -qq ../yolov8_detection.zip
fi

mkdir -p {train,val}/{images,labels}

ls ${orig_label_dir}/ > tmp.labels

if [ -n "${filter_in}" ]; then
    echo "Filtering in paths with \"${filter_in}\""
    grep "${filter_in}" tmp.labels > tmp.filter
    mv tmp.filter tmp.labels
fi

sed -i 's/txt/png/' tmp.labels
shuf tmp.labels > tmp.shuf.labels
all_count=$(cat tmp.shuf.labels | wc -l)
#train_count=$(echo "($all_count * 0.8)/1" | bc)
#val_count=$((all_count - train_count))
train_count=0
val_count=$all_count
echo "${all_count} labels, ${train_count} to train, ${val_count} to val"

head -n ${train_count} tmp.shuf.labels > train.txt
tail -n ${val_count} tmp.shuf.labels > val.txt
rm tmp.labels tmp.shuf.labels

for split in "train" "val"; do
    echo "working on ${split} split, $(cat ${split}.txt | wc -l) entries"
    for f in $(cat ${split}.txt); do
        bname=$(basename $f .png) 
        mv ${orig_label_dir}/${bname}.txt ${split}/labels/
        cp ${orig_img_location}/${bname}.png ${split}/images/
    done
    sed -i "s|^|${split}/images/|" ${split}.txt
done

echo "val: val.txt" >> data.yaml
sed -i "s|path: .|path: $(pwd)|" data.yaml

# if dataset had images now remove them
#if [ "${DATASET_EXTRACTED}" -lt "1" ]; then
#    rm -rf images labels 2>/dev/null
#fi
