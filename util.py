import cv2
from os.path import splitext, basename
from os import getcwd, listdir
from glob import glob
from datetime import datetime

def new_dimension(image, width=0, height=0, scale_percent=100):
    img = cv2.imread(image)
    new_w = int(width * scale_percent / 100) if width >0 else img.shape[1]
    new_h = int(height * scale_percent / 100) if height > 0 else img.shape[0]
    return new_w, new_h

def get_all_files(IMAGE_DIR_PATH, FRAMERATE, START_IMG):
    all_images = [elem for idx, elem in enumerate(glob(IMAGE_DIR_PATH + "/*"))
        if int(splitext(basename(elem).split('_')[-1])[0]) % FRAMERATE == 0 and int(splitext(basename(elem).split('_')[-1])[0]) >= START_IMG]
    all_images.sort(key=lambda img: int(splitext(basename(img).split('_')[-1])[0]))
    return all_images

def get_annotation_csv(CURRENT_DIR):
    files_csv = [i for i in listdir(CURRENT_DIR) if i.endswith('.csv') and i.__contains__("Annotations_Segmentation")]
    annotation_path = files_csv[0] if (len(files_csv) == 1) \
        else getcwd() + "/Annotations_Segmentation [" + datetime.now().strftime('%Y-%m-%d %H_%M_%S') + "].csv"
    return annotation_path

mask_right = [(703, 523), (700, 521), (780, 522), (794, 532), (797, 542), (806, 546), (815, 549), (890, 549), (1003, 551), (1009, 567), (1021, 575), (1069, 563), (1067, 557), (1154, 476), (1178, 477), (1277, 334)]
mask_center = [(347, 503), (505, 501), (572, 514), (626, 519), (706, 521), (783, 521), (800, 544), (809, 550), (885, 550), (959, 546), (1003, 552), (1003, 572), (1025, 577), (1048, 573)]
mask_left = [(7, 479), (46, 481), (49, 474), (88, 472), (141, 487), (174, 481), (215, 486), (239, 489), (330, 498), (421, 503), (502, 509), (600, 515), (622, 523), (667, 523)]
#PREDEFINED_MASK=[mask_left, mask_center, mask_right]