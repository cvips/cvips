# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Handy conversions for CARLA images.

The functions here are provided for real-time display, if you want to save the
converted images, save the images from Python without conversion and convert
them afterwards with the C++ implementation at "Util/ImageConverter" as it
provides considerably better performance.
"""

import glob
import os
import sys


try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

try:
    import numpy as np
    from numpy.matlib import repmat
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')


def to_bgra_array(image):
    """Convert a CARLA raw image to a BGRA numpy array."""
    '''
    if not isinstance(image, sensor.Image):
        raise ValueError("Argument must be a carla.sensor.Image")
    '''
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    return array


def to_rgb_array(image):
    """Convert a CARLA raw image to a RGB numpy array."""
    array = to_bgra_array(image)
    # Convert BGRA to RGB.
    array = array[:, :, :3]
    # array = array[:, :, ::-1]
    return array

def labels_to_array(image):
    """
    Convert an image containing CARLA semantic segmentation labels to a 2D array
    containing the label of each pixel.
    """
    return to_bgra_array(image)[:, :, 2]

def vrus_only_label_array(image):
    """
    Convert an image containing CARLA semantic segmentation labels to
    an image showing only pedestrians.
    """
    classes = {
        12: [220, 20, 60],    # Pedestrian
        13: [255, 0, 0],      # Rider
        18: [0, 0, 230],      # Motorcycle
        19: [119, 11, 32],    # Bicycle
    }
    array = labels_to_array(image)
    result = np.zeros((array.shape[0], array.shape[1]))
    for key, value in classes.items():
        result[np.where(array == key)] = 1
    return result

def vrus_only(image):
    """
    Convert an image containing CARLA semantic segmentation labels to
    an image showing only pedestrians.
    """
    classes = {
        12: [220, 20, 60],    # Pedestrian
        13: [255, 0, 0],      # Rider
        18: [0, 0, 230],      # Motorcycle
        19: [119, 11, 32],    # Bicycle
    }
    array = labels_to_array(image)
    result = np.zeros((array.shape[0], array.shape[1], 3))
    for key, value in classes.items():
        result[np.where(array == key)] = value
    return result

def labels_to_cityscapes_palette(image):
    """
    Convert an image containing CARLA semantic segmentation labels to
    Cityscapes palette.
    """
    classes = {
        0: [0, 0, 0],         # Unlabeled
        1: [128, 64, 128],    # Roads
        2: [244, 35, 232],    # SideWalks
        3: [70, 70, 70],      # Building
        4: [102, 102, 156],   # Wall
        5: [190, 153, 153],   # Fence
        6: [153, 153, 153],   # Pole
        7: [250, 170, 30],    # TrafficLight
        8: [220, 220, 0],     # TrafficSign
        9: [107, 142, 35],    # Vegetation
        10: [152, 251, 152],  # Terrain
        11: [70, 130, 180],   # Sky
        12: [220, 20, 60],    # Pedestrian
        13: [255, 0, 0],      # Rider
        14: [0, 0, 142],      # Car
        15: [0, 0, 70],       # Truck
        16: [0, 60, 100],     # Bus
        17: [0, 60, 100],     # Train
        18: [0, 0, 230],      # Motorcycle
        19: [119, 11, 32],    # Bicycle
        20: [110, 190, 160],  # Static
        21: [170, 120, 50],   # Dynamic
        22: [55, 90, 80],     # Other
        23: [45, 60, 150],    # Water
        24: [157, 234, 50],   # RoadLine
        25: [81, 0, 81],      # Ground
        26: [150, 100, 100],  # Bridge
        27: [230, 150, 140],  # RailTrack
        28: [180, 165, 180]   # GuardRail
    }
    array = labels_to_array(image)
    result = np.zeros((array.shape[0], array.shape[1], 3))
    for key, value in classes.items():
        result[np.where(array == key)] = value
    return result


def depth_to_array(image):
    """
    Convert an image containing CARLA encoded depth-map to a 2D array containing
    the depth value of each pixel normalized between [0.0, 1.0].
    """
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))  # RGBA format
    array = array[:, :, :3]  # Take only BGR
    array = array[:, :, ::-1]  # RGB
    array = array.astype(np.float32)  # 2ms
    gray_depth = ((array[:, :, 0] + array[:, :, 1] * 256.0 + array[:, :, 2] * 256.0 * 256.0) / (
                (256.0 * 256.0 * 256.0) - 1))  # 2.5ms
    gray_depth = 1000 * gray_depth
    log_depth= np.log1p(gray_depth)
    # gray_depth = 1000 *((log_depth - np.min(log_depth)) / (np.max(log_depth) - np.min(log_depth)))
    return log_depth


def depth_to_logarithmic_grayscale(image):
    """
    Convert an image containing CARLA encoded depth-map to a logarithmic
    grayscale image array.
    "max_depth" is used to omit the points that are far enough.
    """
    normalized_depth = depth_to_array(image)
    # Convert to logarithmic depth.
    logdepth = np.ones(normalized_depth.shape) + \
        (np.log(normalized_depth) / 5.70378)
    logdepth = np.clip(logdepth, 0.0, 1.0)
    logdepth *= 255.0
    # Expand to three colors.
    return np.repeat(logdepth[:, :, np.newaxis], 3, axis=2)