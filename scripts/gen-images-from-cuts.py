#!/usr/bin/env python

import argparse
import datetime
import ffmpeg
import glob
from os import path 
import re
import string
import sys
from tqdm import tqdm

outputdir = "/data/mtmoore/school/CSiML_AI395T/videos/cuts/test-set-all-images"
res = {
       'file'     : re.compile(r"^(?P<file>[\S]+\.mp4)$"),
       'cut'      : re.compile(r'^(?P<label>\w+)\s+(?P<cut1>[\d:]+)\s*(?P<cut2>[\d:]+)?\s*(?P<note>.+)*?$')
      }
videocache   = {}
video_params = { 'codec_name': 'h264',
                 'height': 2160,
                 'width': 3840,
                 'r_frame_rate': '10/1',
               }

def fixup_cut_time( time:str ) -> str:

    if time is None:
        return None

    nums = time.split(':')

    for n in nums:
        try:
            v = int(n)
        except:
            print(f"couldn't convert {n} to a number")
            return None

    if len(nums) == 2:
        return f"00:{time}"
    elif len(nums) == 3:
        return time
    else:
        print(f"unexpected number of entries in time, seems invalid: {time}")
        return None

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

def generate_ffmpeg_cut(file: str, params: dict) -> None:

    cduration = 2
    cut1, cut2 = None, None
    duration = None
    starttime = None

    # won't generate without at least one cut time
    if 'cut1' not in params:
        return

    cut1 = datetime.datetime.strptime(params['cut1'], '%H:%M:%S')    

    if 'cut2' in params and params['cut2'] is not None:
        cut2 = datetime.datetime.strptime(params['cut2'], "%H:%M:%S")    
        cduration = (cut2 - cut1).total_seconds()

    starttime = cut1.strftime("%H:%M:%S")
    duration = f"{int(cduration)}"

    if cduration <= 0:
        print(f"**** WARN: confusing duration: {duration}, from cut1: {params['cut1']}, cut2: {params['cut2']}", file=sys.stderr)
        return
    checks = True
    if file not in videocache:
        try: 
            videocache[ file ] = ffmpeg.probe(file)
        except ffmpeg.Error as e:
            #print('ffprobe failure/stdout:', e.stdout.decode('utf8'), file=sys.stderr)
            print('ffprobe failure/stderr:', e.stderr.decode('utf8'), file=sys.stderr)
            return

        
        if 'streams' not in videocache[ file ]:
            print(f"**** ERROR: no streams found in file {file}", file=sys.stderr)
        for s in videocache[ file ]['streams']:
            if s['codec_type'] == "video":
                for k, v in video_params.items():
                    if s[k] != v:
                        print(f"**** WARN: video stream param {k}: expected={v}, found={s[k]}, not creating images", file=sys.stderr)
                        checks = False
    if not checks:
        print(f"**** ERROR: video checks didn't pass, skipping image creation to avoid unexpected data", file=sys.stderr)
        return

    # get the current image count of camera_date_label_X.png format so we don't overwrite
    output_prefix = path.join(outputdir, f"{params['camera']}_{params['date']}_{params['label']}_")
    next_start= count_existing_images( output_prefix )
    output_string = f"{output_prefix}%08d.png"

    try:
        out = ffmpeg.input( file, ss=starttime, t = duration) \
              .output(output_string, r=1, start_number=next_start ) \
              .run(quiet=True)
        after_burst = count_existing_images( output_prefix )
        for i in range(next_start, after_burst):
            if not args.no_print:
                print(f"{params['camera']}_{params['date']}_{params['label']}_{i:08d}.png {params['camera']} {params['date']} {params['label']} \"{params['note']}\"")
    except ffmpeg.Error as e:
        print(f"error when trying to burst {file} with {starttime=}, {duration=}")
        #print('ffprobe failure/stdout:', e.stdout.decode('utf8'), file=sys.stderr)
        print('ffprobe failure/stderr:', e.stderr.decode('utf8'), file=sys.stderr)
        return
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cut-file",  type=argparse.FileType('r'), nargs='+', help="the cut files to generate ffmpeg commands for (camera_date_file.list)")
    parser.add_argument("--dryrun", action='store_true', help="report cuts found in input file, don't generate images")
    parser.add_argument("--no-print", action='store_true', help="don't report cuts")
   
    args = parser.parse_args()
    img_count_estimate = 0

    if not path.isdir(outputdir):
        print(f"specified output directory, {outputdir}, doesn't exist. Exiting")
        sys.exit(1)

    currfile = None
    for f in getattr(args, 'cut-file'):
        lines = f.readlines()
        for line in tqdm(lines, desc=f"Bursting from cuts in {f.name}") if not args.dryrun else lines:
        #for line in f:
            if line == "\n":
                continue

            nomatch = True
            for k,v in res.items():
                m = v.match(line)
                if m is not None:
                    if k == "file":
                        currfile = m["file"]
                        videodir = path.dirname(currfile)
                        filename = path.basename(currfile)
                        #print(f"{videodir=}, {filename=}")
                        camera, date = videodir.split('/')
                    if k == "cut":
                        cut_params = m.groupdict()
                        cut_params['camera'] = camera
                        cut_params['date'] = date
                        cut_params['cut1'] = fixup_cut_time( cut_params['cut1'] )
                        if cut_params['cut1'] is None:
                            print("couldn't parse the first cut time and it's None, exiting")
                            sys.exit(1)
                        cut_params['cut2'] = fixup_cut_time( cut_params['cut2'] )
                        cut2s = cut_params['cut2'] if cut_params['cut2'] is not None else "None"

                        ## print a report for the dryrun 
                        if args.dryrun:
                            cut1 = datetime.datetime.strptime(cut_params['cut1'], '%H:%M:%S')
                            cduration = 2
                            if 'cut2' in cut_params and cut_params['cut2'] is not None:
                                cut2 = datetime.datetime.strptime(cut_params['cut2'], "%H:%M:%S")    
                                cduration = (cut2 - cut1).total_seconds()
                            
                            img_count_estimate = img_count_estimate + cduration
                            print(f"{cut_params['camera']:<10s} {cut_params['label']:<12s} " +
                                  f"{currfile:<30s} " +
                                  f"{cut_params['cut1']:<8s} " +
                                  f"{cut2s:<8s} " + 
                                  f"{cduration} " +
                                  f"{cut_params['note']}" )
                        else:
                           generate_ffmpeg_cut(file=currfile, params=cut_params)
                    nomatch = False
            if nomatch:
                print(f"*** WARN: skipped cut-file line: \"{line}\"", file=sys.stderr)

    if args.dryrun:
        print(f"estimated image count: {img_count_estimate}")
