import csv
from os.path import join, isdir
from os import makedirs
import sys
from util import *

import cv2 as cv
import numpy as np

videos = [
    "ARG 19 SS08 OBC NEU POV.mp4",  # 0
    "ARG 19 SS16 OBC NEU POV.mp4",  # 1
    "ARG 19 SS18 OBC OGI POV.mp4",  # 2
    "FRA 19 SHD POV EVA.mp4",  # 3
    "FRA 19 SHD POV NEU.mp4",  # 4
    "MON 19 SS01 OBC NEU POV.mp4",  # 5
    "SPA 18 SHD OBC NEU POV.mp4",  # 6
    "MON 19 SS01 OBC OGI POV.mp4",  # 7
    "VBOX202002140828390001_0001.mp4",  # 8
    "FIN18_ss19lat_pov.mp4",  # 9
    "ITA18_ss18eva_pov.mp4"  # 10
]

CURRENT_DIR = getcwd()
cur_video = videos[10]
print("Current Video: ", cur_video)
VIDEO_DIR = "C:\\Users\\Dominique\\Desktop\\Masterthesis\\Labeling\\Source"
IMAGE_DIR = splitext(cur_video)[0]
IMAGE_DIR_PATH = join("C:\\Users\\Dominique\\Desktop\\Masterthesis\\Labeling\\Target", IMAGE_DIR)
FRAMERATE = 25
START_IMG = 0

# list all images and sort them
all_images = get_all_files(IMAGE_DIR_PATH, FRAMERATE, START_IMG)
annotation_path = get_annotation_csv(CURRENT_DIR)

img_counter = 0

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
temp_refPt = []
next_entries = []
last_img = []
image = None
temp_img = None
cropping = False
printed = False

SCALE_PERCENT = 90
CONTRAST = 0
BRIGHTNESS = 0
width, height = new_dimension(image=all_images[0], scale_percent=SCALE_PERCENT)
dim = (width, height)

"""
ToDo:
    1. adjust image size. Since Full-HD image, therefore impossible to display the image completely including closing
    button on the monitor (without moving) => Points at the border do not correspond to the border. See example images
    2. maybe add a zoom function including moving by mouse wheel click.
"""


def track_clicks(event, x, y, *flags):
    # grab references to the global variables
    global last_img, next_entries, temp_refPt, refPt, cropping, printed, dim

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv.EVENT_LBUTTONDOWN:
        temp_refPt.append((x, y))
        cv.circle(image, (x, y), 3, (0, 255, 0))

        if len(temp_refPt) > 1:
            print("temp_refPt =", temp_refPt)
            cv.line(image, temp_refPt[-2], temp_refPt[-1], (0, 255, 0))
            last_img.append(image.copy())

        cv.imshow(all_images[img_counter], image)


def draw_line():
    global image, last_img, temp_refPt
    for idx, elem in enumerate(temp_refPt):
        x, y = elem
        cv.circle(image, (x, y), 3, (0, 255, 0))
        print("temp_refPt =", temp_refPt)
        if idx > 0:
            cv.line(image, temp_refPt[idx - 1], temp_refPt[idx], (0, 255, 0))
        last_img.append(image.copy())

    cv.imshow(all_images[img_counter], image)


def last_img_counter(*args):
    global img_counter
    img_counter -= 1
    pass


def create_window(name):
    cv.destroyAllWindows()
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.resizeWindow(name, width, height)
    cv.moveWindow(name, 50, 20)
    cv.createButton("Back", last_img_counter, None, cv.QT_PUSH_BUTTON, 1)
    cv.setMouseCallback(name, track_clicks)


def generate_annotations_file():
    global last_img, next_entries, img_counter, printed, temp_refPt, refPt, dim, image, CONTRAST, BRIGHTNESS

    file = open(annotation_path, 'a+', encoding="utf-8")
    # file.write("Filename;Class;Coordinates/n")
    file.close()

    image = cv.imread(all_images[img_counter])
    image = cv.resize(image, dim)
    last_img.append(image.copy())

    create_window(all_images[img_counter])

    while img_counter < len(all_images):

        cv.imshow(all_images[img_counter], image)
        k = cv.waitKeyEx(0)
        print("k =", k)
        if k in [115, 112, 103] and len(temp_refPt) > 0:
            if k == 115:  # 115 corresponds to s (streets)
                temp_refPt = ["Street", temp_refPt]
            if k == 112:  # 112 corresponds to p (single of persons)
                temp_refPt = ["Person", temp_refPt]
            if k == 103:  # 103 corresponds to g (group of persons)
                temp_refPt = ["Group", temp_refPt]

            refPt.append(temp_refPt)
            alpha = 0.5
            image = last_img[0].copy()
            overlay = last_img[0].copy()
            for poly in refPt:
                temp = np.array([[[elem[0], elem[1]] for elem in poly[1]]], dtype=np.int32)
                if poly[0] == "Street":
                    cv.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                if poly[0] == "Person":
                    cv.fillPoly(overlay, pts=temp, color=(232, 163, 0))
                if poly[0] == "Group":
                    cv.fillPoly(overlay, pts=temp, color=(163, 73, 163))
            cv.addWeighted(image, 1 - alpha, overlay, alpha, 0, image)
            temp_refPt = []
        if k == 114 and len(temp_refPt) > 0:
            # 114 corresponds to r, which resets the last clicked point
            del last_img[-1]
            del temp_refPt[-1]
            image = last_img[-1].copy()

            print("refPt =", temp_refPt)
            cv.imshow(all_images[img_counter], image)
        if k in [33, 34, 36, 167]:
            refPt = []
            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img.append(image.copy())
            old_temp = temp_refPt.copy()
            if k == 33:  # key 33 means '!' and shifts the current points left
                for idx, elem in enumerate(temp_refPt):
                    x, y = elem
                    if x - 1 >= 0:
                        temp_refPt[idx] = (x - 1, y)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 34:  # key 34 means '"' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x, y = elem
                    if x + 1 < width:
                        temp_refPt[idx] = (x + 1, y)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 167:  # key 167 means '$' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x, y = elem
                    if y + 1 < height:
                        temp_refPt[idx] = (x, y + 1)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 36:  # key 36 means '§' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x, y = elem
                    if y - 1 >= 0:
                        temp_refPt[idx] = (x, y - 1)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            for idx, elem in enumerate(temp_refPt):
                x, y = elem
                cv.circle(image, (x, y), 3, (0, 255, 0))
                if idx > 0:
                    cv.line(image, temp_refPt[idx - 1], temp_refPt[idx], (0, 255, 0))
                last_img.append(image.copy())

            cv.imshow(all_images[img_counter], image)
        if 48 <= k <= 57 or k == 223:  # corresponds to the number keys 0 up to 9, this gives the first predefined mask
            temp_refPt = []
            refPt = []
            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img.append(image.copy())
            if cur_video.split('/')[-1] == videos[9]:
                if k == 49:  # 48 corresponds to 0, this gives you the 1st predefined mask
                    temp_refPt = mask_left.copy()
                if k == 50:  # 48 corresponds to 0, this gives you the 1st predefined mask
                    temp_refPt = mask_center.copy()
                if k == 51:  # 48 corresponds to 0, this gives you the 1st predefined mask
                    temp_refPt = mask_right.copy()
                draw_line()
        if k == 108:  # if you type l, then a point at the right bottom we be set
            temp_refPt.append((width - 1, height - 1))
            draw_line()
        if k == 43:
            hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
            hsv[:, :, 2] += 3
            image = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        if k == 45:
            hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
            hsv[:, :, 2] -= 3
            image = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        if k == 13:  # Enter: save and next

            # file = open(annotation_path, 'w+', encoding="utf-8")
            video_name = all_images[img_counter].split('/')[-1].split('_')[0]
            frame_numb = all_images[img_counter].split('/')[-1].split('_')[-1].split('.')[0]
            print("video_name =", video_name)
            print("frame_numb =", frame_numb)
            annotation_dir = getcwd() + "/Segmented_Images/" + video_name + "/"

            if not isdir(annotation_dir):
                makedirs(annotation_dir)

            save_as_shown = False

            image = cv.imread(all_images[img_counter])
            overlay = image.copy()
            output = np.zeros(shape=image.shape)
            points_were_set = False
            street_coordinates = []
            person_coordinates = []
            group_coordinates = []
            for elem in refPt:
                if len(elem[1]) > 0:
                    points_were_set = True
                    temp = np.array(
                        [[[pt[0] * (100.0 / SCALE_PERCENT), pt[1] * (100.0 / SCALE_PERCENT)] for pt in elem[1]]],
                        dtype=np.int32)

                    if save_as_shown:
                        cv.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                    else:
                        if elem[0] == "Street":
                            street_coordinates.append(elem[1])
                            cv.fillPoly(output, pts=temp, color=(0, 171, 244))
                        if elem[0] == "Person":
                            person_coordinates.append(elem[1])
                            cv.fillPoly(output, pts=temp, color=(232, 163, 0))
                        if elem[0] == "Group":
                            group_coordinates.append(elem[1])
                            cv.fillPoly(output, pts=temp, color=(163, 73, 163))
                        # cv2.fillPoly(output, pts=temp, color=(0, 171, 244))
            if save_as_shown:
                cv.addWeighted(image, 1 - 0.4, overlay, 0.4, 0, image)
            if points_were_set:
                if save_as_shown:
                    cv.imwrite(annotation_dir + frame_numb + ".png", image)
                else:
                    cv.imwrite(annotation_dir + frame_numb + ".png", output)
            cv.destroyWindow(all_images[img_counter])

            file = open(annotation_path, 'a+', encoding="utf-8")
            if len(street_coordinates) > 0:
                file.write(all_images[img_counter] + ";Street;" + str(street_coordinates) + "/n")

            if len(person_coordinates) > 0:
                file.write(all_images[img_counter] + ";Person;" + str(person_coordinates) + "/n")

            if len(group_coordinates) > 0:
                file.write(all_images[img_counter] + ";Group;" + str(group_coordinates) + "/n")

            file.close()

            temp_refPt = []
            refPt = []
            img_counter += 1

            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img = [image.copy()]
            create_window(all_images[img_counter])
        if k == 8:  # backspace
            video_name = all_images[img_counter].split('/')[-1].split('_')[0]
            frame_numb = all_images[img_counter - 1].split('/')[-1].split('_')[-1].split('.')[0]
            print("Video name: ", video_name)
            print("Frame number: ", frame_numb)
            cv.destroyWindow(all_images[img_counter])
            temp_refPt = []
            refPt = []
            img_counter -= 1

            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img = [image.copy()]
            create_window(all_images[img_counter])
        if k == 32:  # Space: skip this image and next
            temp_refPt = []
            refPt = []
            img_counter += 1

            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img = [image.copy()]
            create_window(all_images[img_counter])
        if k == 65535:  # delete
            temp_refPt = []
            refPt = []
            image = cv.imread(all_images[img_counter])
            image = cv.resize(image, dim)
            last_img.append(image.copy())
            cv.moveWindow(all_images[img_counter], 50, 20)
            cv.setMouseCallback(all_images[img_counter], track_clicks)
        if k == 27:  # escape key
            cv.setWindowProperty(all_images[img_counter], cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
            # img_counter = len(all_images)
        if k == 113:  # exit=q
            sys.exit(0)

        print("You typed: key =", k)


def refine_annotations():
    """
    ToDo:
        1. Sort the coordinates of the Annotation entries for each Frame number.
    """

    annotation_file_org = open(annotation_path, 'r', encoding="utf-8")
    annotation_list = list(csv.reader(annotation_file_org, delimiter=';'))
    annotation_file_org.close()
    print("annotation_list =", annotation_list)

    annotation_grouped_by_frames = []
    i = 0
    while annotation_list[i][0] != annotation_list[-1][0]:
        temp = []
        for j in range(i, len(annotation_list)):
            elem_i = annotation_list[i][0]
            elem_j = annotation_list[j][0]
            if elem_i == elem_j:
                temp.append(annotation_list[j])
            else:
                i = j
                break
        annotation_grouped_by_frames.append(temp)

    annotation_file_sorted = open(getcwd() + "/Annotations_sorted.csv", 'a+', encoding="utf-8")

    for elem in annotation_grouped_by_frames:
        elem.sort(key=lambda e: int(e[2]))
        elem.sort(key=lambda e: int(e[1]))
        for row in elem:
            annotation_file_sorted.write(
                row[0] + ";" + row[1] + ";" + row[2] + ";" + row[3] + ";" + row[4] + ";" + row[5] + "/n")


def print_reached_end():
    print("\t\t\t----------------------------------------------------")
    print("\t\t\tYou reached the end. No further decreasing possible.")
    print("\t\t\t----------------------------------------------------")


def video_to_images():
    global IMAGE_DIR_PATH
    print("image_dir =", IMAGE_DIR_PATH)

    videos_with_sub_dirs = [cur_video]

    for video_name in videos_with_sub_dirs:
        video_path = join(VIDEO_DIR, video_name)
        print("video_path =", video_path)
        video_capture = cv.VideoCapture(video_path)
        success, image_frame = video_capture.read()
        counter = 0
        prefix = video_name.split('/')[-1][:-4]
        save_dir = join(IMAGE_DIR_PATH, prefix)
        print("save_dir =", save_dir)

        if not isdir(save_dir):
            makedirs(save_dir)

        while success:
            cur_img_path = save_dir + prefix + "_" + str(counter) + ".png"
            cv.imwrite(cur_img_path, image_frame)  # save frame as JPEG file
            success, image_frame = video_capture.read()
            if success and counter % 100 == 0:
                print("Read frame", counter, "successfully")
            counter += 1
        print("Total Read frame", counter, "successfully")


video_to_images()
# generate_annotations_file()
# refine_annotations()
# show_and_refine_Annotations()
