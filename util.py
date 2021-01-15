import cv2
from os.path import splitext, basename, join, dirname
from os import getcwd, listdir, rename, makedirs
from glob import glob
from datetime import datetime
from shutil import copyfile
from tqdm import tqdm
import json
import base64

# from PIL import Image, ImageSequence

mask_right = [(703, 523), (700, 521), (780, 522), (794, 532), (797, 542), (806, 546), (815, 549), (890, 549),
              (1003, 551), (1009, 567), (1021, 575), (1069, 563), (1067, 557), (1154, 476), (1178, 477), (1277, 334)]
mask_center = [(347, 503), (505, 501), (572, 514), (626, 519), (706, 521), (783, 521), (800, 544), (809, 550),
               (885, 550), (959, 546), (1003, 552), (1003, 572), (1025, 577), (1048, 573)]
mask_left = [(7, 479), (46, 481), (49, 474), (88, 472), (141, 487), (174, 481), (215, 486), (239, 489), (330, 498),
             (421, 503), (502, 509), (600, 515), (622, 523), (667, 523)]


# PREDEFINED_MASK=[mask_left, mask_center, mask_right]

def new_dimension(image, width=0, height=0, scale_percent=100):
    img = cv2.imread(image)
    new_w = int(width * scale_percent / 100) if width > 0 else img.shape[1]
    new_h = int(height * scale_percent / 100) if height > 0 else img.shape[0]
    return new_w, new_h


def get_all_files(image_dir_path, framerate=25, start_img=0, img_ext="png", sep='_'):
    all_image_paths = [elem for idx, elem in enumerate(glob(image_dir_path + "/*." + img_ext))
                       if int(splitext(basename(elem).split(sep)[-1])[0]) % framerate == 0 and int(
            splitext(basename(elem).split(sep)[-1])[0]) >= start_img]
    all_image_paths.sort(key=lambda img: int(splitext(basename(img).split(sep)[-1])[0]))
    return all_image_paths


def get_annotation_csv(current_dir):
    files_csv = [i for i in listdir(current_dir) if i.endswith('.csv') and i.__contains__("Annotations_Segmentation")]
    annotation_path = files_csv[0] if (len(files_csv) == 1) \
        else getcwd() + "/Annotations_Segmentation [" + datetime.now().strftime('%Y-%m-%d %H_%M_%S') + "].csv"
    return annotation_path


def copy_files_to(src_files, target_dir):
    makedirs(target_dir, exist_ok=True)
    for file_img in src_files:
        copyfile(file_img, join(target_dir, basename(file_img)))
    print("Successfully, copied all ", len(src_files), "files.")


def rename_justify(filenames, just=9, sep='_'):
    for filename in filenames:
        new_name = "{0}{1}{2}".format(sep.join(basename(filename).split(sep)[:-1]), sep,
                                      ((basename(filename).split(sep)[-1]).rjust(just, '0')))
        rename(filename, join(dirname(filename), new_name))


def video_to_images(IMAGE_DIR_PATH, VIDEO_DIR, cur_video, frame_rate=25):
    # global IMAGE_DIR_PATH
    print("image_dir =", IMAGE_DIR_PATH)

    videos_with_sub_dirs = [cur_video]
    just = 5  # size of count e.g. 1 => 00001

    for video_name in videos_with_sub_dirs:
        video_path = VIDEO_DIR + video_name
        print("video_path =", video_path)
        video_capture = cv2.VideoCapture(video_path)
        success, image_frame = video_capture.read()
        counter = 0
        save_dir = IMAGE_DIR_PATH + "/"
        print("save_dir =", save_dir)

        makedirs(save_dir, exist_ok=True)

        with tqdm(total=int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
                  desc="Frame extraction: ") as progressbar:
            while success:
                cur_img_path = save_dir + str(counter).rjust(just, '0') + ".png"
                if counter % frame_rate == 0:
                    cv2.imwrite(cur_img_path, image_frame)  # save frame as JPEG file
                success, image_frame = video_capture.read()
                counter += 1
                progressbar.update(1)
        print("Total Read frame", counter, "successfully")


def json_to_image(json_file, saving_file):
    with open(json_file, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)

    with open(saving_file, "wb") as new_file:
        new_file.write(base64.b64decode(str(json_object['imageData'])))

    # image = base64.b64decode(str(json_object['imageData']))
    # fileName = 'test.png'
    #
    # img = Image.open(io.BytesIO(image))
    # img.save(fileName, 'png')
    # print(json_object['shapes'])
    # print(type(json_object))


class Shape:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.points = []
        self.flags = ""
        self.label = ""
        self.line_color = None
        self.fill_color = None

    def dict(self):
        return self.__dict__


class Label:
    def __init__(self, imagePath):
        self.version = 0.0
        self.flags = None
        self.shapes = []  # list of Shape(shape_type)

        self.lineColor = [0, 255, 0, 128]
        self.fillColor = [255, 0, 0, 128]
        self.imagePath = imagePath
        self.imageData = ""
        self.imageHeight = 0
        self.imageWidth = 0

    def to_json(self, indent=4):
        return json.dumps(self.__dict__, indent=indent)


if __name__ == "__main__":
    #    all_images = get_all_files('/home/dominique/Bilder/FIN18_ss19lat_pov', 1, 0, 'png') # json with 10, png with 9
    #    rename_justify(all_images, 9)
    # json_to_image('Segmented_Images/00025.json', '00025.png')
    # with open('Segmented_Images/FIN18/00025.json', 'r') as openfile:
    #     json_object = json.load(openfile)
    # with open("Segmented_Images/FIN18/simple_label.json", "w") as outfile:
    #     json_object['imageData'] = ""
    #     json.dump(json_object, outfile, indent=4)

    image_annotation = Label("012.png")
    annotation_shape = Shape('unknown')
    annotation_shape.shape_type = "shape type"
    image_annotation.shapes.append(annotation_shape.dict())
    print(image_annotation.to_json())
