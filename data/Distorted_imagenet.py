from dis import dis
import os
import json
import torch.utils.data as data
import numpy as np
from PIL import Image
from utils import get_sample_params_from_subdiv, get_sample_locations, distort_image
import warnings
import torch 
from glob import glob
import pickle as pkl
import torch.nn as nn
from datetime import datetime
import random
from pyinstrument import Profiler

warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)


def random_1():
    return 1 if random.random() < 0.5 else -1



def random_direction_normal(dim, n):
    p = np.abs(np.random.standard_normal((dim, n)))
    norm = np.sqrt(np.sum(p**2, axis=0))
    return p / norm

def random_direction_uniform(dim, n):
    p = np.random.uniform(0, 1, (dim, n))
    norm = np.sqrt(np.sum(p**2, axis=0))
    return p / norm

def random_magnitude_uniform(points, high=1):
    scale = np.random.uniform(0, high, points.shape[1])
    return points * scale

def random_magnitude_custom(points, high=1):
    scale = np.random.uniform(0, high, points.shape[1])**(1/points.shape[0])
    return points * scale




class M_distort(data.Dataset):
    def __init__(self, root, transform=None, task='train', target_transform=None, radius_cuts=16, azimuth_cuts=64, in_chans=3, img_size=(64, 64)):
        super(M_distort, self).__init__()
        self.data_path = root
        # self.in_chans = in_chans
        # self.subdiv = (radius_cuts, azimuth_cuts)
        # self.n_radius = 15
        # self.n_azimuth = 15
        self.img_size = img_size

        with open(self.data_path + '/classes.pkl', 'rb') as f:
            classes = pkl.load(f)
        
        self.classes = classes
        # with open('distortion_file.pkl') as f: ####
        #     distortion  = pkl.load(f)
        # lst = []
        if task == 'train':
            with open(self.data_path + '/train/train_20.pkl', 'rb') as f:
                data = pkl.load(f)
            # with open(self.data_path + '/train_data.pkl', 'rb') as f:
            #     data = pkl.load(f)
        elif task == 'val':
            with open(self.data_path + '/val/val_20.pkl', 'rb') as f:
                data = pkl.load(f)
        elif task == 'test':
            with open(self.data_path + '/test/test_20.pkl', 'rb') as f:
                data = pkl.load(f)
            # with open(self.data_path + '/val_data.pkl', 'rb') as f:
            #     data = pkl.load(f)
        

        with open(self.data_path + '/dist_params.pkl', 'rb') as f:
            test_dist = pkl.load(f)


        # classes = list(data.keys())

        # self.test = data

        # data_img = {}

        # for i in range(len(data)):


        #     data_img[i] = (keys[i], keys[i].split('/')[1])

        # for i in range(len(data)):
        #     for j in range(len(data[classes[i]])):
        #         data_img[idx] = (data[classes[i]][j], i, data[classes[i]][j].split('/')[-2])
        #         idx = idx+1
        self.test_dist = test_dist
        self.task = task 
        # self.data_img = data_img
        self.data = data
        self.transform = transform
        self.target_transform = target_transform
        # # id & label: https://github.com/google-research/big_transfer/issues/7
        # # total: 21843; only 21841 class have images: map 21841->9205; 21842->15027
        # self.database = json.load(open(self.ann_path))

    # def _load_image(self, path):
    #     try:
    #         im = Image.open(path)
    #     except:
    #         print("ERROR IMG LOADED: ", path)
    #         random_img = np.random.rand(224, 224, 3) * 255
    #         im = Image.fromarray(np.uint8(random_img))
    #     return im

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is class_index of the target class.

            return sampling points for each image and targets :) 
        """
        # print("start params")
#         radius_buffer, azimuth_buffer = 0, 0
#         # get_optimal_buffers(subdiv, n_radius, n_azimuth, img_size)
#         # for k in range(len(keys)):
#         # print(dist[keys[3]])

#         # print(self.data[self.data_img[index][0]])
#         params = get_sample_params_from_subdiv(
#             subdiv=self.subdiv,
#             img_size=self.img_size,
#             D = self.data[self.keys[index]], 
#             n_radius=self.n_radius,
#             n_azimuth=self.n_azimuth,
#             radius_buffer=radius_buffer,
#             azimuth_buffer=azimuth_buffer)


#         # print ("start sample locations")
#         sample_locations = get_sample_locations(**params)
        
# # cProfile.run(get_sample_locations())
#         x_ = torch.tensor(sample_locations[0]).reshape(1024, 1, self.n_radius*self.n_azimuth, 1).float()
#         x_ = x_/ 32
#         x_.long()
#         y_ = torch.tensor(sample_locations[1]).reshape(1024, 1, self.n_radius*self.n_azimuth, 1).float()
#         y_ = y_/32
#         y_.long()
#         out = torch.cat((x_, -(y_)), dim = 3)

        # print("end_sample_location")
        images = Image.open(self.data_path + '/' + self.data[index])

        if self.task == 'train' or self.task=='val':
            points = random_direction_normal(4, 1)
            D = random_magnitude_uniform(points, high=50).T
            D = D[0]
        elif self.task == 'test':
            D = self.test_dist[self.data[index]]
        # images.save("test.png")
        # D = np.array([0.0, 0.0, 0.0, 0.0])
        images = distort_image(images, D)
        # images.save("test_dis.png")


        # images.shape

        # out = self.data[self.data_img[index][0]]


        target = int(self.classes.index(self.data[index].split('/')[1]))

        # distortion = self.data_img[index][2]
        # print(distortion)
        # import pdb;pdb.set_trace()
        

        if self.transform is not None:
            images = self.transform(images)
        
        # print("distorted_dataloader")

        # C, H, W = images.shape

        # image = images.reshape(1, C, H, W)

        # tensor = nn.functional.grid_sample(image, out.reshape(1, self.subdiv[0]*self.subdiv[1], self.n_radius*self.n_azimuth,2), align_corners = True).permute(0,2,1,3).reshape(self.subdiv[0], self.subdiv[1], self.n_radius*self.n_azimuth*self.in_chans)

        # # target
        # # target = int(idb[1])
        # if self.target_transform is not None:
        #     target = self.target_transform(target)
        ######################## 

        # self.num_patches = radius_cuts*azimuth_cuts
        # self.in_chans = in_chans
        # self.embed_dim = embed_dim

        
        # subdiv = 3

        # print(tensor.shape, tensor[0].shape)
        # import pdb;pdb.set_trace()

        # now = datetime.now()

        # current_time = now.strftime("%H:%M:%S")
        # print("Current Time =", current_time)
        # print(index)
        return images, target, D

    def __len__(self):
        return len(self.data)

if __name__=='__main__':

    m = M_distort('/home-local2/akath.extra.nobkp/imagenet_2010', task='train')
    import pdb;pdb.set_trace()
    m[1]
    

