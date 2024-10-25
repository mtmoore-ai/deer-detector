import argparse
import ffmpeg
import json
import pprint
import sys


video_params = { 'codec_name': 'hevc',
                 'height': 2160,
                 'width': 3840,
                 'r_frame_rate': '10/1',
               }

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input-file",  type=argparse.FileType('r'),  help="the cut files to generate ffmpeg commands for (camera_date_file.list)")
    parser.add_argument("--report", action='store_true', help="report video params found")
    parser.add_argument("--verbose", action='store_true', help="report video params found")

    args = parser.parse_args()

    
    for mp4 in getattr(args, 'input-file'):
        mp4 = mp4.strip()
        stream_params = None
        try:
            mp4_vstreams = ffmpeg.probe(mp4, select_streams='v:0', count_packets=None)
            stream_params = mp4_vstreams['streams'][0]
        except ffmpeg.Error as e:
            #print('ffprobe failure/stdout:', e.stdout.decode('utf8'), file=sys.stderr)
            #print('ffprobe failure/stderr:', e.stderr.decode('utf8'), file=sys.stderr)
            print(f"error: malformed file: {mp4}", file=sys.stderr)
            stream_params = None

        if stream_params is None:
            continue

        if args.verbose:
            pprint.pprint(f"{stream_params=}")
       
        any_mismatch = False
        for k,v in video_params.items():
            # may need to massage reported values to compare
            v_c = stream_params[k]
            if v_c != v:
                any_mismatch = True
                if args.report:
                    print(f"mismatch: {mp4}: {k} mismatch, is {v_c}, should be {v}")
        if not any_mismatch:
            print(mp4)
