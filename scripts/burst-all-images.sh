#!/bin/bash

cutlist="cut.list"
wd=$(pwd)
for cam in "IP8M-H-NW" "IP8M-G-NW" "IP8M-G-SW" "IP8M-H-SW"; do
    cd "$wd"
    cd "${cam}"
    for d in $(find . -mindepth 1 -maxdepth 1 -type d); do
        if [ ! -f ${cutlist} ]; then
            echo "No cutlist for ${cam}/${d}"
            continue
        fi

        seq=0
        for c in $(cat ${cutlist}); do
            mkdir ${cam}/${d}/${seq}
            cutfile=$(echo $c | cut -f 1 -d'|')
            tagfile=$(echo $c | cut -f 2 -d'|')
            starttime=$(echo $c | cut -f 3 -d'|')
            duration=$(echo $c | cut -f 4 -d'|')
            if [ ! -f "${cutfile}" ]; then
                echo "Couldn't find listed cutfile: ${cutfile} for ${cam}/${d}"
                continue
            fi
            ffmpeg -i ${cutfile} -ss "${starttime}" -t "${duration}" ${cam}/${d}/${seq}/image_${tag}_%08d.png
            if [ "$?" -ne 0 ]; then
                echo "Error cutting \"${c}\" in ${cam}/${d}"
                continue
            fi
            let "seq=seq++"
        done
    done
done
