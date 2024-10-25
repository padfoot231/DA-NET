#!/bin/bash 
export WANDB_MODE="disabled"


python -m torch.distributed.launch \
--nproc_per_node 4 \
--master_port 12345  main.py \
--cfg configs/swin/CVRG_swin.yaml \
--output /home/prongs/scratch/Swin-unet-disc-sem-new \
--data-path  $SLURM_TMPDIR/data_new/semantic2d3d \
--fov 175.0 \
--xi 0.0 \
--batch-size 8 \
--resume /home/prongs/scratch/Swin-unet-disc-sem-new/swin_new/default/ckpt_epoch_best_new.pth 

# 
