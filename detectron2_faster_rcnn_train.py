#!/usr/bin/env python
import torch, detectron2
import matplotlib as mpl
from detectron2.data.datasets import register_coco_instances
import detectron2
from detectron2.utils.logger import setup_logger
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


get_ipython().system('nvcc --version')
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
datadir="/data/mtmoore/school/CSiML_AI395T/final_project/dataset/"
for d in ["IP8M-H-NW", "IP8M-H-SW", "combined" ]:
    dataset_dir=os.path.join(datadir, f"{f}_coco")
    annotation_dir=os.path.join(dataset_dir, "annotations")

    register_coco_instances(f"{d}_train", {}, os.path.path(annotation_dir, "instances_train.json"), dataset_dir)
    register_coco_instances(f"{d}_train", {}, os.path.path(annotation_dir, "instances_val.json"),   dataset_dir)

    for model in ["faster_rcnn_R_50_FPN_3x", "faster_rcnn_R_101_FPN_3x", ]:
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file(f"{model}.yaml"))
        cfg.DATASETS.TRAIN = (f"{d}_train",)
        cfg.DATASETS.TEST = ()
        cfg.DATALOADER.NUM_WORKERS = 8
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(f"COCO-Detection/{model}.yaml")  # Let training initialize from model zoo
        cfg.SOLVER.IMS_PER_BATCH = 2  # This is the real "batch size" commonly known to deep learning people
        cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
        cfg.SOLVER.MAX_ITER = 5000    # 300 iterations seems good enough for this toy dataset; you will need to train longer for a practical dataset
        cfg.SOLVER.STEPS = []        # do not decay learning rate
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512   # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (ballon). (see https://detectron2.readthedocs.io/tutorials/datasets.html#update-the-config-for-new-datasets)
        # NOTE: this config means the number of classes, but a few popular unofficial tutorials incorrect uses num_classes+1 here.
        cfg.SOLVER.CHECKPOINT_PERIOD = 100
        cfg.OUTPUT_DIR = f"/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2/{model}_{d}_{cfg.SOLVER.IMS_PER_BATCH}batch_512RoI_{attempt}"

        if not os.path.exists(cfg.OUTPUT_DIR):
            os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
            trainer = DefaultTrainer(cfg) 
            trainer.resume_or_load(resume=False)
            trainer.train()
        else:
            print(f"output dir {cfg.OUTPUT_DIR} already exists")




# Inference should use the config with parameters that are used in training
# cfg now already contains everything we've set previously. We changed it a little bit for inference:
for epoch in range(99, 5000, 100):
    odir = f"/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2/faster_rcnn_101_FPN_{cfg.SOLVER.IMS_PER_BATCH}batch_512RoI_0-{epoch+1}epochs-val"

    if os.path.exists(odir):
        print(f"Validation output exists: {odir}")
        continue
        
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, f"model_{epoch:07d}.pth")  # path to the model we just trained
    trainer = DefaultTrainer(cfg) 
    trainer.resume_or_load(resume=False)
    evaluator = COCOEvaluator("IP8M-H-NW_val", ("bbox",), False, output_dir=odir)
    val_loader = build_detection_test_loader(cfg, "IP8M-H-NW_val")
    eval_result = inference_on_dataset(trainer.model, val_loader, evaluator)
    #cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7   # set a custom testing threshold
    #predictor = DefaultPredictor(cfg)
    break


# In[ ]:


print(eval_result)


# In[ ]:


for d in random.sample(IP8M-H-NW_train, 3):
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=balloon_metadata, scale=0.5)
    out = visualizer.draw_dataset_dict(d)
    cv2_imshow(out.get_image()[:, :, ::-1])


# In[ ]:


from detectron2.utils.visualizer import ColorMode
dataset_dicts = get_balloon_dicts("balloon/val")
for d in random.sample(dataset_dicts, 3):    
    im = cv2.imread(d["file_name"])
    outputs = predictor(im)  # format is documented at https://detectron2.readthedocs.io/tutorials/models.html#model-output-format
    v = Visualizer(im[:, :, ::-1],
                   metadata=balloon_metadata, 
                   scale=0.5, 
                   instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels. This option is only available for segmentation models
    )
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    cv2_imshow(out.get_image()[:, :, ::-1])


# In[ ]:


evaluator = COCOEvaluator("IP8M-H-NW_val", ("bbox",), False, 
                          output_dir=f"/data/mtmoore/school/CSiML_AI395T/final_project/models/detectron2/faster_rcnn_101_FPN_{cfg.SOLVER.IMS_PER_BATCH}batch_512RoI_0-val")
val_loader = build_detection_test_loader(cfg, "IP8M-H-NW_val")
eval_result = inference_on_dataset(trainer.model, val_loader, evaluator)

