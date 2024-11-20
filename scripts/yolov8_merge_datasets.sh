#!/bin/bash

src1=$1
src2=$2
dest=$3

if [[ -z "${src1}" ]] || [[ -z "${src2}" ]] || [[ -z "${dest}" ]]; then
    echo "usage $0 <src1> <src2> <dest>"
    exit 1
fi

if [[ ! -d "${src1}" ]] || [[ ! -d "${src2}" ]]; then
    echo "source directory ${src1} and source directory ${src2} must exist"
    exit 1
fi

if [ -d "${dest}" ]; then
    echo "destination directory already exists, remove first"
    exit 1
fi

mkdir -p ${dest}/{train,val}/{images,labels}

for d in "$src1" "$src2"; do
    for s in "train" "val"; do
        for i in "images" "labels"; do
            cp -a ${d}/${s}/${i}/* ${dest}/${s}/${i}/
        done
        cat ${d}/${s}.txt >> ${dest}/${s}.txt
    done
done
cp ${src1}/data.yaml ${dest}

exit
