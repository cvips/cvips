import glob
import os
import sys
from cvips_config import *
from icecream import ic
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import argparse
import carla
import logging
import math
import pygame
import random
import queue
import numpy as np
# from bounding_box import create_kitti_datapoint
from constants import *
from image_converter import *
from dataexport import *
from PIL import Image


def create_directories(town, scenario):
    sub_dirs = ['BEV_instance_camera', 'calib', 'Camera_Back', 'Camera_BackLeft', 'Camera_BackRight', 'Camera_Front', 'Camera_FrontLeft', 'Camera_FrontRight', 'label', 'lidar01']
    vehicle_list = ['veh1', 'veh2',  'veh3', 'veh4', 'infra1', 'infra2']
    root_path = "type1_subtype1_normal"
    type_name = "type001_subtype0001"
    for vehicle in vehicle_list:
        scene_name = town + "_" + type_name + "_" + scenario
        for sub_dir in sub_dirs:
            dir_path = os.path.join(root_path, vehicle, sub_dir, scene_name)
            os.makedirs(dir_path, exist_ok=True)

class SynchronyModel(object):
    def __init__(self, town_name, intersection, setup, weather, time_of_the_day, crowd_level, crossing_percentage, seed_value, scenario):
        self.seed_value = seed_value
        self.weather = weather
        self.time_of_the_day = time_of_the_day
        self.world, self.init_setting, self.client, self.traffic_manager = self._make_setting()
        self.blueprint_library = self.world.get_blueprint_library()
        self.config = config[town_name][intersection][setup]
        self.crowd_level = crowd_level
        self.crossing_percentage = crossing_percentage        
        self.town_name = town_name
        self.vehicle_list = ['veh1', 'veh2',  'veh3', 'veh4', 'infra1', 'infra2']
        self.root_path = "type1_subtype1_normal"
        self.scenario = scenario
        self.scene_name = self.town_name + "_" + "type001_subtype0001" + "_" + self.scenario
        self.non_player = []
        self.actor_list = []
        self.frame = None
        self.veh1 = None
        self.veh2= None
        self.veh3 = None
        self.veh4= None
        self.infra1 = None
        self.infra2 = None
        self.captured_frame_no = 0
        self.sensors = []
        self._queues = []
        self.veh1_frames = []
        self.veh2_frames = []
        self.veh3_frames = []
        self.veh4_frames = []
        self.infra1_frames = []
        self.infra2_frames= []        
        self.veh1_depth_frames = []
        self.veh2_depth_frames = []
        self.veh3_depth_frames = []
        self.veh4_depth_frames = []
        self.infra1_depth_frames = []
        self.infra2_depth_frames= []
        self.veh1_point_cloud = None
        self.veh2_point_cloud = None
        self.veh3_point_cloud = None
        self.veh4_point_cloud = None
        self.infra1_point_cloud = None
        self.infra2_point_cloud = None
        self.veh1_lidar = None
        self.veh2_lidar = None
        self.veh3_lidar = None
        self.veh4_lidar = None
        self.infra1_lidar = None
        self.infra2_lidar = None
        self.veh1_rot = None
        self.veh2_rot2 = None
        self.veh1_cams_ext = []
        self.veh2_cams_ext = []
        self.veh3_cams_ext = []
        self.veh4_cams_ext = []
        self.infra1_cams_ext = []
        self.infra2_cams_ext = []
        self.veh1_cams_int = []
        self.veh2_cams_int = []
        self.veh3_cams_int = []
        self.veh4_cams_int = []
        self.infra1_cams_int = []
        self.infra2_cams_int = []
        self.veh1_cams, self.veh2_cams,  self.veh3_cams, self.veh4_cams, self.infra1_cams, self.infra2_cams = self._span_player()
        self._span_non_player()

    def __enter__(self):
        # set the sensor listener function
        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def current_captured_frame_num(self):
        
        label_path = os.path.join(self.root_path, 'veh1', 'label', self.scene_name)
        num_existing_data_files = len(
            [name for name in os.listdir(label_path) if name.endswith('.txt')])
        print(num_existing_data_files)
        if num_existing_data_files == 0:
            return 0
        answer = "A"
        if answer.upper() == "O":
            logging.info(
                "Resetting frame number to 0 and overwriting existing")
            # Overwrite the data
            return 0
        logging.info("Continuing recording data on frame number {}".format(
            num_existing_data_files))
        return num_existing_data_files

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        
        return data

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:                
                return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self.init_setting)
    def _span_camera(self, agent):
        pass
    def _span_agent(self, agent_list):
        pass
    def _make_setting(self):
        client = carla.Client('localhost', 2000)
        client.set_timeout(6.0)
        world = client.get_world()
        traffic_manager = client.get_trafficmanager(8000)
        traffic_manager.set_global_distance_to_leading_vehicle(3.0)
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_hybrid_physics_mode(True) 
        traffic_manager.set_hybrid_physics_radius(100)
        traffic_manager.set_respawn_dormant_vehicles(True)
        traffic_manager.set_boundaries_respawn_dormant_vehicles(21,70)
        traffic_manager.set_random_device_seed(self.seed_value)
        random.seed(self.seed_value)
        traffic_manager.set_random_device_seed(self.seed_value)
        init_setting = world.get_settings()
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05  
        settings.actor_active_distance = 70
        world.apply_settings(settings)
        if self.weather == 'clear':
            if self.time_of_the_day == 'noon':
                world.set_weather(carla.WeatherParameters.ClearNoon)
            elif self.time_of_the_day == 'sunset':
                world.set_weather(carla.WeatherParameters.ClearSunset)
            elif self.time_of_the_day == 'night':
                world.set_weather(carla.WeatherParameters.ClearNight)
        elif self.weather == 'cloudy':
            if self.time_of_the_day == 'noon':
                world.set_weather(carla.WeatherParameters.CloudyNoon)
            elif self.time_of_the_day == 'sunset':
                world.set_weather(carla.WeatherParameters.CloudySunset)
            elif self.time_of_the_day == 'night':
                world.set_weather(carla.WeatherParameters.CloudyNight)
        elif self.weather == 'wet':
            if self.time_of_the_day == 'noon':
                world.set_weather(carla.WeatherParameters.WetNoon)
            elif self.time_of_the_day == 'sunset':
                world.set_weather(carla.WeatherParameters.WetSunset)
            elif self.time_of_the_day == 'night':
                world.set_weather(carla.WeatherParameters.WetNight)
        elif self.weather == 'rainy':
            if self.time_of_the_day == 'noon':
                world.set_weather(carla.WeatherParameters.MidRainyNoon)
            elif self.time_of_the_day == 'sunset':
                world.set_weather(carla.WeatherParameters.MidRainSunset)
            elif self.time_of_the_day == 'night':
                world.set_weather(carla.WeatherParameters.MidRainyNight)
        elif self.weather == 'storm':
            world.set_weather(carla.WeatherParameters.DustStorm)



        return world, init_setting, client, traffic_manager

    def _span_player(self):
        """create our target vehicle"""
        # lights =  carla.VehicleLightState.NONE
        lights = carla.VehicleLightState(carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam)
        # vehicle.set_light_state(current_lights)
        # lights.high_beam = True
        # lights.position = True

        veh1_bp = self.blueprint_library.filter("model3")[0]
        veh1_bp.set_attribute('role_name', 'hero' )
        veh1_transform = self.config['veh1_pose']
        # print(veh1_transform)
        # veh1_transform = carla.Transform(carla.Location(x=-49.382700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
        # veh1_transform = carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
        veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
        veh1.set_autopilot(True, self.traffic_manager.get_port())
        if self.time_of_the_day == 'night':
            veh1.set_light_state(lights)  # Turn on the lights for veh1
        # breakpoint()
        # veh2_loc =  # 5 (vehicle length) + 2 (gap)
        # veh2_transform = carla.Transform(carla.Location(x=-49.642700, y=-41.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
        veh2_transform = self.config['veh2_pose']
        veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
        veh2_bp.set_attribute('role_name', 'second_vehicle')
        veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
        veh2.set_autopilot(True, self.traffic_manager.get_port())
        if self.time_of_the_day == 'night':
            veh2.set_light_state(lights)  # Turn on the lights for veh2

        veh3_bp = self.blueprint_library.filter("model3")[0]
        veh3_bp.set_attribute('role_name', 'fourth_vehicle' )
        # veh3_transform = carla.Transform(carla.Location(x=-90.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
        veh3_transform = self.config['veh3_pose']
        veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
        veh3.set_autopilot(True, self.traffic_manager.get_port())
        if self.time_of_the_day == 'night':
            veh3.set_light_state(lights)  # Turn on the lights for veh3
        # veh4_transform = carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
        veh4_transform = self.config['veh4_pose']
        veh4_bp = self.blueprint_library.filter("model3")[0] 
        veh4_bp.set_attribute('role_name', 'fourth_vehicle')
        veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
        veh4.set_autopilot(True, self.traffic_manager.get_port())
        if self.time_of_the_day == 'night':
            veh4.set_light_state(lights)  # Turn on the lights for veh4
        veh1_cams, veh2_cams, veh3_cams, veh4_cams, infra1_cams, infra2_cams = self._span_sensor(veh1, veh2, veh3, veh4)
        self.actor_list.append(veh1)
        self.actor_list.append(veh2)
        self.actor_list.append(veh3)
        self.actor_list.append(veh4)
        self.veh1 = veh1
        self.veh2 = veh2
        self.veh3 = veh3
        self.veh4 = veh4

        return tuple(veh1_cams), tuple(veh2_cams), tuple(veh3_cams), tuple(veh4_cams), tuple(infra1_cams), tuple(infra2_cams)

    def _span_sensor(self, player, player2, player3, player4):
        """create camera, depth camera and lidar and attach to the target vehicle"""

        camera_list, camera2_list, camera3_list, camera4_list, rsu_camera_list, rsuc_camera_list = [], [], [], [], [], []
        for camera_name, transform in camera_positions_vehicle.items():
            camera_bp = self.blueprint_library.find('sensor.camera.rgb')
            camera_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT))    
            camera_d_bp = self.blueprint_library.find('sensor.camera.semantic_segmentation')            
            camera_d_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_d_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT))      
            if camera_name == 'Camera_Back':
                camera_bp.set_attribute('fov', '110')
                camera_d_bp.set_attribute('fov', '110')
                self.veh1_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.veh1_cams_int.append(calc_intrinsic_params(110))
                camera_bp.set_attribute('fov', '110')
                camera_d_bp.set_attribute('fov', '110')
            # transform_d =  carla.Transform(carla.Location(x=0, z=50), carla.Rotation(pitch=270, yaw=0, roll=0))
            spawned_camera = self.world.spawn_actor(camera_bp, transform, attach_to=player, attachment_type=carla.AttachmentType.Rigid)
            spawned_camera_d = self.world.spawn_actor(camera_d_bp,transform, attach_to=player,attachment_type=carla.AttachmentType.Rigid)
            camera_list.append(spawned_camera)
            self.actor_list.append(spawned_camera)
            self.actor_list.append(spawned_camera_d)
            self.sensors.append(spawned_camera)
            self.sensors.append(spawned_camera_d)





        lidar_bp = self.blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range', '200')
        lidar_bp.set_attribute('rotation_frequency', '20')
        lidar_bp.set_attribute('upper_fov', '2')
        lidar_bp.set_attribute('lower_fov', '-24.8')
        lidar_bp.set_attribute('points_per_second', '2560000')
        lidar_bp.set_attribute('channels', '64')
        lidar_bp.set_attribute('horizontal_fov', '360')
        lidar_bp.set_attribute('dropoff_general_rate', '0.1')
        lidar_location = carla.Location(0, 0, 1.8)
        lidar_rotation = carla.Rotation(0, 0, 0)
        lidar_transform = carla.Transform(lidar_location, lidar_rotation)
        my_lidar = self.world.spawn_actor(lidar_bp, lidar_transform, attach_to=player)
        self.veh1_lidar = my_lidar
        self.actor_list.append(my_lidar)
        self.sensors.append(my_lidar)

        for camera_name, transform in camera_positions_vehicle.items():
            camera_bp2 = self.blueprint_library.find('sensor.camera.rgb')
            camera_bp2.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_bp2.set_attribute('image_size_y', str(WINDOW_HEIGHT))    
            camera_d_bp2 = self.blueprint_library.find('sensor.camera.semantic_segmentation')
            camera_d_bp2.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_d_bp2.set_attribute('image_size_y', str(WINDOW_HEIGHT))      
            if camera_name == 'Camera_Back':
                camera_bp2.set_attribute('fov', '110')
                camera_d_bp2.set_attribute('fov', '110')
                self.veh2_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.veh2_cams_int.append(calc_intrinsic_params(70))
                camera_bp2.set_attribute('fov', '70')
                camera_d_bp2.set_attribute('fov', '70')

            spawned_camera2 = self.world.spawn_actor(camera_bp2, transform, attach_to=player2, attachment_type=carla.AttachmentType.Rigid)
            spawned_camera_d2 = self.world.spawn_actor(camera_d_bp2,transform, attach_to=player2,attachment_type=carla.AttachmentType.Rigid)
            camera2_list.append(spawned_camera2)
            self.actor_list.append(spawned_camera2)
            self.actor_list.append(spawned_camera_d2)
            self.sensors.append(spawned_camera2)
            self.sensors.append(spawned_camera_d2)








        
        lidar_bp2 = self.blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp2.set_attribute('range', '200')
        lidar_bp2.set_attribute('rotation_frequency', '20')
        lidar_bp2.set_attribute('upper_fov', '2')
        lidar_bp2.set_attribute('lower_fov', '-24.8')
        lidar_bp2.set_attribute('points_per_second', '2560000')
        lidar_bp2.set_attribute('channels', '64')
        lidar_bp2.set_attribute('horizontal_fov', '360')
        lidar_bp2.set_attribute('dropoff_general_rate', '0.1')
        lidar2_location = carla.Location(0, 0, 1.8)
        lidar2_rotation = carla.Rotation(0, 0, 0)
        lidar2_transform = carla.Transform(lidar2_location, lidar2_rotation)
        my_lidar2 = self.world.spawn_actor(lidar_bp2, lidar2_transform, attach_to=player2)
        self.veh2_lidar = my_lidar2
        self.actor_list.append(my_lidar2)
        self.sensors.append(my_lidar2)







        # For player3
        for camera_name, transform in camera_positions_vehicle.items():
            camera_bp3 = self.blueprint_library.find('sensor.camera.rgb')
            camera_bp3.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_bp3.set_attribute('image_size_y', str(WINDOW_HEIGHT))    
            camera_d_bp3 = self.blueprint_library.find('sensor.camera.semantic_segmentation')
            camera_d_bp3.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_d_bp3.set_attribute('image_size_y', str(WINDOW_HEIGHT))      
            if camera_name == 'Camera_Back':
                camera_bp3.set_attribute('fov', '110')
                camera_d_bp3.set_attribute('fov', '110')
                self.veh3_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.veh3_cams_int.append(calc_intrinsic_params(70))
                camera_bp3.set_attribute('fov', '70')
                camera_d_bp3.set_attribute('fov', '70')

            spawned_camera3 = self.world.spawn_actor(camera_bp3, transform, attach_to=player3, attachment_type=carla.AttachmentType.Rigid)
            spawned_camera_d3 = self.world.spawn_actor(camera_d_bp3,transform, attach_to=player3,attachment_type=carla.AttachmentType.Rigid)
            camera3_list.append(spawned_camera3)
            self.actor_list.append(spawned_camera3)
            self.actor_list.append(spawned_camera_d3)
            self.sensors.append(spawned_camera3)
            self.sensors.append(spawned_camera_d3)

        lidar_bp3 = self.blueprint_library.find('sensor.lidar.ray_cast')
        
        lidar_bp3.set_attribute('range', '200')
        lidar_bp3.set_attribute('rotation_frequency', '20')
        lidar_bp3.set_attribute('upper_fov', '2')
        lidar_bp3.set_attribute('lower_fov', '-24.8')
        lidar_bp3.set_attribute('points_per_second', '2560000')
        lidar_bp3.set_attribute('channels', '64')
        lidar_bp3.set_attribute('horizontal_fov', '360')
        lidar_bp3.set_attribute('dropoff_general_rate', '0.1')
        lidar3_location = carla.Location(0, 0, 1.8)
        lidar3_rotation = carla.Rotation(0, 0, 0)
        lidar3_transform = carla.Transform(lidar3_location, lidar3_rotation)
        my_lidar3 = self.world.spawn_actor(lidar_bp3, lidar3_transform, attach_to=player3)
        self.veh3_lidar = my_lidar3
        self.actor_list.append(my_lidar3)
        self.sensors.append(my_lidar3)

        # For player4
        for camera_name, transform in camera_positions_vehicle.items():
            camera_bp4 = self.blueprint_library.find('sensor.camera.rgb')
            camera_bp4.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_bp4.set_attribute('image_size_y', str(WINDOW_HEIGHT))    
            camera_d_bp4 = self.blueprint_library.find('sensor.camera.semantic_segmentation')
            camera_d_bp4.set_attribute('image_size_x', str(WINDOW_WIDTH))
            camera_d_bp4.set_attribute('image_size_y', str(WINDOW_HEIGHT))      
            if camera_name == 'Camera_Back':
                camera_bp4.set_attribute('fov', '110')
                camera_d_bp4.set_attribute('fov', '110')
                self.veh4_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.veh4_cams_int.append(calc_intrinsic_params(70))
                camera_bp4.set_attribute('fov', '70')
                camera_d_bp4.set_attribute('fov', '70')

            spawned_camera4 = self.world.spawn_actor(camera_bp4, transform, attach_to=player4, attachment_type=carla.AttachmentType.Rigid)
            spawned_camera_d4 = self.world.spawn_actor(camera_d_bp4,transform, attach_to=player4,attachment_type=carla.AttachmentType.Rigid)
            camera4_list.append(spawned_camera4)
            self.actor_list.append(spawned_camera4)
            self.actor_list.append(spawned_camera_d4)
            self.sensors.append(spawned_camera4)
            self.sensors.append(spawned_camera_d4)

        lidar_bp4 = self.blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp4.set_attribute('range', '200')
        lidar_bp4.set_attribute('rotation_frequency', '20')
        lidar_bp4.set_attribute('upper_fov', '2')
        lidar_bp4.set_attribute('lower_fov', '-24.8')
        lidar_bp4.set_attribute('points_per_second', '2560000')
        lidar_bp4.set_attribute('channels', '64')
        lidar_bp4.set_attribute('horizontal_fov', '360')
        lidar_bp4.set_attribute('dropoff_general_rate', '0.1')
        lidar4_location = carla.Location(0, 0, 1.8)
        lidar4_rotation = carla.Rotation(0, 0, 0)
        lidar4_transform = carla.Transform(lidar4_location, lidar4_rotation)

        my_lidar4 = self.world.spawn_actor(lidar_bp4, lidar4_transform, attach_to=player4)
        self.veh4_lidar = my_lidar4
        self.actor_list.append(my_lidar4)
        self.sensors.append(my_lidar4)











        for camera_name, transform in camera_positions_infra1.items():
            infra_pose = self.config['infra1_pose']
            rsu_camera_transform = carla.Transform(infra_pose.location, transform.rotation)
            rsu_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
            rsu_camera_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            rsu_camera_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT))
            rsu_camera_d_bp = self.blueprint_library.find('sensor.camera.semantic_segmentation')
            rsu_camera_d_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            rsu_camera_d_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT)) 
            if camera_name == 'Camera_Back':
                rsu_camera_bp.set_attribute('fov', '110')
                rsu_camera_d_bp.set_attribute('fov', '110')
                self.infra1_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.infra1_cams_int.append(calc_intrinsic_params(70))
                rsu_camera_bp.set_attribute('fov', '70')
                rsu_camera_d_bp.set_attribute('fov', '70')

            rsu_spawned_camera = self.world.spawn_actor(rsu_camera_bp, rsu_camera_transform)
            rsu_spawned_camera_d = self.world.spawn_actor(rsu_camera_d_bp, rsu_camera_transform)
            rsu_camera_list.append(rsu_spawned_camera)
            # self.road = rsu_spawned_camera 
            self.actor_list.append(rsu_spawned_camera)
            self.actor_list.append(rsu_spawned_camera_d)
            self.sensors.append(rsu_spawned_camera)
            self.sensors.append(rsu_spawned_camera_d)
        rsu_lidar_bp = self.blueprint_library.find('sensor.lidar.ray_cast')
        rsu_lidar_bp.set_attribute('channels', str(64))
        rsu_lidar_bp.set_attribute('points_per_second', str(2560000))
        rsu_lidar_bp.set_attribute('rotation_frequency', str(20))
        rsu_lidar_bp.set_attribute('range', str(200))
        rsu_lidar_bp.set_attribute('dropoff_general_rate', '0.1')
        rsu_lidar_bp.set_attribute('horizontal_fov', '360')
        rsu_lidar_bp.set_attribute('upper_fov', str(0))
        rsu_lidar_bp.set_attribute('lower_fov', str(-40))
        # rsu_lidar_location = carla.Location(-65, 5, 4)
        # rsu_lidar_rotation = carla.Rotation(0, 0, 0)
        rsu_lidar_transform = self.config['infra1_pose']
        rsu_lidar = self.world.spawn_actor(rsu_lidar_bp, rsu_lidar_transform)   
        self.actor_list.append(rsu_lidar)
        self.sensors.append(rsu_lidar)
        self.infra1_lidar = rsu_lidar

        for camera_name, transform in camera_positions_infra2.items():
            infra_pose = self.config['infra2_pose']
            rsuc_camera_transform = carla.Transform(infra_pose.location, transform.rotation)
            rsuc_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
            rsuc_camera_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            rsuc_camera_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT))
            rsuc_camera_d_bp = self.blueprint_library.find('sensor.camera.semantic_segmentation')
            rsuc_camera_d_bp.set_attribute('image_size_x', str(WINDOW_WIDTH))
            rsuc_camera_d_bp.set_attribute('image_size_y', str(WINDOW_HEIGHT)) 
            if camera_name == 'Camera_Back':
                rsuc_camera_bp.set_attribute('fov', '110')
                rsuc_camera_d_bp.set_attribute('fov', '110')
                self.infra2_cams_int.append(calc_intrinsic_params(110))
            else: 
                self.infra2_cams_int.append(calc_intrinsic_params(70))
                rsuc_camera_bp.set_attribute('fov', '70')
                rsuc_camera_d_bp.set_attribute('fov', '70')
            rsuc_spawned_camera = self.world.spawn_actor(rsuc_camera_bp, rsuc_camera_transform)
            rsuc_spawned_camera_d = self.world.spawn_actor(rsuc_camera_d_bp, rsuc_camera_transform)
            rsuc_camera_list.append(rsuc_spawned_camera)
            self.actor_list.append(rsuc_spawned_camera)
            self.actor_list.append(rsuc_spawned_camera_d)
            self.sensors.append(rsuc_spawned_camera)
            self.sensors.append(rsuc_spawned_camera_d)
        rsuc_lidar_bp = self.blueprint_library.find('sensor.lidar.ray_cast')
        rsuc_lidar_bp.set_attribute('channels', str(64))
        rsuc_lidar_bp.set_attribute('points_per_second', str(2560000))
        rsuc_lidar_bp.set_attribute('rotation_frequency', str(20))
        rsuc_lidar_bp.set_attribute('range', str(200))
        rsuc_lidar_bp.set_attribute('dropoff_general_rate', '0.1')
        rsuc_lidar_bp.set_attribute('horizontal_fov', '360')
        rsuc_lidar_bp.set_attribute('upper_fov', str(0))
        rsuc_lidar_bp.set_attribute('lower_fov', str(-40))
        # rsuc_lidar_location = carla.Location(-36, 10, 4)
        # rsuc_lidar_rotation = carla.Rotation(0, 0, 0)
        rsuc_lidar_transform = self.config['infra2_pose']
        rsuc_lidar = self.world.spawn_actor(rsuc_lidar_bp, rsuc_lidar_transform)
        self.actor_list.append(rsuc_lidar)
        self.sensors.append(rsuc_lidar)
        self.road, self.roadc = rsu_camera_list, rsuc_camera_list 
        self.infra2_lidar = rsuc_lidar
        return camera_list,camera2_list, camera3_list, camera4_list, rsu_camera_list, rsuc_camera_list

    def _span_non_player(self):
        lights = carla.VehicleLightState(carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam)
        vehicles =self.world.get_blueprint_library().filter(FILTERV)
        # for vehicle in vehicles:
        veh1_pose = self.config['veh1_pose']
        veh2_pose = self.config['veh2_pose']
        infra1_pose = self.config['infra1_pose']
        infra2_pose = self.config['infra2_pose']

        # vehicle_1_spawn_point = carla.Transform(carla.Location(x=-5.07157715, y=5.0, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
        # # breakpoint()
        # vehicle_1_blueprint = random.choice(self.blueprint_library.filter(FILTERV))
        # if vehicle_1_blueprint.has_attribute('color'):
        #     color = random.choice(vehicle_1_blueprint.get_attribute('color').recommended_values)
        #     vehicle_1_blueprint.set_attribute('color', color)
        # if vehicle_1_blueprint.has_attribute('driver_id'):
        #     driver_id = random.choice(vehicle_1_blueprint.get_attribute('driver_id').recommended_values)
        #     vehicle_1_blueprint.set_attribute('driver_id', driver_id)
        # vehicle_1_blueprint.set_attribute('role_name', 'autopilot')
        
        
        # vehicle_2_spawn_point=carla.Transform(carla.Location(x=-48.87609375, y=-41.15295776, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
        # vehicle_2_blueprint = random.choice(self.blueprint_library.filter(FILTERV))
        # if vehicle_2_blueprint.has_attribute('color'):
        #     color = random.choice(vehicle_2_blueprint.get_attribute('color').recommended_values)
        #     vehicle_2_blueprint.set_attribute('color', color)
        # if vehicle_2_blueprint.has_attribute('driver_id'):
        #     driver_id = random.choice(vehicle_2_blueprint.get_attribute('driver_id').recommended_values)
        #     vehicle_2_blueprint.set_attribute('driver_id', driver_id)
        # vehicle_2_blueprint.set_attribute('role_name', 'autopilot')
        
        blueprints = self.world.get_blueprint_library().filter(FILTERV)
        blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
        blueprints = [x for x in blueprints if not x.id.endswith('isetta')]
        blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
        blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
        blueprints = [x for x in blueprints if not x.id.endswith('t2')]
        blueprints = sorted(blueprints, key=lambda bp: bp.id)
        
        spawn_points_all = self.world.get_map().get_spawn_points()
        #number_of_spawn_points_all = len(spawn_points_all)
        spawn_points=[]
        for n, transform in enumerate(spawn_points_all):
             if (transform.location.x>infra1_pose.location.x-60) and (transform.location.x<infra1_pose.location.x+60) and (transform.location.y<infra1_pose.location.y+60) and (transform.location.y>infra1_pose.location.y-60):
               spawn_points.append(spawn_points_all[n])
        number_of_spawn_points = len(spawn_points)
        if NUM_OF_VEHICLES <= number_of_spawn_points:
            random.shuffle(spawn_points)
            number_of_vehicles = NUM_OF_VEHICLES
        elif NUM_OF_VEHICLES > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, NUM_OF_VEHICLES, number_of_spawn_points)
            number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor

        batch = []
        # batch.append(SpawnActor(vehicle_1_blueprint, vehicle_1_spawn_point))
        # batch.append(SpawnActor(vehicle_2_blueprint, vehicle_2_spawn_point))
        for n, transform in enumerate(spawn_points):
            if n >= number_of_vehicles:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot
            batch.append(SpawnActor(blueprint, transform))

        vehicles_id = []
        for response in self.client.apply_batch_sync(batch):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_id.append(response.actor_id)
        vehicle_actors = self.world.get_actors(vehicles_id)
        self.non_player.extend(vehicle_actors)
        self.actor_list.extend(vehicle_actors)
        # self.traffic_manager.set_traffic_laws(True)
        for i in vehicle_actors:
            i.set_autopilot(True, self.traffic_manager.get_port())
            i.set_light_state(lights)
        


        blueprintsWalkers = self.world.get_blueprint_library().filter(FILTERW)
        blueprintsWalkers = [bp for bp in blueprintsWalkers if bp.id not in ['walker.pedestrian.0011',  'walker.pedestrian.0009', 'walker.pedestrian.0014',  'walker.pedestrian.0012', 'walker.pedestrian.0048', 'walker.pedestrian.0049']]  
        percentagePedestriansRunning = 0.1  # how many pedestrians will run
        percentagePedestriansCrossing = 0.1  # how many pedestrians will walk through the road
        # 1. take all the random locations to spawn
        spawn_points = []
        for i in range(NUM_OF_WALKERS):
            spawn_point = carla.Transform()
            loc = self.world.get_random_location_from_navigation()
            while (loc.x>infra1_pose.location.x+30) or (loc.x<infra1_pose.location.x-30) or (loc.y<infra1_pose.location.y-30) or (loc.y>infra1_pose.location.y+30):
                loc = self.world.get_random_location_from_navigation()
            if (loc != None):
                spawn_point.location = loc
                spawn_points.append(spawn_point)
        # 2. we spawn the walker object
        batch = []
        walker_speed = []
        # breakpoint()
        for spawn_point in spawn_points:
            walker_bp = random.choice(blueprintsWalkers)
            # set as not invincible
            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')
            # set the max speed
            if walker_bp.has_attribute('speed'):
                if (random.random() > percentagePedestriansRunning):
                    # walking
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                else:
                    # running
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
            else:
                print("Walker has no speed")
                walker_speed.append(0.0)
            batch.append(SpawnActor(walker_bp, spawn_point))
        results = self.client.apply_batch_sync(batch, True)
        walker_speed2 = []
        walkers_list = []
        all_id = []
        walkers_id = []
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list.append({"id": results[i].actor_id})
                walker_speed2.append(walker_speed[i])
        walker_speed = walker_speed2
        # 3. we spawn the walker controller
        batch = []
        walker_controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')
        for i in range(len(walkers_list)):
            batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
        results = self.client.apply_batch_sync(batch, True)
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list[i]["con"] = results[i].actor_id
        # 4. we put altogether the walkers and controllers id to get the objects from their id
        for i in range(len(walkers_list)):
            all_id.append(walkers_list[i]["con"])
            all_id.append(walkers_list[i]["id"])
        all_actors = self.world.get_actors(all_id)

        for i in range(len(walkers_list)):
            walkers_id.append(walkers_list[i]["id"])
        walker_actors = self.world.get_actors(walkers_id)
        self.non_player.extend(walker_actors)
        self.actor_list.extend(all_actors)
        self.world.tick()
        # breakpoint()
        # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # set how many pedestrians can cross the road
        self.world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
        for i in range(0, len(all_id), 2):
            # start walker
            all_actors[i].start()
            # set walk to random point
            all_actors[i].go_to_location(self.world.get_random_location_from_navigation())
            # max speed
            all_actors[i].set_max_speed(float(walker_speed[int(i / 2)]))
        # breakpoint()

        print('spawned %d walkers and %d vehicles, press Ctrl+C to exit.' % (len(walkers_id), len(vehicles_id)))
        # """create autonomous vehicles and people"""
        # # breakpoint()
        # # lights =  carla.VehicleLightState.NONE
        # lights = carla.VehicleLightState(carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam)
        # vehicles =self.world.get_blueprint_library().filter(FILTERV)
        # # for vehicle in vehicles:       
    
        # veh1_pose = self.config['veh1_pose']
        # veh2_pose = self.config['veh2_pose']
        # infra1_pose = self.config['infra1_pose']
        # infra2_pose = self.config['infra2_pose']
        # # vehicle_1_spawn_point = carla.Transform(carla.Location(x=veh1_pose.location.x+65.07157715, y=veh1_pose.location.y-5.0, z=0.600000), carla.Rotation(pitch=veh1_pose.rotation.pitch, yaw=veh1_pose.rotation.yaw, roll=veh1_pose.rotation.roll))
        # # # breakpoint()
        # # vehicle_1_blueprint = random.choice(self.blueprint_library.filter(FILTERV))
        # # if vehicle_1_blueprint.has_attribute('color'):
        # #     color = random.choice(vehicle_1_blueprint.get_attribute('color').recommended_values)
        # #     vehicle_1_blueprint.set_attribute('color', color)
        # # if vehicle_1_blueprint.has_attribute('driver_id'):
        # #     driver_id = random.choice(vehicle_1_blueprint.get_attribute('driver_id').recommended_values)
        # #     vehicle_1_blueprint.set_attribute('driver_id', driver_id)
        # # vehicle_1_blueprint.set_attribute('role_name', 'autopilot')
        
        
        # # vehicle_2_spawn_point=carla.Transform(carla.Location(x=veh2_pose.location.x-10.07157715, y=veh2_pose.location.y-5.0, z=0.600000), carla.Rotation(pitch=veh2_pose.rotation.pitch, yaw=veh2_pose.rotation.yaw, roll=veh2_pose.rotation.roll))
        # # vehicle_2_blueprint = random.choice(self.blueprint_library.filter(FILTERV))
        # # if vehicle_2_blueprint.has_attribute('color'):
        # #     color = random.choice(vehicle_2_blueprint.get_attribute('color').recommended_values)
        # #     vehicle_2_blueprint.set_attribute('color', color)
        # # if vehicle_2_blueprint.has_attribute('driver_id'):
        # #     driver_id = random.choice(vehicle_2_blueprint.get_attribute('driver_id').recommended_values)
        # #     vehicle_2_blueprint.set_attribute('driver_id', driver_id)
        # # vehicle_2_blueprint.set_attribute('role_name', 'autopilot')
        
        # blueprints = self.world.get_blueprint_library().filter(FILTERV)
        # blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
        # blueprints = [x for x in blueprints if not x.id.endswith('isetta')]
        # blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
        # blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
        # blueprints = [x for x in blueprints if not x.id.endswith('t2')]
        # blueprints = sorted(blueprints, key=lambda bp: bp.id)
        
        # spawn_points_all = self.world.get_map().get_spawn_points()
        # #number_of_spawn_points_all = len(spawn_points_all)
        # spawn_points=[]
        # for n, transform in enumerate(spawn_points_all): 
        #     # print(transform.location.x, transform.location.y, infra1_pose.location.x, infra1_pose.location.y)           
        #     if (transform.location.x>infra1_pose.location.x-100) and (transform.location.x<infra1_pose.location.x+100) and (transform.location.y<infra1_pose.location.y+100) and (transform.location.y>infra1_pose.location.y-100):
        #         spawn_points.append(spawn_points_all[n])
        # # breakpoint()
        # number_of_spawn_points = len(spawn_points)
        # # print(number_of_spawn_points)
        # if NUM_OF_VEHICLES <= number_of_spawn_points:
        #     random.shuffle(spawn_points)
        #     number_of_vehicles = NUM_OF_VEHICLES
        # elif NUM_OF_VEHICLES > number_of_spawn_points:
        #     msg = 'requested %d vehicles, but could only find %d spawn points'
        #     logging.warning(msg, NUM_OF_VEHICLES, number_of_spawn_points)
        #     number_of_vehicles = number_of_spawn_points

        # # @todo cannot import these directly.
        # SpawnActor = carla.command.SpawnActor

        # batch = []
        # # batch.append(SpawnActor(vehicle_1_blueprint, vehicle_1_spawn_point))
        # # batch.append(SpawnActor(vehicle_2_blueprint, vehicle_2_spawn_point))
        # for n, transform in enumerate(spawn_points):
        #     if n >= number_of_vehicles:
        #         break
        #     blueprint = random.choice(blueprints)
        #     if blueprint.has_attribute('color'):
        #         color = random.choice(blueprint.get_attribute('color').recommended_values)
        #         blueprint.set_attribute('color', color)
        #     if blueprint.has_attribute('driver_id'):
        #         driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
        #         blueprint.set_attribute('driver_id', driver_id)
        #     blueprint.set_attribute('role_name', 'autopilot')

        #     # spawn the cars and set their autopilot
        #     batch.append(SpawnActor(blueprint, transform))

        # vehicles_id = []
        # for response in self.client.apply_batch_sync(batch):
        #     if response.error:
        #         logging.error(response.error)
        #     else:
        #         vehicles_id.append(response.actor_id)
        # vehicle_actors = self.world.get_actors(vehicles_id)
        # self.non_player.extend(vehicle_actors)
        # self.actor_list.extend(vehicle_actors)
        # # self.traffic_manager.set_traffic_laws(True)
        # for i in vehicle_actors:
        #     i.set_autopilot(True, self.traffic_manager.get_port())
        #     if self.time_of_the_day == 'night':
        #         i.set_light_state(lights)


        # blueprintsWalkers = self.world.get_blueprint_library().filter(FILTERW)
        # blueprintsWalkers = [bp for bp in blueprintsWalkers if bp.id not in ['walker.pedestrian.0011',  'walker.pedestrian.0009', 'walker.pedestrian.0014',  'walker.pedestrian.0012', 'walker.pedestrian.0048', 'walker.pedestrian.0049']]  
        # percentagePedestriansRunning = 0.1 # how many pedestrians will run
        # percentagePedestriansCrossing = 0.1  # how many pedestrians will walk through the road
        # # 1. take all the random locations to spawn
        # spawn_points = []
        # for i in range(NUM_OF_WALKERS):
        #     spawn_point = carla.Transform()
        #     loc = self.world.get_random_location_from_navigation()
        #     while (transform.location.x>infra1_pose.location.x-100) and (transform.location.x<infra1_pose.location.x+100) and (transform.location.y<infra1_pose.location.y+100) and (transform.location.y>infra1_pose.location.y-100):
        #         loc = self.world.get_random_location_from_navigation()
        #     if (loc != None):
        #         spawn_point.location = loc
        #         spawn_points.append(spawn_point)
        # # 2. we spawn the walker object
        # batch = []
        # walker_speed = []
        # # breakpoint()
        # for spawn_point in spawn_points:
        #     walker_bp = random.choice(blueprintsWalkers)
        #     # set as not invincible
        #     if walker_bp.has_attribute('is_invincible'):
        #         walker_bp.set_attribute('is_invincible', 'false')
        #     # set the max speed
        #     if walker_bp.has_attribute('speed'):
        #         if (random.random() > percentagePedestriansRunning):
        #             # walking
        #             walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
        #         else:
        #             # running
        #             walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
        #     else:
        #         print("Walker has no speed")
        #         walker_speed.append(0.0)
        #     batch.append(SpawnActor(walker_bp, spawn_point))
        # results = self.client.apply_batch_sync(batch, True)
        # walker_speed2 = []
        # walkers_list = []
        # all_id = []
        # walkers_id = []
        # for i in range(len(results)):
        #     if results[i].error:
        #         logging.error(results[i].error)
        #     else:
        #         walkers_list.append({"id": results[i].actor_id})
        #         walker_speed2.append(walker_speed[i])
        # walker_speed = walker_speed2
        # # 3. we spawn the walker controller
        # batch = []
        # walker_controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')
        # for i in range(len(walkers_list)):
        #     batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
        # results = self.client.apply_batch_sync(batch, True)
        # for i in range(len(results)):
        #     if results[i].error:
        #         logging.error(results[i].error)
        #     else:
        #         walkers_list[i]["con"] = results[i].actor_id
        # # 4. we put altogether the walkers and controllers id to get the objects from their id
        # for i in range(len(walkers_list)):
        #     all_id.append(walkers_list[i]["con"])
        #     all_id.append(walkers_list[i]["id"])
        # all_actors = self.world.get_actors(all_id)

        # for i in range(len(walkers_list)):
        #     walkers_id.append(walkers_list[i]["id"])
        # walker_actors = self.world.get_actors(walkers_id)
        # self.non_player.extend(walker_actors)
        # self.actor_list.extend(all_actors)
        # self.world.tick()
        # # breakpoint()
        # # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # # set how many pedestrians can cross the road
        # self.world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
        # for i in range(0, len(all_id), 2):
        #     # start walker
        #     all_actors[i].start()
        #     # set walk to random point
        #     all_actors[i].go_to_location(self.world.get_random_location_from_navigation())
        #     # max speed
        #     all_actors[i].set_max_speed(float(walker_speed[int(i / 2)]))
        # # breakpoint()

        # print('spawned %d walkers and %d vehicles, press Ctrl+C to exit.' % (len(walkers_id), len(vehicles_id)))
        # breakpoint()




    def _save_training_files(self, agent_vel_list, image_list, label_list, lidar_data_list, calib_list, depth_image_list):
        """ Save data in Kitti dataset format """
        print("saving files in Kitti dataset format")
        logging.info("Attempting to save at frame no: {}".format(self.captured_frame_no))    
        # breakpoint()
        for veh_idx,vehicle in enumerate(self.vehicle_list):   
            # print(vehicle)        
            scene_name =self.scene_name
            # breakpoint()
            for img_idx, cam in enumerate(list(camera_positions_vehicle.keys())):
                img_path = os.path.join(self.root_path, vehicle, cam, scene_name)
                file_name = os.path.join(img_path, scene_name+"_"+str(self.captured_frame_no).zfill(3) + '.png')
                # breakpoint()
                save_image_data(file_name, image_list[veh_idx][img_idx])
                depth_file_name = os.path.join(img_path, scene_name+"_seg_"+str(self.captured_frame_no).zfill(3) + '.png')
                # breakpoint()
                save_image_data(depth_file_name,  depth_image_list[veh_idx][img_idx], depth=True)
            lidar_path = os.path.join(self.root_path, vehicle,'lidar01', scene_name, scene_name+"_"+str(self.captured_frame_no).zfill(3) + '.npz')
            calib_path = os.path.join(self.root_path, vehicle, 'calib', scene_name, scene_name+"_"+str(self.captured_frame_no).zfill(3) + '.pkl')
            bev_path = os.path.join(self.root_path, vehicle, 'BEV_instance_camera', scene_name, scene_name+"_"+str(self.captured_frame_no).zfill(3) + '.npz')
            label_path= os.path.join(self.root_path, vehicle, 'label', scene_name, scene_name+"_"+str(self.captured_frame_no).zfill(3) + '.txt')
            save_lidar(lidar_path, lidar_data_list[veh_idx])
            save_bev(bev_path, lidar_data_list[veh_idx])
            save_calib(calib_path,calib_list[veh_idx])
            save_label(label_path, agent_vel_list[veh_idx], label_list[veh_idx])

        print(f' Data successfully saved at frame no  {self.captured_frame_no} !')


    def get_data(self, veh1_cams_int, veh1_cams_ext, veh1_pos, veh1_lidar_pos, depth_map_list):
        """ Returns a list of datapoints (labels and such) that are generated this frame together with the main image
        image """
        image_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        calib_dict = {
        'ego_to_world': None,
        'intrinsic_Camera_Back': None,
        'intrinsic_Camera_BackLeft': None,
        'intrinsic_Camera_BackRight': None,
        'intrinsic_Camera_Front': None,
        'intrinsic_Camera_FrontLeft': None,
        'intrinsic_Camera_FrontRight': None,
        'lidar_to_Camera_Back': None,
        'lidar_to_Camera_BackLeft': None,
        'lidar_to_Camera_BackRight': None,
        'lidar_to_Camera_Front': None,
        'lidar_to_Camera_FrontLeft': None,
        'lidar_to_Camera_FrontRight': None,
        'lidar_to_ego': None
        }
        # breakpoint()
        agent_dict = {
            'class': [],
            'rel_x': [],
            'rel_y': [],
            'rel_z': [],
            'length': [],
            'width': [],
            'height': [],
            'yaw': [],
            'vel_x': [],
            'vel_y': [],
            'agent_id': [],
            'pts': [],
            'visibility': [],
            'visibility_per_camera':[]
        }
        # depth_dict = {





        # }
        ego_transform =np.array(veh1_pos.get_matrix())
        lidar_transform = np.array(veh1_lidar_pos)
        calib_dict['ego_to_world'] = np.array(ego_transform)
        inv_ego_transform = np.linalg.inv(ego_transform)
        calib_dict['lidar_to_ego'] = np.dot(inv_ego_transform, lidar_transform)        
        camera_names = list(camera_positions_vehicle.keys())
        cam_intrinsic_list = []
        cam_extrinsic_list = []
        for k,cams in enumerate(veh1_cams_ext):
            intrinsic_idx = 'intrinsic_'+camera_names[k]
            extrinsic_idx = 'lidar_to_'+camera_names[k]
            intrinsic_mat = veh1_cams_int[k]
            cam_intrinsic_list.append(intrinsic_mat)
            # cam_extrinsic_list.append(extrinsic_idx)
            extrinsic_mat = np.array(cams)
            cam_extrinsic_list.append(extrinsic_mat)
            calib_dict[intrinsic_idx] = intrinsic_mat
            calib_dict[extrinsic_idx] = np.dot(np.linalg.inv(extrinsic_mat), lidar_transform)
        cls = ""
        for agent in self.non_player:
            agent_name = agent.type_id
            # breakpoint
            # if GEN_DATA:
            if ("vehicle" in agent_name and (agent_name in motorycle_name_list or agent_name in bicycle_name_list)) or ("pedestrian" in agent_name):
                # if (*  *  != 0): 
                # if (agent.bounding_box.extent.x * agent.bounding_box.extent.y * agent.bounding_box.extent.z != 0):
                    bounding_box = agent.bounding_box
                    if agent_name in motorycle_name_list:
                        cls = "motorcycle"
                        print(cls)
                        # bounding_box.extent.x = 0.68/2
                        # bounding_box.extent.y = 1.95/2
                        # bounding_box.extent.z = 1.47/2
                        # # print(agent.get_transform().location.x, agent.get_transform().location.y, agent.get_transform().location.z)
                        # # agent.bounding_box.location.x
                        # # agent.bounding_box.location.x
                        # # agent.bounding_box.location.x
                        # # agent.get_transform().location.x + agent.bounding_box.location.x*2
                        # # agent.get_transform().location.y + agent.bounding_box.location.y*2
                        # # agent.get_transform().location.z -= agent.bounding_box.location.z
                        # # agent_transform = agent.get_transform()
                        # extent = bounding_box.extent
                        # velocity = agent.get_velocity()
                        # vel_x, vel_y = velocity.x, velocity.y
                        # pts = 3    
                        # x,y,z,l,w,h,yaw = (agent.get_transform().location.x + agent.bounding_box.location.x*2), (agent.get_transform().location.y + agent.bounding_box.location.y*2), agent_transform.location.z, extent.x*2, extent.y*2, extent.z*2, agent_transform.rotation.yaw
                        # bbox_center_world = np.array([x, y, z, 1])
                        # bbox_yaw_world = yaw
                        # inv_lidar_transform = np.linalg.inv(lidar_transform) 
                        # bbox_center_ego = np.dot(inv_lidar_transform, bbox_center_world)[:3]
                        # # breakpoint()
                        # relative_yaw = bbox_yaw_world - veh1_pos.rotation.yaw
                        # rel_x = bbox_center_ego[0] #- veh1_pos.location.x
                        # rel_y = bbox_center_ego[1] #- veh1_pos.location.y
                        # rel_z = bbox_center_ego[2] #- veh1_pos.location.z
                        # # relative_yaw = yaw #- veh1_pos.rotation.yaw
                        # agent_dict['class'].append(cls)
                        # agent_dict['rel_x'].append(rel_x)
                        # agent_dict['rel_y'].append(rel_y)
                        # agent_dict['rel_z'].append(rel_z)
                        # agent_dict['length'].append(l)
                        # agent_dict['width'].append(w)
                        # agent_dict['height'].append(h)
                        # agent_dict['yaw'].append(relative_yaw)
                        # agent_dict['vel_x'].append(vel_x)
                        # agent_dict['vel_y'].append(vel_y)
                        # agent_dict['agent_id'].append(agent.id)
                        # agent_dict['pts'].append(pts)
                        # center = np.array([x,y,z])
                        # dimensions = np.array([l,w,h])       
                        # depth_arrays = [vrus_only_label_array(depth_map) for depth_map in depth_map_list]                            
                        # visibility_per_camera = [False] * len(camera_positions_vehicle)       
                        # for i, (intrinsic_mat, extrinsic_mat) in enumerate(zip(cam_intrinsic_list, cam_extrinsic_list)):
                        #     occluded = is_occluded(center, dimensions, relative_yaw, depth_arrays[i], intrinsic_mat, extrinsic_mat, image_size)
                        #     visibility_per_camera[i] = not occluded           
                        # if any(visibility_per_camera):
                        #     agent_dict['visibility'].append(True)          
                        #     agent_dict['visibility_per_camera'].append(visibility_per_camera)
                        # else:
                        #     agent_dict['visibility'].append(False)
                        #     agent_dict['visibility_per_camera'].append(visibility_per_camera)
                    elif agent_name in bicycle_name_list:
                        cls="cyclist"
                        print(cls)
                        # bounding_box.extent.x = 0.64/2
                        # bounding_box.extent.y = 1.82/2
                        # bounding_box.extent.z = 1.39/2
                        # # print(agent.get_transform().location.x, agent.get_transform().location.y, agent.get_transform().location.z)
                        # # agent.get_transform().location.x += agent.bounding_box.location.x*2
                        # # agent.get_transform().location.y += agent.bounding_box.location.y*2
                        # # agent.get_transform().location.z -= agent.bounding_box.location.z
                        # agent_transform = agent.get_transform()
                        # extent = bounding_box.extent
                        # velocity = agent.get_velocity()
                        # vel_x, vel_y = velocity.x, velocity.y
                        # pts = 3    
                        # x,y,z,l,w,h,yaw = (agent.get_transform().location.x), (agent.get_transform().location.y + 2), agent_transform.location.z, extent.x*2, extent.y*2, extent.z*2, agent_transform.rotation.yaw
                        # bbox_center_world = np.array([x, y, z, 1])
                        # bbox_yaw_world = yaw
                        # inv_lidar_transform = np.linalg.inv(lidar_transform) 
                        # bbox_center_ego = np.dot(inv_lidar_transform, bbox_center_world)[:3]
                        # # breakpoint()
                        # relative_yaw = bbox_yaw_world - veh1_pos.rotation.yaw
                        # rel_x = bbox_center_ego[0] #- veh1_pos.location.x
                        # rel_y = bbox_center_ego[1] #- veh1_pos.location.y
                        # rel_z = bbox_center_ego[2] #- veh1_pos.location.z
                        # # relative_yaw = yaw #- veh1_pos.rotation.yaw
                        # agent_dict['class'].append(cls)
                        # agent_dict['rel_x'].append(rel_x)
                        # agent_dict['rel_y'].append(rel_y)
                        # agent_dict['rel_z'].append(rel_z)
                        # agent_dict['length'].append(l)
                        # agent_dict['width'].append(w)
                        # agent_dict['height'].append(h)
                        # agent_dict['yaw'].append(relative_yaw)
                        # agent_dict['vel_x'].append(vel_x)
                        # agent_dict['vel_y'].append(vel_y)
                        # agent_dict['agent_id'].append(agent.id)
                        # agent_dict['pts'].append(pts)
                        # center = np.array([x,y,z])
                        # dimensions = np.array([l,w,h])       
                        # depth_arrays = [vrus_only_label_array(depth_map) for depth_map in depth_map_list]                            
                        # visibility_per_camera = [False] * len(camera_positions_vehicle)       
                        # for i, (intrinsic_mat, extrinsic_mat) in enumerate(zip(cam_intrinsic_list, cam_extrinsic_list)):
                        #     occluded = is_occluded(center, dimensions, relative_yaw, depth_arrays[i], intrinsic_mat, extrinsic_mat, image_size)
                        #     visibility_per_camera[i] = not occluded           
                        # if any(visibility_per_camera):
                        #     agent_dict['visibility'].append(True)          
                        #     agent_dict['visibility_per_camera'].append(visibility_per_camera)
                        # else:
                        #     agent_dict['visibility'].append(False)
                        #     agent_dict['visibility_per_camera'].append(visibility_per_camera)
                    else:
                        cls = "pedestrian"                
                    agent_transform = agent.get_transform()
                    extent = bounding_box.extent
                    velocity = agent.get_velocity()
                    vel_x, vel_y = velocity.x, velocity.y
                    pts = 3    
                    x,y,z,l,w,h,yaw = agent_transform.location.x, agent_transform.location.y, agent_transform.location.z, extent.x*2, extent.y*2, extent.z*2, agent_transform.rotation.yaw
                    bbox_center_world = np.array([x, y, z, 1])
                    bbox_yaw_world = yaw
                    inv_lidar_transform = np.linalg.inv(lidar_transform) 
                    bbox_center_ego = np.dot(inv_lidar_transform, bbox_center_world)[:3]
                    # breakpoint()
                    relative_yaw = bbox_yaw_world - veh1_pos.rotation.yaw
                    rel_x = bbox_center_ego[0] #- veh1_pos.location.x
                    rel_y = bbox_center_ego[1] #- veh1_pos.location.y
                    rel_z = bbox_center_ego[2] #- veh1_pos.location.z
                    # relative_yaw = yaw #- veh1_pos.rotation.yaw
                    agent_dict['class'].append(cls)
                    agent_dict['rel_x'].append(rel_x)
                    agent_dict['rel_y'].append(rel_y)
                    agent_dict['rel_z'].append(rel_z)
                    agent_dict['length'].append(l)
                    agent_dict['width'].append(w)
                    agent_dict['height'].append(h)
                    agent_dict['yaw'].append(relative_yaw)
                    agent_dict['vel_x'].append(vel_x)
                    agent_dict['vel_y'].append(vel_y)
                    agent_dict['agent_id'].append(agent.id)
                    agent_dict['pts'].append(pts)
                    center = np.array([x,y,z])
                    dimensions = np.array([l,w,h])       
                    depth_arrays = [vrus_only_label_array(depth_map) for depth_map in depth_map_list]                            
                    visibility_per_camera = [False] * len(camera_positions_vehicle)       
                    for i, (intrinsic_mat, extrinsic_mat) in enumerate(zip(cam_intrinsic_list, cam_extrinsic_list)):
                        occluded = is_occluded(center, dimensions, relative_yaw, depth_arrays[i], intrinsic_mat, extrinsic_mat, image_size)
                        visibility_per_camera[i] = not occluded    
                    # breakpoint()       
                    if any(visibility_per_camera):
                        agent_dict['visibility'].append(True)          
                        agent_dict['visibility_per_camera'].append(visibility_per_camera)
                    else:
                        agent_dict['visibility'].append(False)
                        agent_dict['visibility_per_camera'].append(visibility_per_camera)
        return agent_dict, calib_dict


def draw_image(surface, image, blend=False):
    array = image[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    if blend:
        image_surface.set_alpha(100)
    surface.blit(image_surface, (0, 0))


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                return True
    return False


def get_font():
    fonts = [x for x in pygame.font.get_fonts()]
    default_font = 'ubuntumono'
    font = default_font if default_font in fonts else fonts[0]
    font = pygame.font.match_font(font)
    return pygame.font.Font(font, 14)
def parse_args():
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("--root", help="root directory")
    argparser.add_argument("--town", type=str,help="Town list: Town03, Town04, Town05, Town06, Town07, Town10HD", default="Town10HD")
    argparser.add_argument("--intersection", type=str,help="intersection type 4way or 3way", default="4way")
    argparser.add_argument("--setup", type=str, help="if 4way: wnse, wsee, wwss, wwee, wwws: 3way: wwss, wsse, wwse",default="4way")
    argparser.add_argument("--weather", type=str, help="weather type: clear, wet, cloudy, rainy", default="clear")    
    argparser.add_argument("--time_of_the_day", type=str, help="time of the day: noon, sunset, night",default="noon")
    argparser.add_argument("--crowd_level", type=str, help="crowd level: low, medium, high", default="medium")
    argparser.add_argument("--crossing_percentage", help="Percentage of pedestrians crossing: eg. 0.1", type=float, default=0.1)
    # argparser.add_argument("--pedestrian_speed", help="Status of pedestrians: running, jogging, walking", default="walking")
    # argparser.add_argument("--percentage_of_kids", help="Percentage of kids in the crowd: eg. 0.05", type=float, default=0.1)
    argparser.add_argument("--seed_value", help="Seed value for random number generation", type=int, default=23)
    argparser.add_argument("--scenario", type=str, help="scenario: eg. scenario00001", default="scenario00001")
    args = argparser.parse_args()
    return args
def main():
    args = parse_args()
    # root_path = args.root
    town_name = args.town
    intersection = args.intersection
    setup = args.setup
    weather = args.weather
    time_of_the_day = args.time_of_the_day
    crowd_level = args.crowd_level
    crossing_percentage = args.crossing_percentage
    # pedestrian_speed = args.pedestrian_speed
    # percentage_of_kids = args.percentage_of_kids
    seed_value = args.seed_value
    scenario = args.scenario
    # breakpoint()
    create_directories(args.town, args.scenario)
    pygame.init()
    clock = pygame.time.Clock()
    with SynchronyModel(town_name, intersection, setup, weather, time_of_the_day, crowd_level, crossing_percentage, seed_value, scenario) as sync_mode:
        try:
            step = 5
            stop_flag = 1
            while True:
                if should_quit():
                    break
                if stop_flag == 102:
                    break
                clock.tick()                
                sensed_results = sync_mode.tick(timeout=2.0)		
                # print(f"{len(sensed_results)} sensed results")
                # breakpoint()

                #VELOCITY
                veh1_vel = (sync_mode.veh1.get_velocity().x, sync_mode.veh1.get_velocity().y)
                veh2_vel = (sync_mode.veh2.get_velocity().x, sync_mode.veh2.get_velocity().y)
                veh3_vel = (sync_mode.veh3.get_velocity().x, sync_mode.veh3.get_velocity().y)
                veh4_vel = (sync_mode.veh4.get_velocity().x, sync_mode.veh4.get_velocity().y)
                infra1_vel = (0, 0)
                infra2_vel = (0, 0)
                agent_vel_list = [veh1_vel, veh2_vel, veh3_vel, veh4_vel, infra1_vel, infra2_vel]

                veh1_image  = []
                veh2_image = []
                veh3_image = []
                veh4_image = []
                infra1_image = []      
                infra2_image = []   
                pointcloud_list = []
                veh1_depth_image = []
                veh2_depth_image = []
                veh3_depth_image = []
                veh4_depth_image = []
                infra1_depth_image = []
                infra2_depth_image = []
                snapshot = sensed_results[0]     
                sensed_results = sensed_results[1:]
                # breakpoint()
                for i in range(len(sensed_results)):
                    if i % 13 == 12:  # Exclude the 12th, 25th, 38th, 51th, etc.
                        pointcloud_list.append(sensed_results[i])

                # pointcloud_list = [sensed_results[12*i - 1] for i in range(1, len(sensed_results)//12 + 1)]
                sensed_results = [item for i, item in enumerate(sensed_results) if i % 13 != 12]
                # breakpoint()
                for i in range(len(camera_positions_vehicle)):
                    veh1_image.append(image_converter.to_rgb_array(sensed_results[2*i]))
                    veh1_depth_image.append(sensed_results[2*i+1]) 


                    sync_mode.veh1_frames.append(sensed_results[2*i])                    
                    sync_mode.veh1_depth_frames.append(sensed_results[2*i+1])   
                            
                    veh2_image.append(image_converter.to_rgb_array(sensed_results[2*(i+6)]))    
                    veh2_depth_image.append(sensed_results[2*(i+6)+1]) 
                    # breakpoint()s

                    sync_mode.veh2_frames.append(sensed_results[2*(i+6)])
                    sync_mode.veh2_depth_frames.append(sensed_results[2*(i+6)+1])

                    veh3_image.append(image_converter.to_rgb_array(sensed_results[2*(i+12)]))
                    veh3_depth_image.append(sensed_results[2*(i+12)+1])

                    sync_mode.veh3_frames.append(sensed_results[2*(i+12)])
                    sync_mode.veh3_depth_frames.append(sensed_results[2*(i+12)+1])

                    veh4_image.append(image_converter.to_rgb_array(sensed_results[2*(i+18)]))  
                    veh4_depth_image.append(sensed_results[2*(i+18)+1])

                    sync_mode.veh4_frames.append(sensed_results[2*(i+18)])
                    sync_mode.veh4_depth_frames.append(sensed_results[2*(i+18)+1])



                    # breakpoint()
                    
                    infra1_image.append(image_converter.to_rgb_array(sensed_results[2*(i+24)]))
                    infra1_depth_image.append(sensed_results[2*(i+24)+1])

                    sync_mode.infra1_frames.append(sensed_results[2*(i+24)])
                    sync_mode.infra1_depth_frames.append(sensed_results[2*(i+24)+1])

                    infra2_image.append(image_converter.to_rgb_array(sensed_results[2*(i+30)]))  
                    infra2_depth_image.append(sensed_results[2*(i+30)+1])

                    sync_mode.infra2_frames.append(sensed_results[2*(i+30)])
                    sync_mode.infra2_depth_frames.append(sensed_results[2*(i+30)+1])
                    # breakpoint()

                    sync_mode.veh1_cams_ext.append(np.mat(sync_mode.veh1_cams[i].get_transform().get_matrix()))
                    sync_mode.veh2_cams_ext.append(np.mat(sync_mode.veh2_cams[i].get_transform().get_matrix()))
                    # breakpoint()
                    sync_mode.veh3_cams_ext.append(np.mat(sync_mode.veh3_cams[i].get_transform().get_matrix()))
                    sync_mode.veh4_cams_ext.append(np.mat(sync_mode.veh4_cams[i].get_transform().get_matrix()))
                    sync_mode.infra1_cams_ext.append(np.mat(sync_mode.infra1_cams[i].get_transform().get_matrix()))
                    sync_mode.infra2_cams_ext.append(np.mat(sync_mode.infra2_cams[i].get_transform().get_matrix()))

                # breakpoint()
                veh1_pos = sync_mode.veh1.get_transform()
                veh2_pos = sync_mode.veh2.get_transform()
                veh3_pos = sync_mode.veh3.get_transform()
                veh4_pos = sync_mode.veh4.get_transform()
                infra1_pos = sync_mode.infra1_lidar.get_transform()
                infra2_pos = sync_mode.infra2_lidar.get_transform()
                # breakpoint()
                veh1_lidar_pos = sync_mode.veh1_lidar.get_transform().get_matrix()
                veh2_lidar_pos = sync_mode.veh2_lidar.get_transform().get_matrix()
                veh3_lidar_pos = sync_mode.veh3_lidar.get_transform().get_matrix()
                veh4_lidar_pos = sync_mode.veh4_lidar.get_transform().get_matrix()
                infra1_lidar_pos = sync_mode.infra1_lidar.get_transform().get_matrix()
                infra2_lidar_pos = sync_mode.infra2_lidar.get_transform().get_matrix()
                # breakpoint()
                #IMAGES, LABELS, CALIBS
                veh1_label, veh1_calib = sync_mode.get_data(sync_mode.veh1_cams_int, sync_mode.veh1_cams_ext, veh1_pos, veh1_lidar_pos, veh1_depth_image)
                # breakpoint()
                veh2_label, veh2_calib= sync_mode.get_data(sync_mode.veh2_cams_int, sync_mode.veh2_cams_ext, veh2_pos, veh2_lidar_pos,veh2_depth_image)

                veh3_label, veh3_calib = sync_mode.get_data(sync_mode.veh3_cams_int, sync_mode.veh3_cams_ext, veh3_pos, veh3_lidar_pos, veh3_depth_image)
                veh4_label, veh4_calib = sync_mode.get_data(sync_mode.veh4_cams_int, sync_mode.veh4_cams_ext, veh4_pos, veh4_lidar_pos, veh4_depth_image)

                infra1_label,infra1_calib = sync_mode.get_data(sync_mode.infra1_cams_int, sync_mode.infra1_cams_ext, infra1_pos, infra1_lidar_pos, infra1_depth_image)  
                # print("INFRA2")  
                infra2_label, infra2_calib = sync_mode.get_data(sync_mode.infra2_cams_int, sync_mode.infra2_cams_ext, infra2_pos, infra2_lidar_pos, infra2_depth_image)
                # breakpoint()
                
                image_list = [veh1_image, veh2_image, veh3_image, veh4_image, infra1_image, infra2_image]
                depth_image_list = [veh1_depth_image, veh2_depth_image, veh3_depth_image, veh4_depth_image, infra1_depth_image, infra2_depth_image]
                label_list = [veh1_label, veh2_label, veh3_label, veh4_label, infra1_label, infra2_label]
                calib_list = [veh1_calib, veh2_calib, veh3_calib, veh4_calib, infra1_calib, infra2_calib]
                # breakpoint()

                #LIDAR
                sync_mode.veh1_point_cloud = pointcloud_list[0]
                sync_mode.veh2_point_cloud = pointcloud_list[1]
                sync_mode.veh3_point_cloud = pointcloud_list[2]
                sync_mode.veh4_point_cloud = pointcloud_list[3]
                sync_mode.infra1_point_cloud = pointcloud_list[4]
                sync_mode.infra2_point_cloud  =   pointcloud_list[5]

                # breakpoint()
                veh1_data = np.copy(np.frombuffer(sync_mode.veh1_point_cloud.raw_data, dtype=np.dtype('f4')))
                veh2_data = np.copy(np.frombuffer(sync_mode.veh2_point_cloud.raw_data, dtype=np.dtype('f4')))
                veh3_data = np.copy(np.frombuffer(sync_mode.veh3_point_cloud.raw_data, dtype=np.dtype('f4')))
                veh4_data = np.copy(np.frombuffer(sync_mode.veh4_point_cloud.raw_data, dtype=np.dtype('f4')))
                infra1_data = np.copy(np.frombuffer(sync_mode.infra1_point_cloud.raw_data, dtype=np.dtype('f4')))
                infra2_data = np.copy(np.frombuffer(sync_mode.infra2_point_cloud.raw_data, dtype=np.dtype('f4')))
                # breakpoint()
                
                veh1_lidar_data = np.reshape(veh1_data, (int(veh1_data.shape[0] / 4), 4))
                veh2_lidar_data = np.reshape(veh2_data, (int(veh2_data.shape[0] / 4), 4))
                veh3_lidar_data = np.reshape(veh3_data, (int(veh3_data.shape[0] / 4), 4))
                veh4_lidar_data = np.reshape(veh4_data, (int(veh4_data.shape[0] / 4), 4))
                infra1_lidar_data = np.reshape(infra1_data, (int(infra1_data.shape[0] / 4), 4))
                infra2_lidar_data = np.reshape(infra2_data, (int(infra2_data.shape[0] / 4), 4))
                lidar_data_list = [veh1_lidar_data, veh2_lidar_data, veh3_lidar_data, veh4_lidar_data, infra1_lidar_data, infra2_lidar_data]


                sync_mode.veh1_cams_ext = []
                sync_mode.veh2_cams_ext = []
                sync_mode.veh3_cams_ext = []
                sync_mode.veh4_cams_ext = []
                sync_mode.infra1_cams_ext = []
                sync_mode.infra2_cams_ext = []
                # sync_mode.veh1_depth_frames = []
                # sync_mode.veh2_depth_frames = []
                # sync_mode.infra1_depth_frames = []
                # sync_mode.infra2_depth_frames= []
                # breakpoint()
                if  step % 2 == 0:
                    sync_mode._save_training_files(agent_vel_list,image_list, label_list, lidar_data_list, calib_list, depth_image_list) 
                    sync_mode.captured_frame_no += 1
                    stop_flag += 1
                # sync_mode.captured_frame_no += 1
                # stop_flag += 1
                print(f"step =============== {step}")
                step = step+1
                fps = round(1.0 / snapshot.timestamp.delta_seconds)
                # print(f"fps =============== {fps}")
        finally:
            print('destroying actors.')
            for actor in sync_mode.actor_list:
                actor.destroy()
            pygame.quit()
            print('done.')


if __name__ == '__main__':
    main()
