#!/usr/bin/env python
# based on example in https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5

import argparse, os, json
import torch, detectron2
import matplotlib as mpl
from detectron2.data.datasets import register_coco_instances
import detectron2
from detectron2.utils.logger import setup_logger
import numpy as np
import cv2, random
import matplotlib as mpl

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader
from detectron2.engine import DefaultTrainer
from detectron2.utils.events import get_event_storage


TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
print("detectron2:", detectron2.__version__)
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
import matplotlib as mpl
# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader
from detectron2.engine import DefaultTrainer
from detectron2.utils.events import get_event_storage
attempt=0

if __name__=="__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", type=str, required=True, help="model name from model zoo, located in Coco_Detection directory")
    parser.add_argument("--dataset", type=str, required=True, help="dataset name, located in dataset-dir")
    parser.add_argument("--dataset-dir", type=str, required=True, help="dataset directory, parent of where dataset should be found")
    parser.add_argument("--output-dir", type=str, required=True, help="location for model outputs")
    args = parser.parse_args()
    
    dataset_dir=os.path.join(args.dataset_dir, f"{args.dataset}_coco")
    annotation_dir=os.path.join(dataset_dir, "annotations")

    register_coco_instances(f"{args.dataset}_train", {}, os.path.join(annotation_dir, "instances_train.json"), dataset_dir)
    register_coco_instances(f"{args.dataset}_val", {}, os.path.join(annotation_dir, "instances_val.json"),   dataset_dir)

    print(args)
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(f"COCO-Detection/{args.model}.yaml"))
    cfg.DATASETS.TRAIN = (f"{args.dataset}_train",)
    cfg.DATASETS.TEST = ()
    cfg.DATALOADER.NUM_WORKERS = 8
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(f"COCO-Detection/{args.model}.yaml")  # Let training initialize from model zoo
    cfg.SOLVER.IMS_PER_BATCH = 6  # This is the real "batch size" commonly known to deep learning people
    cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
    cfg.SOLVER.MAX_ITER = 5000    # 300 iterations seems good enough for this toy dataset; you will need to train longer for a practical dataset
    cfg.SOLVER.STEPS = []        # do not decay learning rate
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (ballon). (see https://detectron2.readthedocs.io/tutorials/datasets.html#update-the-config-for-new-datasets)
    # NOTE: this config means the number of classes, but a few popular unofficial tutorials incorrect uses num_classes+1 here.
    cfg.SOLVER.CHECKPOINT_PERIOD = 100
    cfg.OUTPUT_DIR = f"{args.output_dir}/{args.model}_{args.dataset}_{cfg.SOLVER.IMS_PER_BATCH}batch_512RoI_{attempt}"

    if not os.path.exists(cfg.OUTPUT_DIR):
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
        trainer = DefaultTrainer(cfg) 
        trainer.resume_or_load(resume=False)
        trainer.train()
    else:
        print(f"output dir {cfg.OUTPUT_DIR} already exists")

