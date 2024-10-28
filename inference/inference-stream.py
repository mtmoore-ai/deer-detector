import argparse
import sys
import torch
import torchaudio

try:
    from torchaudio.io import StreamReader
except ModuleNotFoundError:
    print("Missing StreamReader, exiting")
    sys.exit(1)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stream-file", type=argparse.FileType('r'),  nargs='+', help="file(s) containing URIs of streams to process")
                        
    args = parser.parse_args()
                        
    streams = {}
    for f in getattr(args, 'stream-file'):
        for stream in f:
            print(f"stream: {stream}")
            streams[stream] = StreamReader(src=stream)
            print(streams[stream].get_src_stream_info())

