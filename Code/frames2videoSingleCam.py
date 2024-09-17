import cv2
import os
from PIL import Image
import numpy as np

def create_video_from_images(image_list, output_video, fps=5):
    # Get the dimensions of the first image
    first_image = image_list[0]
    height, width, layers = first_image.shape
    video_size = (width, height)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    video = cv2.VideoWriter(output_video, fourcc, fps, video_size)

    for frame in image_list:
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
        video.write(bgr_frame)

    # Release the VideoWriter object
    video.release()
    print(f"Video saved as {output_video}")

# Parameters
image_dir = 'Dataset/type1_subtype1_normal/veh2/Camera_Front/Town04_type001_subtype0001_scenario00011/'  # Replace with the actual path to your images
output_video = 'input.mp4'  # Ensure the output file is .mp4
fps = 5  # Frames per second

# Load images
image_list = []
time_stamp_list = [f"0{i:02d}" for i in range(10, 96)]
for time_stamp in time_stamp_list:
    img_path = os.path.join(image_dir, f"Town04_type001_subtype0001_scenario00011_{time_stamp}.png")
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((int(img.size[0]/2), int(img.size[1]/2)))
        img_array = np.array(img)
        image_list.append(img_array)
    else:
        print(f"Warning: Image {img_path} does not exist and will be skipped.")

# Create the video
create_video_from_images(image_list, output_video, fps)
