"""
This file contains all the methods responsible for saving the generated data in the correct output format.

"""

import numpy as np
import os
import sys
import glob
import logging
from utils import degrees_to_radians
import carla
import math
from numpy.linalg import pinv, inv
from PIL import Image
from constants import *
import pickle
import cv2
from icecream import ic
from image_converter import *


def project_to_image_plane(point, intrinsic_mat, extrinsic_mat, image_size):
    point_cam_space = np.dot(np.linalg.inv(extrinsic_mat), np.array([point[0], point[1], point[2], 1.0]))
    point_cam_space = [point_cam_space[1], -point_cam_space[2], point_cam_space[0]]
    point_img_space = np.dot(intrinsic_mat, point_cam_space)
    point_img_space /= point_img_space[2]
    u,v = int(point_img_space[0]), int(point_img_space[1])
    if not (0 <= u < image_size[0] and 0 <= v < image_size[1]):
        return None
    return u, v



def get_bbox_corners(center, dimensions, yaw):
    l, w, h = dimensions
    dx = l / 2
    dy = w / 2
    dz = h / 2
    corners = np.array([
        [dx, dy, -dz], [dx, -dy, -dz], [-dx, -dy, -dz], [-dx, dy, -dz],
        [dx, dy, dz], [dx, -dy, dz], [-dx, -dy, dz], [-dx, dy, dz]
    ])

    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    R = np.array([
        [cos_yaw, -sin_yaw, 0],
        [sin_yaw, cos_yaw, 0],
        [0, 0, 1]
    ])
    corners_rotated = np.dot(corners, R.T)
    corners_global = corners_rotated + center    
    return corners_global

def get_image_point(loc,K, transform):
    inv_transform = np.linalg.inv(transform)
    point = np.array([loc[0], loc[1], loc[2], 1])
    point_camera = np.dot(inv_transform, point)    
    point_camera = [point_camera[1], -point_camera[2], point_camera[0]]
    point_img = np.dot(K, point_camera)
    point_img[0] /= point_img[2]
    point_img[1] /= point_img[2]
    return point_camera, point_img[0:2]

def is_occluded(center, dimensions, yaw, semantic_img, intrinsic_mat, extrinsic_mat, image_size, threshold=50):
    corners = get_bbox_corners(center, dimensions, yaw)
    projected_corners = [project_to_image_plane(corner, intrinsic_mat, extrinsic_mat, image_size) for corner in corners]
    if None in projected_corners:
        return True
    bbox_mask = np.zeros(semantic_img.shape[:2], dtype=np.uint8)
    projected_corners = np.array(projected_corners, dtype=np.int32)
    cv2.fillConvexPoly(bbox_mask, projected_corners, 1)
    return np.sum(semantic_img[bbox_mask == 1])<threshold




def get_image_points(img,verts, K, world_2_camera):
    edges = [[0,1], [1,3], [3,2], [2,0], [0,4], [4,5], [5,1], [5,7], [7,6], [6,4], [6,2], [7,3]]
    for edge in edges:
        p1 = get_image_point(verts[edge[0]], K, world_2_camera)
        p2 = get_image_point(verts[edge[1]],  K, world_2_camera)
        cv2.line(img, (int(p1[0]),int(p1[1])), (int(p2[0]),int(p2[1])), (255,0,0, 255), 1)

def calc_intrinsic_params(fov):
    k = np.identity(3)
    k[0, 2] = WINDOW_WIDTH_HALF
    k[1, 2] = WINDOW_HEIGHT_HALF
    f = WINDOW_WIDTH / (2.0 * math.tan(fov * math.pi / 360.0))
    k[0, 0] = k[1, 1] = f
    return k 

def save_groundplanes(planes_fname, player, lidar_height):
    from math import cos, sin
    """ Saves the groundplane vector of the current frame.
        The format of the ground plane file is first three lines describing the file (number of parameters).
        The next line is the three parameters of the normal vector, and the last is the height of the normal vector,
        which is the same as the distance to the camera in meters.
    """
    rotation = player.get_transform().rotation
    pitch, roll = rotation.pitch, rotation.roll
    # Since measurements are in degrees, convert to radians
    pitch = degrees_to_radians(pitch)
    roll = degrees_to_radians(roll)
    # Rotate normal vector (y) wrt. pitch and yaw
    normal_vector = [cos(pitch)*sin(roll),
                     -cos(pitch)*cos(roll),
                     sin(pitch)
                     ]
    normal_vector = map(str, normal_vector)
    with open(planes_fname, 'w') as f:
        f.write("# Plane\n")
        f.write("Width 4\n")
        f.write("Height 1\n")
        f.write("{} {}\n".format(" ".join(normal_vector), lidar_height))
    logging.info("Wrote plane data to %s", planes_fname)


def save_ref_files(OUTPUT_FOLDER, id):
    """ Appends the id of the given record to the files """
    for name in ['train.txt', 'val.txt', 'trainval.txt']:
        path = os.path.join(OUTPUT_FOLDER, name)
        with open(path, 'a') as f:
            f.write("{0:06}".format(id) + '\n')
        logging.info("Wrote reference files to %s", path)


def save_image_data(filename, image, depth=False):
    # logging.info("Wrote image data to %s", filename)
    # breakpoint()
    # print("Here")
    if not depth:
        Image.fromarray(image[:, :, ::-1]).save(filename)
    else:
        image_arr = vrus_only_label_array(image)
        # breakpoint()
        Image.fromarray((image_arr*255).astype('uint8')).save(filename)


def save_lidar(filename, lid_arr):
    # pass
    np.savez(filename, lid_arr)


def save_calib(filename, calib_dict):
    with open(filename, 'wb') as f:
        pickle.dump(calib_dict, f)

def save_label(filename, agent_vel, label_dict):
    with open(filename, 'w') as f:
        # Write velocity on the first line
        f.write(str(agent_vel) + '\n')

        # Write agent dictionary values on the next lines
        for i in range(len(label_dict['class'])):
            f.write(' '.join(str(label_dict[key][i]) for key in label_dict.keys()) + '\n')

def save_bev(filename, bev):
    np.savez(filename, bev)



def save_lidar_data(filename, point_cloud, format="bin"):
    """ Saves lidar data to given filename, according to the lidar data format.
        bin is used for KITTI-data format, while .ply is the regular point cloud format
        In Unreal, the coordinate system of the engine is defined as, which is the same as the lidar points
        z
        ^   ^ x
        |  /
        | /
        |/____> y
        This is a left-handed coordinate system, with x being forward, y to the right and z up
        See also https://github.com/carla-simulator/carla/issues/498
        However, the lidar coordinate system from KITTI is defined as
              z
              ^   ^ x
              |  /
              | /
        y<____|/
        Which is a right handed coordinate sylstem
        Therefore, we need to flip the y axis of the lidar in order to get the correct lidar format for kitti.
        This corresponds to the following changes from Carla to Kitti
            Carla: X   Y   Z
            KITTI: X  -Y   Z
        NOTE: We do not flip the coordinate system when saving to .ply.
    """
    logging.info("Wrote lidar data to %s", filename)

    if format == "bin":
        lidar_array = [[point[0], -point[1], point[2], 1.0]
                       for point in point_cloud]
        lidar_array = np.array(lidar_array).astype(np.float32)

        logging.debug("Lidar min/max of x: {} {}".format(
                      lidar_array[:, 0].min(), lidar_array[:, 0].max()))
        logging.debug("Lidar min/max of y: {} {}".format(
                      lidar_array[:, 1].min(), lidar_array[:, 0].max()))
        logging.debug("Lidar min/max of z: {} {}".format(
                      lidar_array[:, 2].min(), lidar_array[:, 0].max()))
        lidar_array.tofile(filename)

    # point_cloud.save_to_disk(filename)




def save_kitti_data(filename, datapoints):
    with open(filename, 'w') as f:
        out_str = "\n".join([str(point) for point in datapoints if point])
        f.write(out_str)
    logging.info("Wrote kitti data to %s", filename)

def save_loc_data(filename, loc,loc_rc):
    loc=np.array(loc)
    loc_rc=np.array(loc_rc)
    ravel_mode = 'C'
    def write_flat(f, name, arr):
        f.write("{}: {}\n".format(name, ' '.join(
            map(str, arr.flatten(ravel_mode).squeeze()))))
    with open(filename, 'w') as f:
        write_flat(f, "ego_vehicle" , loc)
        write_flat(f, "other_vehicle" , loc_rc)
    logging.info("Wrote loc data to %s", filename)
    
def save_loc_data_0(filename, loc):
    loc=np.array(loc)
    print(loc)
    ravel_mode = 'C'
    def write_flat(f, name, arr):
        f.write("{}: {}\n".format(name, ' '.join(
            map(str, arr.flatten(ravel_mode).squeeze()))))
    with open(filename, 'w') as f:
        write_flat(f, "ego_vehicle" , loc)
        print("data export")
    logging.info("Wrote loc data to %s", filename)
    
def save_loc_data_2(filename, loc,loc_r,loc_rc):
    loc=np.array(loc)
    loc_r=np.array(loc_r)
    loc_rc=np.array(loc_rc)
    ravel_mode = 'C'
    def write_flat(f, name, arr):
        f.write("{}: {}\n".format(name, ' '.join(
            map(str, arr.flatten(ravel_mode).squeeze()))))
    with open(filename, 'w') as f:
        write_flat(f, "ego_vehicle" , loc)
        write_flat(f, "fore_vehicle" , loc_r)
        write_flat(f, "other_vehicle" , loc_rc)
    logging.info("Wrote loc data to %s", filename)

def save_calibration_matrices(filename, intrinsic_mat, rt_2, rt_3, rt_r,rt_rc):
    """ Saves the calibration matrices to a file.
        AVOD (and KITTI) refers to P as P=K*[R;t], so we will just store P.
        The resulting file will contain:
        3x4    p0-p3      Camera P matrix. Contains extrinsic
                          and intrinsic parameters. (P=K*[R;t])
        3x3    r0_rect    Rectification matrix, required to transform points
                          from velodyne to camera coordinate frame.
        3x4    tr_velodyne_to_cam    Used to transform from velodyne to cam
                                     coordinate frame according to:
                                     Point_Camera = P_cam * R0_rect *
                                                    Tr_velo_to_cam *
                                                    Point_Velodyne.
        3x4    tr_imu_to_velo        Used to transform from imu to velodyne coordinate frame. This is not needed since we do not export
                                     imu data.
    """
    f=1000
    k=[[f,0,960,0],[0,f,540,0],[0,0,1,0]]
    it=np.array(k)

    R_r=np.dot(inv(rt_2),rt_r)
    L_r=R_r
    R_rc=np.dot(inv(rt_2),rt_rc)
    L_rc=R_rc
    kitti_to_carla=np.mat([[0,0,1,0],[1,0,0,0],[0,-1,0,0],[0,0,0,1]])
    R_r=np.dot(R_r,kitti_to_carla)
    R_rc=np.dot(R_rc,kitti_to_carla)
    carla_to_kitti=np.mat([[0,1,0,0],[0,0,-1,0],[1,0,0,0],[0,0,0,1]])
    R_r=np.dot(carla_to_kitti,R_r)
    R_rc=np.dot(carla_to_kitti,R_rc)

    
    ravel_mode = 'C'
    P0 = it
    P1 = np.dot(it,R_r)
    P2 = np.dot(it,R_rc)
    
    R_2_to_r=np.dot(inv(rt_r),rt_2)
    R_2_to_r=np.dot(R_2_to_r,kitti_to_carla)
    R_2_to_r=np.dot(carla_to_kitti,R_2_to_r)
    P_2_to_r = np.dot(it,R_2_to_r)
    
    R_2_to_rc=np.dot(inv(rt_rc),rt_2)
    R_2_to_rc=np.dot(R_2_to_rc,kitti_to_carla)
    R_2_to_rc=np.dot(carla_to_kitti,R_2_to_rc)
    P_2_to_rc = np.dot(it,R_2_to_rc)
    

    R0 = np.identity(3)
    vel_to_world = np.mat([[1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,1]])
    vel_ego_to_cam = np.mat([[0,-1,0,0],[0,0,-1,0],[1,0,0,0]])
    vel_to_kitti = np.mat([[0,1,0,0],[0,0,-1,0],[1,0,0,0]])
    vel_r_to_cam = np.dot(L_r,vel_to_world)
    vel_r_to_cam = np.dot(vel_to_kitti,vel_r_to_cam)
    vel_rc_to_cam = np.dot(L_rc,vel_to_world)
    vel_rc_to_cam = np.dot(vel_to_kitti,vel_rc_to_cam)

    TR_imu_to_velo = np.identity(3)
    TR_imu_to_velo = np.column_stack((TR_imu_to_velo, np.array([0, 0, 0])))

    def write_flat(f, name, arr):
        f.write("{}: {}\n".format(name, ' '.join(
            map(str, arr.flatten(ravel_mode).squeeze()))))

    # All matrices are written on a line with spacing
    with open(filename, 'w') as f:
         # Avod expects all 4 P-matrices even though we only use the first
        write_flat(f, "P0" , P0)
        write_flat(f, "P1" , np.array(P1))
        write_flat(f, "P2" , np.array(P2))
        write_flat(f, "P3" , P0)
        write_flat(f, "Pc-r" , np.array(P_2_to_r))
        write_flat(f, "Pc-rc" , np.array(P_2_to_rc))
        write_flat(f, "R0_rect", R0)
        write_flat(f, "Tr_velo_to_cam", np.array(vel_ego_to_cam))
        write_flat(f, "Tr_velo_r_to_cam", np.array(vel_r_to_cam))
        write_flat(f, "Tr_velo_rc_to_cam", np.array(vel_rc_to_cam))
        write_flat(f, "TR_imu_to_velo", TR_imu_to_velo)
    logging.info("Wrote all calibration matrices to %s", filename)


# def save_frames(self, image_list):
#     #TODO: save veh1, veh2, infra1, infra2 images