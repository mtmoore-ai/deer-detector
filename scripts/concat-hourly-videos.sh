#!/bin/bash

OVERWRITE_EXISTING=0

if [ -z "$1" ]; then
    echo "usage: $0 CAMERA_FILE"
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "usage: $0 CAMERA_FILE; $1 isn't accessible"
    exit 1
fi

CAMERA_FILE=$1
wd="$(pwd)"

# read names of cameras one per line which should also be directorties
readarray -t cameras < $CAMERA_FILE

for c in "${cameras[@]}"; do
    echo "Processing camera ${c}: "
 
    # top-level directory of camera videos, children must be date based directories
    for d in $(find ${wd}/${c} -mindepth 1 -maxdepth 1 -type d); do
        curr_date=$(basename $d)
        echo "    date: ${curr_date}"

        # d is the full path, assume for now it's always the first stream at 001/dav/ for hour directories
        for h in $(find ${d}/001/dav -mindepth 1 -maxdepth 1 -type d); do
            curr_hour=$(basename $h)
            echo "        hour: ${curr_hour}"

            if [ "${OVERWRITE_EXISTING}" -gt 0 ]; then
                # remove any generated mp4s
                rm ${d}/${curr_date}_${curr_hour}.mp4 2>/dev/null
            fi

            # find any mp4s in the date directory below current dir
            find ${h} -mindepth 1 -name "*.mp4" | sort -n > inputs.txt

            # append ffmpeg format file 'F'
            sed -i -e "s|^|file '|" -e "s|$|'|" inputs.txt

            # concat whatever smaller videos we found, sorted by file name (numeric)
            # with ffmpeg
            #echo -n "Generating video for ${c}/${curr_date}/${curr_hour} ..."
            if [ -f ${d}/${curr_date}_${curr_hour}.mp4 ]; then
                continue;
            fi
            ffmpeg -f concat -safe 0 -i inputs.txt -c copy ${d}/${curr_date}_${curr_hour}.mp4 >/dev/null 2>&1

            # bail if something failed unexpectedly (ie bad video file)
            if [ "$?" -ne "0" ]; then
                echo "failure generating in ${d}"
                exit 1
            fi
        done
    done
done
rm inputs.txt
