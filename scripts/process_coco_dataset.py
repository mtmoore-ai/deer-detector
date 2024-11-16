import argparse
import json
import os
import sys

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation-file",  type=str, default="instances_default.json", help="json formatted annotation")
    parser.add_argument("--start-id", type=int, default=0, help="id to start keeping, default=0")
    parser.add_argument("--end-id", type=int, default=-1, help="last id to include, default=-1, end of ids")
    parser.add_argument("--new-annotation-file",  type=str, default="new_instances_default.json", help="new file with modified annotations")

    args = parser.parse_args()

    print(args)
    if not os.path.exists( args.annotation_file):
       print("provided annotation file doesn't exist")
       sys.exit(1)

    with open(args.annotation_file) as f:
        records = json.load(f)

        imgs = sorted([ img['id'] for img in records['images'] ])
        keep_images = imgs[args.start_id:args.end_id]

        image_keep_list = []
        annotation_keep_list = []
        for img in records['images']:
            if img['id'] in keep_images:
                image_keep_list.append(img)
        for ann in records['annotations']:
            if ann['image_id'] in keep_images:
                annotation_keep_list.append(ann)
 
        records['images'] = image_keep_list
        records['annotation'] = annotation_keep_list

    with open(args.new_annotation_file, mode='w') as nf:
        nf.write(json.dumps(records))
        nf.close()
