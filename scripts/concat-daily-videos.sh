#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 camera_dir"
    exit 1
fi

# top-level directory of camera videos, children must be date based directories
wd="$(pwd)/$1"

for d in $(ls -d ${wd}*); do
    cd ${d}

    # get the date from the directory we're in
    g=$(basename $PWD)
    # remove any top-level mp4s (in case we already had generated something)
    rm ${g}.mp4

    # find any mp4s in the date directory below current dir
    find . -mindepth 2 -name "*.mp4" | sort -n > inputs.txt

    # append ffmpeg format file 'F'
    sed -i -e "s|^|file '|" -e "s|$|'|" inputs.txt

    # concat whatever smaller videos we found, sorted by file name (numeric)
    # with ffmpeg
    ffmpeg -f concat -safe 0 -i inputs.txt -c copy ${g}.mp4

    # bail if something failed unexpectedly (ie bad video file)
    if [ "$?" -ne "0" ]; then
        cd ${wd}
        echo "failure generating in ${d}"
        exit 1
    fi

    # go back to parent
    cd "${wd}"
done
