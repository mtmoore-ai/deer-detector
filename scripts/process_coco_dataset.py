import argparse
import json
import os
import random
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
    parser.add_argument("--start-id", type=int, default=0, help="id to start keeping, default=0")
    parser.add_argument("--end-id", type=int, default=None, help="last id to include, default=-1, end of ids")
    parser.add_argument("--filter", type=str, default=None, help="string to include/exclude with image name with filter-op flag")
    parser.add_argument("--filter-op", type=str, default=None, choices=['include', 'exclude', None], 
                        help="string to include/exclude with filter-op flag happens after start/end id contraint")
    parser.add_argument("--new-path", type=str, default="new_dataset", help="new directory with processed annotations")
    parser.add_argument("--print-file-names", action="store_true", help="print image file names for valid images")
    parser.add_argument("--create-split", type=float, default=0.8, help="create a train/val split with train,, default 0.8")
    parser.add_argument("--no_reset_image_paths", action="store_true", help="reset image paths, default is yes")
    parser.add_argument("--move_images", action="store_true", help="Move image files to new location, default to copy")
    args = parser.parse_args()

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
       
    # ugly way to get the name of the original split source which is probably just default
    orig_split_name = os.path.basename(args.annotation_file).split("_")[1].split(".")[0]
    # read in current annotation file
    with open(os.path.join(args.dataset_path, args.annotation_file)) as f:
        records = json.load(f)

        # get list of image id's 
        imgs = sorted([ img['id'] for img in records['images'] ])
        
        # get list of image id's we want to keep
        keep_images = imgs[args.start_id:args.end_id]

        # here is where we can filter reasonably 
        if args.filter is not None and args.filter_op is not None:
            filter_images = []
            for img in records['images']:
                # honor the list of image ids based on range
                if img['id'] not in keep_images:
                    continue

                if args.filter_op == "include":
                    if args.filter in img['file_name']:
                        filter_images.append(img['id'])
                if args.filter_op == "exclude":
                    if args.filter not in img['file_name']:
                        filter_images.append(img['id'])
            keep_images = filter_images

        # create dict to hold id -> split name mapping
        split_ids = {}

        # shuffle ids before splitting
        random.shuffle( keep_images )

        # assume two splits, the first one gets the float arg as a percent of total
        # the remainder goes in the other
        start=0
        print(f"{len(keep_images)=}")
        for i, s in enumerate(SPLIT_NAMES):
            if i == 0:
                split_ids = { k: s for k in keep_images[: int( len(keep_images)* args.create_split) ] }
                start = max(0, len(split_ids)-1)
                print(f"{s} split, {len(split_ids)} images")
            else:
                other_split = { k: s for k in keep_images[start:] }
                split_ids.update(other_split)
                print(f"{s} split, {len(other_split)} images")

        print(f"{len(split_ids)=}, {len(keep_images)=}")
        # keeper of new json entries, top-level is split names
        new_records = { }
        for s in SPLIT_NAMES:
            new_records[s] = { 'images': [], 'annotations': [] }

        # iterate over all images, checking for them in the split
        for img in tqdm(records['images']):
            if img['id'] in split_ids:
                current_split = split_ids[ img['id'] ]
                
                if not args.no_reset_image_paths:
                    orig_img_path = img['file_name']
                    fname = os.path.basename(img['file_name'])

                    # set filename to new relative directory inside the dataset directory
                    new_relative_dir = os.path.join("images", current_split)
                    img['file_name'] = os.path.join(new_relative_dir, fname)

                    # make new directory for split images in new dataset home
                    new_full_dir = os.path.join(args.new_path, new_relative_dir)
                    if not os.path.exists(new_full_dir):
                        os.makedirs( new_full_dir )
                    
                    full_orig_path = os.path.join(args.dataset_path, "images", orig_split_name, orig_img_path)
                    new_full_path = os.path.join(new_full_dir, fname)
                    if args.move_images:
                        shutil.rename(full_orig_path, new_full_path)
                    else:
                        shutil.copy(full_orig_path, new_full_path)

                if args.print_file_names:
                    print(img['file_name'])
                new_records[ current_split ]['images'].append( img )

        for ann in records['annotations']:
            if ann['image_id'] in split_ids:
                current_split = split_ids[ ann['image_id'] ]
                new_records[ current_split ]['annotations'].append( ann )

    if args.new_path is not None:
        for s in new_records.keys():
            # copy 'other' parts of the json: licenses, info, categories
            for k in records.keys():
                if k not in new_records[s]:
                    new_records[s][k] = records[k]

            new_json_path = os.path.join(args.new_path, "annotations", f"instances_{s}.json")
            with open(new_json_path, mode='w') as nf:
                nf.write(json.dumps(new_records[s]))
                nf.close()
