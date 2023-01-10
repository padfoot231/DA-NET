#!/bin/bash 
# export WANDB_MODE="disabled"


python -m torch.distributed.launch \
--nproc_per_node 2 \
--master_port 12345  main.py \
--cfg configs/swin/one_distortion_swin_small_patch2_window4_64_gp2_jit.yaml \
--data-path /home-local2/akath.extra.nobkp/imagenet_2010 \
--batch-size 128
