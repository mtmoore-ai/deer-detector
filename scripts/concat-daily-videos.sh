#!/bin/bash
wd=$(pwd)

for d in "2024-05-11" "2024-05-19" "2024-05-27" "2024-06-04" "2024-06-12" "2024-06-20" "2024-06-28" "2024-07-06" "2024-07-14" "2024-07-22" "2024-07-30"; do
    cd ${d}
    g=$(basename $PWD)
    rm ${g}.mp4
    find . -mindepth 2 -name "*.mp4" | sort -n > inputs.txt
    sed -i -e "s|^|file '|" -e "s|$|'|" inputs.txt
    ffmpeg -f concat -safe 0 -i inputs.txt -c copy ${g}.mp4
    if [ "$?" -ne "0" ]; then
        cd ${wd}
        echo "failure generating in ${d}"
        exit 1
    fi
    cd "${wd}"
done
