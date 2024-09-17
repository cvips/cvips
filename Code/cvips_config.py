import glob
import os
import sys
# from config import *
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
from constants import *
import image_converter
from dataexport import *
from icecream import ic



Town_list = [ "Town03", "Town04", "Town05", "Town06", "Town07", "Town10HD"]
agent_list = ["veh1", "veh2", "veh3", "veh4","infra1", "infra2"]
camera_list = ["Camera_FrontLeft", "Camera_Front", "Camera_FrontRight", "Camera_BackLeft", "Camera_Back", "Camera_BackRight"]

# Position of the agents based on town type
# weather categories {clear, rainy, cloudy, wet}
# Time of the day {Noon, Sunset, Night}
# Size type variability or class type variability for pedestrians
# Class speed variability
# Pedestrian emerging from two parked vehicles
# Pedestrian walking/running/jogging toward the crossing
config = {
    "Town03": {
        "4way": {
            "wnse": {"veh1_pose": "", 
                     "veh2_pose": "",
                    "veh3_pose": "",
                    "veh4_pose": "", 
                    "infra1_pose": "", 
                    "infra2_pose": ""},
            "wsee": {"veh1_pose": "",
                      "veh2_pose": "", 
                      "veh3_pose": "", 
                      "veh4_pose": "", 
                      "infra1_pose": "", 
                      "infra2_pose": ""},
            "wwss": {"veh1_pose": "", 
                     "veh2_pose": "", 
                     "veh3_pose": "", 
                     "veh4_pose": "", 
                     "infra1_pose": "",
                       "infra2_pose": ""},
            "wwee": {"veh1_pose": "", 
                     "veh2_pose": "", 
                     "veh3_pose": "", 
                     "veh4_pose": "", 
                     "infra1_pose": "", 
                     "infra2_pose": ""},
            "wwws": {"veh1_pose": "", 
                     "veh2_pose": "", 
                     "veh3_pose": "", 
                     "veh4_pose": "", 
                     "infra1_pose": "", 
                     "infra2_pose": ""},
        },
        "3way": {
            "wwss": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wsse": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wwse": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
        }
    },
    "Town04": {
        "4way": {
            "wnse": {"veh1_pose": carla.Transform(carla.Location(x=231,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                     "veh2_pose": carla.Transform(carla.Location(x=255,y=-278.53, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=258.61,y=-214.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=287,y=-250, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-255.00, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.88,y=-239.54, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
                     
            "wsee": {"veh1_pose":carla.Transform(carla.Location(x=231,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=258.61,y=-214.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "veh3_pose": carla.Transform(carla.Location(x=287,y=-250, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                      "veh4_pose": carla.Transform(carla.Location(x=297,y=-250, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-255.00, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.88,y=-239.54, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
            "wwss": {"veh1_pose": carla.Transform(carla.Location(x=231,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=221,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh3_pose": carla.Transform(carla.Location(x=258.61,y=-214.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "veh4_pose": carla.Transform(carla.Location(x=258.61,y=-224.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-255.00, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.88,y=-239.54, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
            "wwee": {"veh1_pose": carla.Transform(carla.Location(x=231,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=221,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh3_pose": carla.Transform(carla.Location(x=287,y=-250, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                      "veh4_pose": carla.Transform(carla.Location(x=297,y=-250, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-255.00, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.88,y=-239.54, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
            "wwws": {"veh1_pose": carla.Transform(carla.Location(x=231,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=221,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh3_pose": carla.Transform(carla.Location(x=241,y=-246.18, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=258.61,y=-214.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-255.00, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.88,y=-239.54, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
        },
        "3way": {
            "wwss": {"veh1_pose": carla.Transform(carla.Location(x=234,y=-308.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                    "veh2_pose": carla.Transform(carla.Location(x=224,y=-308.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                    "veh3_pose": carla.Transform(carla.Location(x=258.81,y=-285.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                    "veh4_pose": carla.Transform(carla.Location(x=258.81,y=-275.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-303.17, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.82,y=-302.53, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
            "wsse": {"veh1_pose": carla.Transform(carla.Location(x=234,y=-308.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=258.81,y=-285.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)),  
                     "veh3_pose": carla.Transform(carla.Location(x=258.81,y=-275.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "veh4_pose": carla.Transform(carla.Location(x=273.8,y=-310.70, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),  
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-303.17, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.82,y=-302.53, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
            "wwse": {"veh1_pose": carla.Transform(carla.Location(x=234,y=-308.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                    "veh2_pose": carla.Transform(carla.Location(x=224,y=-308.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                    "veh3_pose": carla.Transform(carla.Location(x=258.81,y=-275.00, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "veh4_pose": carla.Transform(carla.Location(x=273.8,y=-310.70, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),  
                     "infra1_pose": carla.Transform(carla.Location(x=250,y=-303.17, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "infra2_pose": carla.Transform(carla.Location(x=263.82,y=-302.53, z=4.0000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)) },
        }
    },
    "Town05": {
        "4way": {
            "wnse": {"veh1_pose": carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                      "veh2_pose": carla.Transform(carla.Location(x=-43.60,y=53.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                      "veh3_pose": carla.Transform(carla.Location(x=-54.71, y=-43.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.000000, roll=0.000000)), 
                      "veh4_pose": carla.Transform(carla.Location(x=-81.40,y=6.24, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                      "infra1_pose": carla.Transform(carla.Location(x=-60.000000, y=15.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                      "infra2_pose": carla.Transform(carla.Location(x=-38.050000, y=-10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wwss": {"veh1_pose": carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                      "veh2_pose": carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                      "veh3_pose": carla.Transform(carla.Location(x=-54.71, y=-59.52, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.000000, roll=0.000000)), 
                      "veh4_pose": carla.Transform(carla.Location(x=-54.71, y=-43.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.000000, roll=0.000000)), 
                      "infra1_pose": carla.Transform(carla.Location(x=-60.000000, y=15.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                      "infra2_pose": carla.Transform(carla.Location(x=-38.050000, y=-10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wsee": {"veh1_pose": carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                      "veh2_pose": carla.Transform(carla.Location(x=-43.60,y=53.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                      "veh3_pose": carla.Transform(carla.Location(x=-81.40,y=6.24, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                      "veh4_pose": carla.Transform(carla.Location(x=-91.40,y=6.24, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                      "infra1_pose": carla.Transform(carla.Location(x=-60.000000, y=15.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                      "infra2_pose": carla.Transform(carla.Location(x=-38.050000, y=-10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wwee": {"veh1_pose": carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                      "veh2_pose": carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                      "veh3_pose": carla.Transform(carla.Location(x=-81.40,y=6.24, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                      "veh4_pose": carla.Transform(carla.Location(x=-91.40,y=6.24, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                      "infra1_pose": carla.Transform(carla.Location(x=-60.000000, y=15.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                      "infra2_pose": carla.Transform(carla.Location(x=-38.050000, y=-10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},


            "wwws": {"veh1_pose": carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                    "veh2_pose": carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)), 
                    "veh3_pose": carla.Transform(carla.Location(x=-20,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                    "veh4_pose": carla.Transform(carla.Location(x=-43.60,y=43.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                    "infra1_pose": carla.Transform(carla.Location(x=-60.000000, y=15.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                    "infra2_pose": carla.Transform(carla.Location(x=-38.050000, y=-10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},
        },
        "3way": {
            "wwss": {"veh1_pose": carla.Transform(carla.Location(x=-150.90,y=-135.5, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                     "veh2_pose": carla.Transform(carla.Location(x=-160.90,y=-135.5, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),  
                     "veh3_pose": carla.Transform(carla.Location(x=-120.90,y=-113.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                     "veh4_pose": carla.Transform(carla.Location(x=-120.90,y=-103.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                    "infra1_pose": carla.Transform(carla.Location(x=-140.30,y=-130.47, z=4.00000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                    "infra2_pose":carla.Transform(carla.Location(x=-116.30,y=-130.47, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},

            "wsse": {"veh1_pose": carla.Transform(carla.Location(x=-150.90,y=-135.5, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)), 
                     "veh2_pose": carla.Transform(carla.Location(x=-120.90,y=-113.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)),  
                     "veh3_pose": carla.Transform(carla.Location(x=-120.90,y=-103.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)), 
                    "veh4_pose": carla.Transform(carla.Location(x=-103.30,y=-145.4, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                    "infra1_pose": carla.Transform(carla.Location(x=-140.30,y=-130.47, z=4.00000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                    "infra2_pose":carla.Transform(carla.Location(x=-116.30,y=-130.47, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},

            "wwse": {"veh1_pose": carla.Transform(carla.Location(x=-150.90,y=-135.5, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                    "veh2_pose": carla.Transform(carla.Location(x=-160.90,y=-135.5, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                    "veh3_pose": carla.Transform(carla.Location(x=-120.90,y=-113.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270, roll=0.000000)),  
                    "veh4_pose":carla.Transform(carla.Location(x=-103.30,y=-145.4, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000)),
                    "infra1_pose": carla.Transform(carla.Location(x=-140.30,y=-130.47, z=4.00000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000)),
                    "infra2_pose":carla.Transform(carla.Location(x=-116.30,y=-130.47, z=4.000000), carla.Rotation(pitch=0.000000, yaw=0, roll=0.000000))},
        }
    },

    "Town07": {
        "4way": {
            "wnse": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wsee": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wwss": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wwee": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wwws": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
        },
        "3way": {
            "wwss": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wsse": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
            "wwse": {"veh1_pose": "", "veh2_pose": "", "veh3_pose": "", "veh4_pose": "", "infra1_pose": "", "infra2_pose": ""},
        }
    },
    "Town10HD": {
        "4way": {
            "wnse": {"veh1_pose":  carla.Transform(carla.Location(x=19.52700-10, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh2_pose": carla.Transform(carla.Location(x=-49.642700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.0, roll=0.000000)), 
                     "veh3_pose":carla.Transform(carla.Location(x=-43.572700, y=50.0, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.0, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-80.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-36.000000, y=37.400000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

             "wwss": {"veh1_pose":carla.Transform(carla.Location(x=19.52700-10, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh2_pose":carla.Transform(carla.Location(x=19.52700, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=-43.572700, y=50.0-8, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.0, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-43.572700, y=50.0, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.0, roll=0.000000)), #w
                     "infra1_pose": carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-36.000000, y=37.400000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

           "wsee": {"veh1_pose": carla.Transform(carla.Location(x=19.52700-10, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh2_pose": carla.Transform(carla.Location(x=-43.572700, y=50.0, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.0, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=-70.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-36.000000, y=37.400000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wwee": {"veh1_pose":carla.Transform(carla.Location(x=19.52700-10, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh2_pose":carla.Transform(carla.Location(x=19.52700, y=12.9, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.0, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=-70.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-36.000000, y=37.400000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wwws": {"veh1_pose": carla.Transform(carla.Location(x=-70.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "veh2_pose": carla.Transform(carla.Location(x=-80.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=-90.11, y=24.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-43.572700, y=50.0, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.0, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-36.000000, y=37.400000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},
        },
        "3way": {
            "wwss": {"veh1_pose": carla.Transform(carla.Location(x=13.382700, y=-68.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.432304, roll=0.000000)),
                    "veh2_pose": carla.Transform(carla.Location(x=3.382700, y=-68.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.432304, roll=0.000000)),
                    "veh3_pose": carla.Transform(carla.Location(x=-41.3382700, y=-7.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.432304, roll=0.000000)),
                    "veh4_pose": carla.Transform(carla.Location(x=-41.3382700, y=-17.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.432304, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-34.000000, y=-55.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-57.000000, y=-55.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},

            "wsse": {"veh1_pose": carla.Transform(carla.Location(x=13.382700, y=-68.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.432304, roll=0.000000)),
                     "veh2_pose":carla.Transform(carla.Location(x=-97.382700, y=-43.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=315.432304, roll=0.000000)),
                    "veh3_pose": carla.Transform(carla.Location(x=-41.3382700, y=-7.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.432304, roll=0.000000)),
                    "veh4_pose": carla.Transform(carla.Location(x=-41.3382700, y=-17.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.432304, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-34.000000, y=-55.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-57.000000, y=-55.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},
                     
            "wwse": {"veh1_pose": carla.Transform(carla.Location(x=13.382700, y=-68.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.432304, roll=0.000000)),
                    "veh2_pose": carla.Transform(carla.Location(x=3.382700, y=-68.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180.432304, roll=0.000000)),
                     "veh3_pose": carla.Transform(carla.Location(x=-97.382700, y=-43.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=315.432304, roll=0.000000)),
                     "veh4_pose": carla.Transform(carla.Location(x=-41.3382700, y=-17.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.432304, roll=0.000000)),
                     "infra1_pose": carla.Transform(carla.Location(x=-34.000000, y=-55.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)), 
                     "infra2_pose": carla.Transform(carla.Location(x=-57.000000, y=-55.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0))},
        }
    }
}





print(config['Town10HD']['4way']['wnse']['veh1_pose'])





camera_positions_vehicle = {
    'Camera_Front':       carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':        carla.Transform(carla.Location(x=0,y=-1,  z=1.8), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=0, z=1.8), carla.Rotation(pitch=0, yaw=-110, roll=0))
}


camera_positions_infra1 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-60.000000, y=-90.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

camera_positions_infra2 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

motorycle_name_list = ['vehicle.harley-davidson.low_rider', 'vehicle.vespa.zx125', 'vehicle.kawasaki.ninja', 'vehicle.yamaha.yzf']
bicycle_name_list = ['vehicle.bh.crossbike', 'vehicle.diamondback.century', 'vehicle.gazelle.omafiets']




















"""
- Occlusions
- Low light conditions
- Crowded scenes
- Abrupt motions
- Variability in appearance
- Varying distance (very close, very far)
- Shadows and reflections
- Camera motions
- Variable camera angles
- Similarity between pedestrian and backgound
- Adverse weather conditions
- Multiple /overlapping tracks due to an a class leaving/reentering a scene
- Peds in wheelchairs, pushing strollers or carrying large objects

"""

"""
spawn_pts = 
ego = 54.6, 13.87, .61
aux1 = 33.57, 13.87, .61
infra1 = 92.25, .401.919312, .571
infra2 = 
"""
# 9225.308594, 401.919312, 571.999207""""""
time_of_the_day_list = ['Day', 'Night']
weather = ['clear', 'rainy', 'cloudy', 'wet']
vru_speed_variability = ['walking', 'jogging', 'running']
scene_variability = ['crowded', 'uncrowded', 'crossing', 'on side walk', 'occluded', 'not occluded']
# other_vru_classes = ['in wheelchair', 'pushing stroller', 'carrying large object']
Annotation_list = ['BEV instance class labels', '3D BBOX', '3D Trajectory', 'Skeletal Coordinates']
town_list = ['Town01', 'Town02', 'Town03', 'Town04', 'Town05', 'Town06', 'Town07', 'Town10HD']
