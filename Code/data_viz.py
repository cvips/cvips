from glob import glob
import numpy as np
from PIL import Image
import os
from glob import glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import cv2
from PIL import ImageOps
from icecream import ic
import pdb


camera_names = ['FrontLeft_Cam', 'Front_Cam', 'FrontRight_Cam', 'BackLeft_Cam', 'Back_Cam', 'BackRight_Cam']
pred_bbox_color = (241, 101, 72)
gt_bbox_color = (61, 102, 255)
camera_name_list = ['Camera_FrontLeft', 'Camera_Front', 'Camera_FrontRight', 'Camera_BackLeft', 'Camera_Back', 'Camera_BackRight']
agent_list = ["veh1", "veh2", "veh3", "infra2"]




def put_text_on_image(image, text, position=(10, 10), font_size=20):
    """Add text to an image."""
    draw = ImageDraw.Draw(image)
    font_size = 40  # Adjust this value as needed
    font = ImageFont.truetype("Gidole-Regular.ttf", font_size)

    draw.text(position, text, font=font, fill="red")
    return image
def add_border(image, border_color="cyan", border_width=3):
    """Add a border around the image."""
    return ImageOps.expand(image, border=border_width, fill=border_color)

vehicle_name_list = []
time_stamp_list = [f"0{i}" for i in range(10, 96, 1)]
scenario_list = []
agent_frames_dict = {key:[] for key in agent_list}
add_border_agent = lambda img: np.array(add_border(Image.fromarray(img.astype('uint8')), border_color="red", border_width=5))

for time_stamp in time_stamp_list:
    for agent in agent_list:
        cam_list = []
        for i,camera in enumerate(camera_name_list):
            img = Image.open(f"viz/type1_subtype1_normal/{agent}/{camera}/Town10HD_type001_subtype0001_scenario00009/Town10HD_type001_subtype0001_scenario00009_{time_stamp}.png")
            img = img.resize((int(img.size[0]/2), int(img.size[1]/2)))
            agent_text = agent.capitalize()
            camera_text = camera_names[i]
            put_text_on_image(img, f"{agent_text} - {camera_text} - {time_stamp}")
            img = add_border(img)
            cam_list.append(img)
        frame_list = [np.array(cam) for cam in cam_list]
        # frame_list = np.vstack(([np.hstack((frame_list[0:3])), np.hstack((frame_list[3:]))]))
        if agent == 'infra2':
            frame_list = frame_list[-3]
        elif agent == 'veh3':
            frame_list = frame_list[-3]
        else:
            frame_list = frame_list[1]
        frame_list  = add_border_agent(frame_list)
        agent_frames_dict[agent].append(frame_list)

# for t, time_stamp in enumerate(time_stamp_list):
#         top_row = np.hstack((agent_frames_dict[agent_list[0]][t],  agent_frames_dict[agent_list[2]][t]))
#         bottom_row = np.hstack(( agent_frames_dict[agent_list[1]][t],  agent_frames_dict[agent_list[3]][t])) 
#         final_frame = np.vstack((top_row, bottom_row))
#         final_frames.append(final_frame)
# breakpoint()
def combine_frames(agent_name, time_stamp_list):
    final_frames = []
    # agent_mapping = {'veh1':0, 'veh2':1, 'veh3':2, 'infra2':3}
    for t, time_stamp in enumerate(time_stamp_list):
            top_row = np.hstack((agent_frames_dict['veh1'][t],  agent_frames_dict['veh3'][t]))
            bottom_row = np.hstack(( agent_frames_dict['veh2'][t],  agent_frames_dict['infra2'][t])) 
            final_frame = np.vstack((top_row, bottom_row))
            final_frames.append(final_frame)
    return final_frames

def write_video(frames, filename, fps=5):
    if not frames:
        return  # No frames to write, exit function

    height, width, layers = frames[0].shape
    video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for frame in frames:
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
        video.write(bgr_frame)

    video.release()

agent = 'VVVI'

# for agent in ['veh1', 'veh2', 'infra2']:
#     frames = [Image.fromarray(np.vstack((np.hstack(agent_frames_dict[agent][:3][t]), 
#                                          np.hstack(agent_frames_dict[agent][3:][t])))) 
#               for t in range(len(time_stamp_list))]
final_frames = combine_frames(agent, time_stamp_list)
write_video(final_frames, f'output_video_{agent}_4cam.mp4')








# frames_pil = [Image.fromarray(frame) for frame in final_frames]


# import cv2
# import numpy as np

# # Assuming final_frames is a list of numpy arrays in RGB format
# final_frames = [np.array(frame) for frame in frames_pil]  # Convert PIL images to numpy arrays if needed

# # Define the codec and create VideoWriter object
# height, width, layers = final_frames[0].shape
# video = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 2, (width, height))

# for frame in final_frames:
#     bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
#     video.write(bgr_frame)

# video.release()  # Release the video writer

