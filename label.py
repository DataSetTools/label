import os
import sys
import glob
import numpy as np
import cv2
import csv

import time
import datetime

# import argparse if you want to set neccessary arguments which are needed to start this file (e.g. Image path)

# from tkinter import *
# from tkinter.filedialog import askopenfilename
# root = Tk()

videos = ["ARG 19 SS08 OBC NEU POV.mp4",        # 0
          "ARG 19 SS16 OBC NEU POV.mp4",        # 1
          "ARG 19 SS18 OBC OGI POV.mp4",        # 2
          "FRA 19 SHD POV EVA.mp4",             # 3
          "FRA 19 SHD POV NEU.mp4",             # 4
          "MON 19 SS01 OBC NEU POV.mp4",        # 5
          "SPA 18 SHD OBC NEU POV.mp4",         # 6
          "MON 19 SS01 OBC OGI POV.mp4",        # 7
          "VBOX202002140828390001_0001.mp4",    # 8
          "FIN18_ss19lat_pov.mp4",              # 9
          "ITA18_ss18eva_pov.mp4"               #10
          ]

# video_dir = "ARG 19 SS18 POV/"
video_dir = "/"

# cur_video = video_dir + videos[2]
cur_video = video_dir + videos[9]
print("cur_video =", cur_video)


video_dir_path = "/home/dominique/Videos/MA/Videos/"

print("/home/dominique/Bilder/" + cur_video.split('/')[-1].split('.')[0])

framerate = 25

all_images = [elem for idx, elem in enumerate(glob.glob("/home/dominique/Bilder/" + cur_video.split('/')[-1].split('.')[0] + "/*"))
              if int((elem.split('/')[-1]).split('_')[-1].split('.')[0]) % framerate == 0 and int((elem.split('/')[-1]).split('_')[-1].split('.')[0]) >= 0] # 5275

# all_images.sort(key = os.path.getmtime)
all_images.sort(key=lambda t: int(t.split('_')[-1].split('.')[0]))
print(all_images)


date_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H_%M_%S')
annotation_path = os.getcwd() + "/Annotations_Segmentation [" + date_time + "].csv"

img_counter = 0

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
temp_refPt = []
next_entries = []
last_img = []
temp_img = None
cropping = False
printed = False

scale_percent = 90  # percent of original size
width = int(1280 * scale_percent / 100)
height = int(720 * scale_percent / 100)
dim = (width, height)

contrast = 0
brightness = 0

"""
ToDo:
    1. Bildgröße anpassen. Da Full-HD Bild, daher unmöglich das Bild komplett inkl Schließen-Button auf den Monitor zu 
       bekommen (ohne zu verschieben)
       => Punkte am Rand entsprechen nicht dem Rand. Siehe Bsp.bilder
    2. Vielleicht noch Zoom-Funktion inkl. verschieben per Mausrad-Klick einbauen.
"""


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global last_img, next_entries, temp_refPt, refPt, cropping, printed, dim

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        # print(all_images[img_counter], "/tStartpoints:", x, y, end="")
        temp_refPt.append((x, y))
        cv2.circle(image, (x,y), 3, (0,255,0))

        if len(temp_refPt) > 1:
            print("temp_refPt =", temp_refPt)
            cv2.line(image, temp_refPt[-2], temp_refPt[-1], (0, 255, 0))
            last_img.append(image.copy())

        cv2.imshow(all_images[img_counter], image)


def generate_annotations_file():
    global last_img, next_entries, img_counter, printed, temp_refPt, refPt, dim, image, contrast, brightness

    file = open(annotation_path, 'a+', encoding="utf-8")
    # file.write("Filename;Class;Coordinates/n")
    file.close()

    image = cv2.imread(all_images[img_counter])
    image = cv2.resize(image, dim)
    last_img.append(image.copy())

    cv2.namedWindow(all_images[img_counter])
    # cv2.namedWindow(all_images[img_counter], cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty(all_images[img_counter], cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(all_images[img_counter], 50, 20)
    cv2.setMouseCallback(all_images[img_counter], click_and_crop)
    cv2.imshow(all_images[img_counter], image)

    while img_counter < len(all_images):

        cv2.imshow(all_images[img_counter], image)
        k = cv2.waitKeyEx(0)
        print("k =", k)
        if k == 115:  # 115 cooresponds to s (streets)
            if len(temp_refPt) > 0:
                temp_refPt = ["Street", temp_refPt]
                refPt.append(temp_refPt)
                alpha = 0.5
                image = last_img[0].copy()
                overlay = last_img[0].copy()
                for poly in refPt:
                    temp = np.array([[[elem[0], elem[1]] for elem in poly[1]]], dtype=np.int32)
                    if poly[0] == "Street":
                        cv2.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                    if poly[0] == "Person":
                        cv2.fillPoly(overlay, pts=temp, color=(232, 163, 0))
                    if poly[0] == "Group":
                        cv2.fillPoly(overlay, pts=temp, color=(163, 73, 163))
                cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0, image)
                temp_refPt = []
        if k == 112:  # 112 cooresponds to p (single of persons)
            if len(temp_refPt) > 0:
                temp_refPt = ["Person", temp_refPt]
                refPt.append(temp_refPt)
                alpha = 0.5
                image = last_img[0].copy()
                overlay = last_img[0].copy()
                for poly in refPt:
                    temp = np.array([[[elem[0], elem[1]] for elem in poly[1]]], dtype=np.int32)
                    if poly[0] == "Street":
                        cv2.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                    if poly[0] == "Person":
                        cv2.fillPoly(overlay, pts=temp, color=(232, 163, 0))
                    if poly[0] == "Group":
                        cv2.fillPoly(overlay, pts=temp, color=(163, 73, 163))
                cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0, image)
                temp_refPt = []
        if k == 103:  # 103 cooresponds to g (group of persons)
            if len(temp_refPt) > 0:
                temp_refPt = ["Group", temp_refPt]
                refPt.append(temp_refPt)
                alpha = 0.5
                image = last_img[0].copy()
                overlay = last_img[0].copy()
                for poly in refPt:
                    temp = np.array([[[elem[0], elem[1]] for elem in poly[1]]], dtype=np.int32)
                    if poly[0] == "Street":
                        cv2.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                    if poly[0] == "Person":
                        cv2.fillPoly(overlay, pts=temp, color=(232, 163, 0))
                    if poly[0] == "Group":
                        cv2.fillPoly(overlay, pts=temp, color=(163, 73, 163))
                cv2.addWeighted(image, 1 - alpha, overlay, alpha, 0, image)
                temp_refPt = []
        if k == 114:  # 114 cooresponds to r, which resets the last bounding box
            if len(temp_refPt) > 0:
                try:
                    del last_img[-1]
                    del temp_refPt[-1]
                    image = last_img[-1].copy()
                except:
                    pass
                print("refPt =", temp_refPt)
                cv2.imshow(all_images[img_counter], image)
        if k in [33,34,36,167]:
            refPt = []
            image = cv2.imread(all_images[img_counter])
            image = cv2.resize(image, dim)
            last_img.append(image.copy())
            old_temp = temp_refPt.copy()
            if k == 33:  # key 33 means '!' and shifts the current points left
                for idx, elem in enumerate(temp_refPt):
                    x,y = elem
                    if x-1 >= 0:
                        temp_refPt[idx] = (x-1,y)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 34:  # key 34 means '"' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x,y = elem
                    if x + 1 < width:
                        temp_refPt[idx] = (x+1,y)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 167: # key 167 means '$' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x,y = elem
                    if y + 1 < height:
                        temp_refPt[idx] = (x,y+1)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            if k == 36: # key 36 means '§' and shifts the current points right
                for idx, elem in enumerate(temp_refPt):
                    x,y = elem
                    if y - 1 >= 0:
                        temp_refPt[idx] = (x,y-1)
                    else:
                        print_reached_end()
                        temp_refPt = old_temp.copy()
                        break
            for idx, elem in enumerate(temp_refPt):
                x, y = elem
                cv2.circle(image, (x, y), 3, (0, 255, 0))
                if idx > 0:
                    cv2.line(image, temp_refPt[idx - 1], temp_refPt[idx], (0, 255, 0))
                last_img.append(image.copy())

            cv2.imshow(all_images[img_counter], image)
        if 48 <= k <= 57 or k == 223:   # numbers between 48 and 58 cooresponds to the number keys 0 up to 9, this gives you the first predefined mask
            temp_refPt = []
            refPt = []
            image = cv2.imread(all_images[img_counter])
            image = cv2.resize(image, dim)
            last_img.append(image.copy())
            if k == 48:  # 48 cooresponds to 0, this gives you the 1st predefined mask
                if cur_video.split('/')[-1] == videos[9]:
                    temp_refPt = [(388, 455), (451, 457), (506, 463), (515, 463), (553, 469), (661, 470), (698, 469), (712, 478), (720, 492), (727, 489), (732, 494), (896, 494), (907, 500), (907, 515), (922, 519), (930, 516), (934, 516), (942, 513), (963, 506), (961, 502), (1039, 430)]
                    #temp_refPt = [(12, 431), (33, 432), (44, 426), (76, 424), (118, 434), (125, 440), (138, 439), (146, 434), (161, 432), (195, 437), (204, 444), (311, 453), (446, 455), (487, 459), (553, 469), (704, 469), (719, 489), (730, 491), (732, 495), (895, 495), (906, 503), (908, 516), (922, 520), (946, 513), (963, 505), (960, 501), (1039, 430), (1063, 428), (1151, 298)]

            for idx, elem in enumerate(temp_refPt):
                x, y = elem
                cv2.circle(image, (x, y), 3, (0, 255, 0))
                print("temp_refPt =", temp_refPt)
                if idx > 0:
                    cv2.line(image, temp_refPt[idx - 1], temp_refPt[idx], (0, 255, 0))
                last_img.append(image.copy())

            cv2.imshow(all_images[img_counter], image)
        if k == 108:    # if you type l, then a point at the right bottum we be set
            temp_refPt.append((width-1, height-1))
            for idx, elem in enumerate(temp_refPt):
                x, y = elem
                cv2.circle(image, (x, y), 3, (0, 255, 0))
                print("temp_refPt =", temp_refPt)
                if idx > 0:
                    cv2.line(image, temp_refPt[idx - 1], temp_refPt[idx], (0, 255, 0))
                last_img.append(image.copy())

            cv2.imshow(all_images[img_counter], image)
        if k == 43:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[:,:,2] += 3
            image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        if k == 45:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[:,:,2] -= 3
            image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        if k == 13:  # 0 corresponds to the right arrow (but also to the Entf key), which means we skip this image

            # file = open(annotation_path, 'w+', encoding="utf-8")
            video_name = all_images[img_counter].split('/')[-1].split('_')[0]
            frame_numb = all_images[img_counter].split('/')[-1].split('_')[-1].split('.')[0]
            print("video_name =", video_name)
            print("frame_numb =", frame_numb)
            anno_dir = os.getcwd() + "/Segmented_Images/" + video_name + "/"

            if not os.path.isdir(anno_dir):
                os.makedirs(anno_dir)


            save_as_shown = False

            image = cv2.imread(all_images[img_counter])
            overlay = image.copy()
            output = np.zeros(shape=image.shape)
            points_were_set = False
            street_coordinates = []
            person_coordinates = []
            group_coordinates = []
            for elem in refPt:
                if len(elem[1]) > 0:
                    points_were_set = True
                    temp = np.array([[[pt[0] * (100.0/scale_percent), pt[1]*(100.0/scale_percent)] for pt in elem[1]]], dtype=np.int32)

                    if save_as_shown:
                        cv2.fillPoly(overlay, pts=temp, color=(0, 171, 244))
                    else:
                        if elem[0] == "Street":
                            street_coordinates.append(elem[1])
                            cv2.fillPoly(output, pts=temp, color=(0, 171, 244))
                        if elem[0] == "Person":
                            person_coordinates.append(elem[1])
                            cv2.fillPoly(output, pts=temp, color=(232, 163, 0))
                        if elem[0] == "Group":
                            group_coordinates.append(elem[1])
                            cv2.fillPoly(output, pts=temp, color=(163, 73, 163))
                        # cv2.fillPoly(output, pts=temp, color=(0, 171, 244))
            if save_as_shown:
                cv2.addWeighted(image, 1 - 0.4, overlay, 0.4, 0, image)
            if points_were_set:
                if save_as_shown:
                    cv2.imwrite(anno_dir + frame_numb + ".png",image)
                else:
                    cv2.imwrite(anno_dir + frame_numb + ".png", output)
            cv2.destroyWindow(all_images[img_counter])

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

            image = cv2.imread(all_images[img_counter])
            image = cv2.resize(image, dim)
            last_img = [image.copy()]
            cv2.namedWindow(all_images[img_counter])
            # cv2.namedWindow(all_images[img_counter], cv2.WND_PROP_FULLSCREEN)
            # cv2.setWindowProperty(all_images[img_counter], cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.moveWindow(all_images[img_counter], 50, 20)
            cv2.setMouseCallback(all_images[img_counter], click_and_crop)
            cv2.imshow(all_images[img_counter], image)
        if k == 8:
            temp_refPt = []
            refPt = []
            image = cv2.imread(all_images[img_counter])
            image = cv2.resize(image, dim)
            last_img.append(image.copy())
            cv2.moveWindow(all_images[img_counter], 50, 20)
            cv2.setMouseCallback(all_images[img_counter], click_and_crop)
            cv2.imshow(all_images[img_counter], image)
        if k == 27:  # escape key
            img_counter = len(all_images)
        if k == 113: # exit=q
            sys.exit(0)

        print("You typed: key =", k)




def refine_Annotations():
    """
    ToDo:
        1. Sort the coordinates of the Annotation entries for each Frame number.
    """

    anno_file_org = open(annotation_path, 'r', encoding="utf-8")
    anno_list = list(csv.reader(anno_file_org, delimiter=';'))
    anno_file_org.close()
    print("anno_list =", anno_list)

    anno_grouped_by_Frames = []
    i = 0
    while anno_list[i][0] != anno_list[-1][0]:
        temp = []
        for j in range(i,len(anno_list)):
            elem_i = anno_list[i][0]
            elem_j = anno_list[j][0]
            if elem_i == elem_j:
                temp.append(anno_list[j])
            else:
                i = j
                break
        anno_grouped_by_Frames.append(temp)

    # print(anno_list[0])
    # print(anno_grouped_by_Frames)
    anno_file_sorted = open(os.getcwd() + "/Annotations_sorted.csv", 'a+', encoding="utf-8")

    for elem in anno_grouped_by_Frames:
        elem.sort(key = lambda e : int(e[2]))
        elem.sort(key=lambda e: int(e[1]))
        for row in elem:
            anno_file_sorted.write(row[0] + ";" + row[1] + ";" + row[2] + ";" + row[3] + ";" + row[4] + ";" + row[5] + "/n")

def print_reached_end():
    print("\t\t\t----------------------------------------------------")
    print("\t\t\tYou reached the end. No further decreasing possible.")
    print("\t\t\t----------------------------------------------------")

def Video_to_Images():
    image_dir = "/home/dominique/Bilder/"
    print("image_dir =", image_dir)

    videos_with_subdirs = [cur_video]

    for video_name in videos_with_subdirs:
        video_path = video_dir_path + video_name
        print("video_path =", video_path)
        vidcap = cv2.VideoCapture(video_path)
        success, image = vidcap.read()
        counter = 0
        prefix = video_name.split('/')[-1][:-4]
        save_dir = image_dir + prefix + "/"
        print("save_dir =", save_dir)

        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        while success:
            cur_img_path = save_dir + prefix + "_" + str(counter) + ".png"
            cv2.imwrite(cur_img_path, image)  # save frame as JPEG file
            success, image = vidcap.read()
            if success and counter % 100 == 0:
                print("Read frame", counter, "successfully")
            counter += 1




# Video_to_Images()
generate_annotations_file()
# refine_Annotations()
# show_and_refine_Annotations()
