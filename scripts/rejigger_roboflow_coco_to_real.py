import argparse
import json
import os
import random
import re
import pprint
import shutil
import sys
from tqdm import tqdm

SPLIT_NAMES=["train", "val"]

if __name__=="__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--annotation-file", type=str, default="annotations/instances_default.json",
                        help="relative path to json formatted annotation within dataset")
    parser.add_argument("--dataset-path", type=str, default="dataset", help="dataset path")
    parser.add_argument("--new-path", type=str, default="new_dataset", help="new directory with processed annotations")
    parser.add_argument("--image-path", type=str, default="dataset", help="path to original images")
    parser.add_argument("--create-split", type=float, default=0.8, help="create a train/val split with train,, default 0.8")

    args = parser.parse_args()

    fname_re = re.compile(r"^(.+)_png.+")

    # make sure annotation file exists
    if not os.path.exists( os.path.join(args.dataset_path, args.annotation_file) ):
       print("provided annotation file doesn't exist")
       sys.exit(1)

    # create directory for new dataset
    try: 
        os.makedirs( args.new_path, exist_ok=False)
        os.makedirs( os.path.join(args.new_path, "annotations"), exist_ok=False)
        for s in SPLIT_NAMES:
            os.makedirs( os.path.join(args.new_path, "images", s), exist_ok=False)

    except FileExistsError:
        print("Location for processed dataset exists, not overwriting. Exiting")
        sys.exit(1)


    with open(os.path.join(args.dataset_path, args.annotation_file)) as f:
        records = json.load(f)
        new_records = {}
        for s in SPLIT_NAMES:
            new_records[s] = { 'images': [], 'annotations': [] }

        imgs = sorted([ img['id'] for img in records['images'] ])
        split_ids = {}
        random.shuffle(imgs)

        start=0
        for i, s in enumerate(SPLIT_NAMES):
            if i == 0:
                split_ids = { k: s for k in imgs[: int( len(imgs)* args.create_split) ] }
                start = max(0, len(split_ids)-1)
                print(f"{s} split, {len(split_ids)} images")
            else:
                other_split = { k: s for k in imgs[start:] }
                split_ids.update(other_split)
                print(f"{s} split, {len(other_split)} images")

        for img in records['images']:
            fname = img['file_name']
            m = fname_re.match(os.path.basename(fname))
            if m is not None:
                real_name = m.group(1) + ".png"
                new_rel_path = os.path.join("images", split_ids[ img['id'] ], real_name)
                img['file_name'] = new_rel_path
                if os.path.exists(os.path.join(args.image_path, real_name)):
                    shutil.copy(os.path.join(args.image_path, real_name),
                                os.path.join(args.new_path, new_rel_path) )
                    new_records[ split_ids[ img['id'] ] ]['images'].append(img)
                else:
                    print(f"Couldn't find source image {os.path.join(args.image_path, real_name)}")
            else:
                print(f"didn't understand {fname}")

        for ann in records['annotations']:
            if ann['image_id'] in split_ids:
                current_split = split_ids[ ann['image_id'] ]
                new_records[ current_split ]['annotations'].append( ann )

        for s in new_records.keys():
            # copy 'other' parts of the json: licenses, info, categories
            for k in records.keys():
                if k not in new_records[s]:
                    new_records[s][k] = records[k]

            new_json_path = os.path.join(args.new_path, "annotations", f"instances_{s}.json")
            with open(new_json_path, mode='w') as nf:
                nf.write(json.dumps(new_records[s]))
                nf.close()

        #train/IP8M-H-SW_2024-10-24_deer_00000121_png.rf.1aa7496f674849ced6941bd347b8ef37.jpg  


