import os
import random
import h5py
import numpy as np
import torch
from torchvision import transforms
from scipy import ndimage
from scipy.ndimage.interpolation import zoom
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import json
from PIL import Image
import pickle as pkl
# Transpose.FLIP_LEFT_RIGHT 

normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])

def imresize(im, size, interp='bilinear'):
    if interp == 'nearest':
        resample = Image.NEAREST
    elif interp == 'bilinear':
        resample = Image.BILINEAR
    elif interp == 'bicubic':
        resample = Image.BICUBIC
    else:
        raise Exception('resample method undefined!')

    return im.resize(size, resample)

def random_rot_flip(image, label):
    k = np.random.randint(0, 4)
    image = np.rot90(image, k)
    label = np.rot90(label, k)
    axis = np.random.randint(0, 2)
    image = np.flip(image, axis=axis).copy()
    label = np.flip(label, axis=axis).copy()
    return image, label


def random_rotate(image, label):
    angle = np.random.randint(-20, 20)
    image = ndimage.rotate(image, angle, order=0, reshape=False)
    label = ndimage.rotate(label, angle, order=0, reshape=False)
    return image, label


def img_transform(img):
    # 0-255 to 0-1
    img = np.float32(np.array(img)) / 255.
    img = img.transpose((2, 0, 1))
    img = normalize(torch.from_numpy(img.copy()))
    return img

def segm_transform(segm):
    # to tensor, -1 to 149
    segm = torch.from_numpy(np.array(segm)).long()
    return segm

# H, W = (128, 128)
# x = torch.linspace(0, H, H+1) - H//2 - 0.5
# y = torch.linspace(0, W, W+1) - H//2 - 0.5
# grid_x, grid_y = torch.meshgrid(x[1:], y[1:])
# x_ = grid_x.reshape(H*H, 1)
# y_ = grid_y.reshape(W*W, 1)
# grid_pix = torch.cat((x_, y_), dim=1)
# grid_pix = grid_pix.reshape(1, H*W, 2)

class RandomGenerator(object):
    def __init__(self, output_size):
        self.output_size = output_size

    def __call__(self, sample):
        image, label = sample['image'], sample['label']

        if random.random() > 0.5:
            image, label = random_rot_flip(image, label)
        elif random.random() > 0.5:
            image, label = random_rotate(image, label)
        x, y = image.shape
        if x != self.output_size[0] or y != self.output_size[1]:
            image = zoom(image, (self.output_size[0] / x, self.output_size[1] / y), order=3)  # why not 3?
            label = zoom(label, (self.output_size[0] / x, self.output_size[1] / y), order=0)
        image = torch.from_numpy(image.astype(np.float32)).unsqueeze(0)
        label = torch.from_numpy(label.astype(np.float32))
        sample = {'image': image, 'label': label.long()}
        return sample


class Woodscape_dataset(Dataset):
    def __init__(self, base_dir, split, img_size, transform=None):
        self.transform = transform  # using transform in torch!
        self.split = split
        
        if split == 'train':
            with open(base_dir + '/train.json', 'r') as f:
                data = json.load(f)
        elif split == 'val':
            with open(base_dir + '/val.json', 'r') as f:
                data = json.load(f)
        elif split == 'test':
            with open(base_dir + '/test.json', 'r') as f:
                data = json.load(f)
        with open(base_dir + '/calib.pkl', 'rb') as f:
            calib = pkl.load(f)
        self.calib = calib
        self.data = data
        self.data_dir = base_dir
        self.img_size = img_size

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.data_dir + '/rgb_images/' + self.data[idx]
        lbl_path = self.data_dir + '/gtLabels/' + self.data[idx]
        mat_path = self.data_dir + '/index_16s_1k/' + self.data[idx][:-4] + '_img.npy'
        img = Image.open(img_path).convert('RGB')
        segm = Image.open(lbl_path).convert('L')
        key = self.data[idx][:-4] + '_img' + '.png'
        cls = np.load(mat_path)

        dist = self.calib[key].astype(np.float32)
        assert(segm.mode == "L")
        assert(img.size[0] == segm.size[0])
        assert(img.size[1] == segm.size[1])

            # random_flip
        if np.random.choice([0, 1]):
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            segm = segm.transpose(Image.FLIP_LEFT_RIGHT)

        # import pdb;pdb.set_trace()
        # note that each sample within a mini batch has different scale param
        img = imresize(img, (self.img_size, self.img_size), interp='bilinear')
        segm = imresize(segm, (self.img_size,self.img_size), interp='nearest')

        # image transform, to torch float tensor 3xHxW
        img = img_transform(img)

        # segm transform, to torch long tensor HxW
        segm = segm_transform(segm)

        # sample = {'image': img, 'label': segm, 'dist':dist, 'class':cls}
        return img, segm, dist, cls


if __name__=='__main__':
    db_train = Woodscape_dataset(base_dir="/home-local2/akath.extra.nobkp/woodscapes", split="train")
    # trainloader = DataLoader(db_train, batch_size=8, shuffle=True, num_workers=1, pin_memory=True)
    # for i_batch, sampled_batch in enumerate(trainloader):
    #     import pdb;pdb.set_trace()
    #     print("ass")
    m = db_train[0]
    import pdb;pdb.set_trace()
    print("ass")
