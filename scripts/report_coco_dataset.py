import argparse
import json
import os
import random
import pprint
import sys
from tqdm import tqdm


SPLIT_NAMES=["train", "val"]

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation-file",  nargs='+', type=str, default="annotations/instances_default.json", help="json formatted annotation")
    args = parser.parse_args()

    all_records = {}
    for annotation_file in args.annotation_file:
        if not os.path.exists( annotation_file ):
            print(f"{annotation_file} doesn't exist, skipping")

        tag=os.path.basename(annotation_file)
        with open(annotation_file) as f:
            all_records[tag] = json.load(f)

    for k,v in all_records.items():
        print(f"split {k}: {len(v['images'])} images, {len(v['annotations'])} annotations")
