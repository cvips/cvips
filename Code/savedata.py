import glob
import os
import sys
from cvips_config import *
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import logging
import math
import pygame
import random
import queue
import numpy as np
from bounding_box import create_kitti_datapoint
from constants import *
import image_converter
from dataexport import *
from PIL import Image


class saveSample(object):
    def __init__(self, town, agentList, camList, imgList, lidar, label, bev):
        pass
    def creatPath(self):
        pass
    def saveImages(town, agent_list, cam_list, img, lidar, label, bev):
        pass
    def saveLabels(town, agent_list, cam_list, img, lidar, label, bev):
        pass
    def saveLidar():
        pass
    