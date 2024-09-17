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



class ScenarioConfig(object):
    def __init__(self, world, numOfAgents = None, numCamerasPerAgent = None, weather = None, timeOfDay=None, classes =None,
        crowdLevel =None, occlusionProb = None,town = None, speedStatus= None, annotation = None):
        pass
    def placeAgents(self):
        pass
    def placeSensors(self):
        pass
    def setWeather(self):
        weather = carla.WeatherParameters(
        cloudiness=80.0,  # Cloudiness percentage
        rain=30.0,        # Rain intensity
        wind_intensity=50.0,  # Wind intensity
        sun_azimuth_angle=70.0,  # Sun azimuth angle
        sun_altitude_angle=70.0  # Sun altitude angle
         )
        self.world.set_weather(weather)
        pass
    def setTimeOfDay(self):
        pass
    def setClasses(self):
        pass
    def setCrowdLevel(self):
        pass
    def setOcclusionProb(self):
        pass
    def setTown(self):
        pass
    def setSpeedStatus(self):
        pass
    def setAnnotation(self):
        pass