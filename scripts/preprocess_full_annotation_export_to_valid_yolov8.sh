#!/bin/bash

orig_img_location="/data/mtmoore/school/CSiML_AI395T/final_project/dataset/build/validation/deer/"
orig_label_dir="labels/train/cuts/deer"

# cleanup previous contents
rm -rf labels train val 2>/dev/null
rm data.yaml train.txt val.txt

unzip -qq yolov8_detection.zip

mkdir -p {train,val}/{images,labels}

ls ${orig_label_dir}/ > tmp.labels
sed -i 's/txt/png/' tmp.labels
shuf tmp.labels > tmp.shuf.labels
all_count=$(cat tmp.shuf.labels | wc -l)
train_count=$(echo "($all_count * 0.8)/1" | bc)
val_count=$((all_count - train_count))

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
sed -i "s|path: .
