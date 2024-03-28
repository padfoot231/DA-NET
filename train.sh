#!/bin/bash 
export WANDB_MODE="disabled"


python -m torch.distributed.launch \
--nproc_per_node 1 \
--master_port 12345  main.py \
--cfg configs/swin/CVRG_den_unet.yaml \
--output /home-local2/akath.extra.nobkp/Radial-unet \
--data-path /home-local2/akath.extra.nobkp/CVRG-Pano \
--fov 170.0 \
--xi 0.0 \
--batch-size 1