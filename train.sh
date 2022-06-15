#!/bin/bash 

python -m torch.distributed.launch \
--nproc_per_node 3 \
--master_port 12345  main.py \
--cfg configs/swin/distorted_swin_small_patch2_window4_64.yaml \
--data-path /gel/usr/akath/distorted-tiny-imagenet \
--batch-size 128