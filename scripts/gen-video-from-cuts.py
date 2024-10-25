#!/usr/bin/env python

import argparse
import datetime
import ffmpeg
import glob
from os import path 
import re
import sys

ffmpeg_params = { 'fps_to_image': 2 }
outputdir = "/data/mtmoore/school/CSiML_AI395T/videos/cuts"
res = {
       'file'     : re.compile(r"^(?P<file>\S+)\.mp4$"),
       'cut'      : re.compile(r'^(?P<label>\w+)\s+(?P<cut1>[\d:]+)\s*(?P<cut2>[\d:]+)?\s*?(?P<note>.+)*?$')
      }
videocache   = {}
video_params = { 'codec_name': 'hevc',
                 'height': 2160,
                 'width': 3840,
                 'avg_frame_rate': '10/1',
               }
                          

def count_existing_images(path_prefix: str ) -> int:
    max_seen = 0

    # assumes format of file name camera_date_label_num.png
    for f in glob.glob( path_prefix + "*" ):
        fname = path.basename(f)
        camera, date, label, number_ext = fname.split("_")
        number, ext = number_ext.split(".")
        if int(number) > max_seen:
            max_seen = int(number)
    return max_seen + 1

def generate_ffmpeg_cut(file: str, videodir: str, params: dict) -> None:

    cduration = 0
    cut1, cut2 = None, None
    duration = None
    starttime = None

    # won't generate without at least one cut time
    if 'cut1' not in params:
        return

    cut1 = datetime.datetime.strptime(params['cut1'], '%M:%S')    

    if 'cut2' in params and params['cut2'] is not None:
        cut2 = datetime.datetime.strptime(params['cut2'], "%M:%S")    
        cduration = (cut2 - cut1).total_seconds()
    else:
        c_duration = datetime.timedelta(seconds=2).total_seconds()

    starttime = cut1.strftime("%M:%S")
    duration = f"{int(cduration)}"

    # video file names start with hour field
    hour = file.split('.')[0]
    fullpath = path.join(videodir, hour, file + ".mp4" )
    checks = True
    if fullpath not in videocache:
        videocache[ fullpath ] = ffmpeg.probe(fullpath)
        if 'streams' not in videocache[ fullpath ]:
            print(f"**** ERROR: no streams found in file {fullpath}")
        for s in videocache[ fullpath ]['streams']:
            if s['codec_type'] == "video":
                for k, v in video_params.items():
                    if s[k] != v:
                        print(f"**** WARN: video stream param {k}: expected={v}, found={s[k]}, not creating images")
                        checks = False
    #if not checks:
    #    print(f"**** ERROR: video checks didn't pass, skipping image creation to avoid unexpected data")
    #    return

    # get the current image count of camera_date_label_X.png format so we don't overwrite
    output_prefix = path.join(outputdir, f"{params['camera']}_{params['date']}_{params['label']}_")
    next_start= count_existing_images( output_prefix )
    output_string = f"{output_prefix}%08d.png"

    out = ffmpeg.input( fullpath, ss=starttime, t = duration) \
          .output(output_string, r=1, start_number=next_start ) \
          .run(quiet=True)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cut-file", type=str, nargs='+', help="the cut files to generate ffmpeg commands for (camera_date_file.list)")
   
    args = parser.parse_args()

    currfile = None
    for f in getattr(args, 'cut-file'):

        camera, date, _ = f.split('_')
        videodir=f"{camera}/{date}/001/dav/"

        with open(f) as cutlist:
            for line in cutlist:
                nomatch = True
                for k,v in res.items():
                    m = v.match(line)
                    if m is not None:
                        if k == "file":
                            currfile = m["file"]
                        if k == "cut":
                            cut_params = m.groupdict()
                            cut_params['camera'] = camera
                            cut_params['date'] = date
                            generate_ffmpeg_cut(file=currfile, videodir=videodir, params=cut_params)
                        nomatch = False
                if nomatch:
                    print(f"*** WARN: skipped cut-file line in {f}: \"{line}\"")
