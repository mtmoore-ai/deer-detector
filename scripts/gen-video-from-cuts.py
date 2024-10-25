#!/usr/bin/env python

import argparse
import datetime
import ffmpeg
from os import path 
import pprint
import re

ffmpeg_params = { 'fps_to_image': 2 }
outputdir = "/data/mtmoore/school/CSiML_AI395T/videos/cuts"
res = {
       'file'     : re.compile(r"^(?P<file>\S+)\.mp4$"),
       'cut'      : re.compile(r'^(?P<label>\w+)\s+(?P<cut1>[\d:]+)\s*?(?P<cut2>[\d:]+)?\s*(?P<note>.+)?$')
      }
videocache = {}

video_expected_params = { 'codec_name': 'hevc',
                          'height': 2160,
                          'width': 3840,
                          'avg_frame_rate': '10/1',
                        }
                          

def generate_ffmpeg_cut(file: str, videodir: str, params: dict):

    cduration = 0
    cut1, cut2 = None, None
    duration = None
    starttime = None

    # won't generate without at least one cut time
    if 'cut1' not in params:
        return

    cut1 = datetime.datetime.strptime(params['cut1'], '%M:%S')    

    if 'cut2' in params:
        cut2 = datetime.datetime.strptime(params['cut1'], "%M:%S")    
        cduration = (cut2 - cut1).total_seconds()
    else:
        c_duration = timedelta(seconds=2).total_seconds()

    starttime = cut1.strftime("%M:%S")
    duration = f"{cduration}"

    # video file names start with hour field
    hour = file.split('.')[0]
    fullpath = path.join(videodir, hour, file + ".mp4" )

    if fullpath not in videocache:
        print(f"{file=}, {videodir=}, {starttime=}, {duration=}")
        print(fullpath)
        videocache[ fullpath ] = ffmpeg.probe(fullpath)
        if 'streams' not in videocache[ fullpath ]:
            print(f"**** ERROR: no streams found in file {fullpath}")
        for s in videocache[ fullpath ]['streams']:
            if s['codec_type'] == "video":
                for k, v in video_expected_params.items():
                    if s[k] != v:
                        print(f"**** ERROR: video stream param {k}: expected={v}, found={s[k]}")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cut-file", type=str, nargs='+', help="the cut files to generate ffmpeg commands for (camera_date_file.list)")
   
    args = parser.parse_args()
    print(args)

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
                            generate_ffmpeg_cut(file=currfile, videodir=videodir, params=m.groupdict())
                        nomatch = False
                if nomatch:
                    print(f"*** WARN: skipped line in {f}: \"{line}\"")
