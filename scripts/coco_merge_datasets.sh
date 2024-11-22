import argparse
import glob
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
    parser.add_argument("--dataset-source", nargs='+', type=str, help="paths to datasets")
    parser.add_argument("--dataset-destination", type=str, default='new_dataset',  help="New location for datasets")
    args = parser.parse_args()

    # make sure annotation file exists
    for dataset in args.dataset_source:
        if not os.path.exists( dataset ):
            print(f"provided source {dataset} doesn't exist")
            sys.exit(1)

    # create directory for new dataset
    try: 
        os.makedirs( args.dataset_destination, exist_ok=False)
        os.makedirs( os.path.join(args.dataset_destination, "annotations"), exist_ok=False)
        for s in SPLIT_NAMES:
            os.makedirs( os.path.join(args.dataset_destination, "images", s), exist_ok=False)

    except FileExistsError:
        print("Location for new dataset exists, not overwriting. Exiting")
        sys.exit(1)
       

#    new_dataset = { 'image_ids' = [], 'annotation_ids' = [], 'images' = [], 'annotations' = [] }

    img_id_map = { }
    ann_id_map = { }
    new_records = { }
    for dataset in args.dataset_source:

        print(f"dataset source: {dataset}")

        # iterate over each split
        for a in glob.glob(os.path.join(dataset, "annotations", "*.json")):
            print(f"json file: {a}")

            # ugly way to get the name of the original split source which is probably just default
            orig_split_name = os.path.basename(a).split("_")[1].split(".")[0]
            
            # map original img ids if they need to change
            img_id_map[orig_split_name] = {}
            ann_id_map[orig_split_name] = {}
            new_records[orig_split_name] = { 'annotations': [], 'images': [] }

            with open(a) as f:
                records = json.load(f)

                for img in records['images']:
                    # if id already exists, map to a new value recording the mapping and update img
                    if img['id'] in img_id_map[orig_split_name]:
                        img_id_map[orig_split_name][ img['id'] ] = len(img_id_map[orig_split_name])
                        img['id'] = img_id_map[orig_split_name][ img['id'] ]
                    else:
                        img_id_map[orig_split_name][ img['id'] ] = img["id"]

                    # filename was fixed when we generated the dataset
                    # img['file_name'] = os.path.join(new_relative_dir, fname)
                    print(f"original filename: {img['file_name']}")
                    # make new directory for split images in new dataset home
                    new_full_path = os.path.join(args.dataset_destination, img['file_name'])
                    full_orig_path = os.path.join(dataset, img['file_name'])
                    print(f"copying {full_orig_path} -> {new_full_path}")
                    shutil.copy(full_orig_path, new_full_path)

                    new_records[orig_split_name]['images'].append(img)

                for ann in records['annotations']:
                    # update ids when merging
                    if ann['id'] in ann_id_map[orig_split_name]:
                        ann_id_map[orig_split_name][ ann['id'] ] = len(ann_id_map[orig_split_name])
                        ann['id'] = ann_id_map[orig_split_name][ ann['id'] ]
                    else:
                        ann_id_map[orig_split_name][ ann['id'] ] = ann['id']
                    
                    # update image reference with new image id
                    ann['image_id'] = img_id_map[orig_split_name][ ann['image_id'] ]

                    new_records[ orig_split_name]['annotations'].append( ann )
                for s in new_records.keys():
                    for k in records.keys():
                        if k not in new_records:
                            new_records[s][k] = records[k]

    if args.dataset_destination is not None:
        for s in new_records.keys():
            # copy 'other' parts of the json: licenses, info, categories
            for k in records.keys():
                if k not in new_records[s]:
                    new_records[s][k] = records[k]

            new_json_path = os.path.join(args.dataset_destination, "annotations", f"instances_{s}.json")
            with open(new_json_path, mode='w') as nf:
                nf.write(json.dumps(new_records[s]))
                nf.close()
