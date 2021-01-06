import base64
import math
import tkinter as tk
import cv2 as cv
import sys
from PIL import Image
from PIL import ImageTk
import json
from os.path import splitext


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.img_path = "/home/dominique/Bilder/predict1.png"
        self.img_path = "Segmented_Images/FIN18/100.png"

    def show(self):
        self.lift()


class Setting(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Settings Seit")
        label.pack(side="top", fill="both", expand=True)


class Labeling(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.undoes = []
        self.olds_coordinates = []
        self.circle = 0
        self.radius = 10  # change this for the size of your circle
        self.line_id = None
        self.old_coordinate = None
        self.shape_origin_coordinate = None
        self.image_annotation = Label(self.img_path)
        self.annotation_shape = Shape()
        self.label = tk.Label(self, text="Labeling Tool")
        self.label.pack(side="top", fill="both", expand=True)

        self.cv_img = cv.cvtColor(cv.imread(self.img_path), cv.COLOR_BGR2RGB)
        self.height, self.width, no_channels = self.cv_img.shape
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        # self.canvas.grid(column=0, row=1, sticky='nwes')

        self.image_annotation.imageWidth = self.width
        self.image_annotation.imageHeight = self.height

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Motion>", self.moved)

    def put_image(self):
        # self.cv_img = cv.cvtColor(cv.imread("/home/dominique/Bilder/predict1.png"), cv.COLOR_BGR2RGB)
        # self.height, self.width, no_channels = self.cv_img.shape
        # self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.photo = ImageTk.PhotoImage(file=self.img_path)  # image=Image.fromarray(self.cv_img))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.lift()

    def clicked(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.annotation_shape.points.append([x, y])
        self.annotation_shape.points.append([x, y])

        if self.shape_origin_coordinate:
            x1, y1 = self.shape_origin_coordinate
            dist = math.hypot(x - x1, y - y1)
            if dist > self.radius:
                self.old_coordinate = x, y
            else:
                self.object_label()
                # x1, y1 = self.shape_origin_coordinate
                # self.line_id = self.canvas.create_line(x, y, x1, y1, fill='green', activewidth=4, smooth=True)
                self.old_coordinate = None
                self.shape_origin_coordinate = None
        else:
            self.old_coordinate = x, y
            self.shape_origin_coordinate = x, y

        self.undoes.append(self.line_id)
        self.olds_coordinates.append(self.old_coordinate)

        self.line_id = None
        self.canvas.delete(self.circle)  # to refresh the circle each motion

        # Some test
        # s = "Last point clicked at x=%s  y=%s" % (x, y)
        # self.label['text'] = s

    def moved(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        if self.line_id:
            self.canvas.delete(self.line_id)

        if self.old_coordinate:
            x1, y1 = self.old_coordinate
            self.line_id = self.canvas.create_line(x, y, x1, y1, fill='green', activewidth=4, smooth=True)

        if self.shape_origin_coordinate:
            x1, y1 = self.shape_origin_coordinate
            dist = math.hypot(x - x1, y - y1)

            self.canvas.delete(self.circle)  # to refresh the circle each motion
            if dist < self.radius:
                self.circle = self.canvas.create_oval(x + self.radius, y + self.radius, x - self.radius, y - self.radius, outline="tomato")
                self.canvas.delete(self.line_id)
                x2, y2 = self.old_coordinate
                x1, y1 = self.shape_origin_coordinate
                self.line_id = self.canvas.create_line(x2, y2, x1, y1, fill='green', activewidth=4, smooth=True)

        # Some test
        # s = "Cursor at x=%s  y=%s" % (x, y)
        # print(s)
        # self.label['text'] = s

    def save(self):
        my_json = self.image_annotation.dict()
        with open(splitext(self.image_annotation.imagePath)[0] + ".json", "w") as write_file:
            json.dump(my_json, write_file, indent=4)
        print(my_json)
        # print(self.image_annotation.to_json())

    def object_label(self):
        self.annotation_shape.label = 'Person'
        self.image_annotation.shapes.append(self.annotation_shape.dict().copy())
        self.annotation_shape = Shape()
        # print(self.image_annotation.to_json())

    def next(self):
        self.img_path = "Segmented_Images/FIN18/150.png"
        self.put_image()

    def undo(self):
        if len(self.undoes) > 0:
            self.canvas.delete(self.undoes[-1])
            del self.undoes[-1]
        if len(self.olds_coordinates) > 1:
            del self.olds_coordinates[-1]
            self.old_coordinate = self.olds_coordinates[-1]
        if len(self.olds_coordinates) == 1:
            self.old_coordinate = None



class Hilfe(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Help Page")
        label.pack(side="top", fill="both", expand=True)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        setting = Setting(self)
        labeling = Labeling(self)
        hilfe = Hilfe(self)

        button_frame = tk.Frame(self)
        container = tk.Frame(self)
        button_frame.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        setting.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        labeling.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        hilfe.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(button_frame, text="Setting", command=setting.lift)
        b2 = tk.Button(button_frame, text="Labeling", command=labeling.put_image)
        b3 = tk.Button(button_frame, text="Help", command=hilfe.lift)
        b4 = tk.Button(button_frame, text="Save", command=labeling.save)
        b5 = tk.Button(button_frame, text="Object label", command=labeling.object_label)
        b6 = tk.Button(button_frame, text="Next", command=labeling.next)
        b7 = tk.Button(button_frame, text="Undo", command=labeling.undo)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")
        b5.pack(side="left")
        b6.pack(side="left")
        b7.pack(side="left")

        setting.show()


class Shape:
    def __init__(self, shape_type='polygon'):
        self.label = ""
        self.line_color = None
        self.fill_color = None
        self.points = []
        self.shape_type = shape_type
        self.flags = {}

    def dict(self):
        return self.__dict__


class Label:
    def __init__(self, imagePath):
        self.version = '1.0'
        self.flags = {}
        self.shapes = []  # list of Shape(shape_type)

        self.lineColor = [0, 255, 0, 128]
        self.fillColor = [255, 0, 0, 128]
        self.imagePath = imagePath
        self.imageData = ''
        self.imageHeight = 1
        self.imageWidth = 1

    def to_json(self, indent=4):
        with open(self.imagePath, "rb") as imageFile:
            self.imageData = base64.b64encode(imageFile.read()).decode('utf-8')
        return json.dumps(self.__dict__, indent=indent)

    def dict(self):
        with open(self.imagePath, "rb") as imageFile:
            self.imageData = base64.b64encode(imageFile.read()).decode('utf-8')
        return self.__dict__


if __name__ == "__main__":
    print(cv.__version__)
    app = tk.Tk()
    main = MainView(app)
    main.pack(side="top", fill="both", expand=True)
    app.title("Labeling")
    app.geometry('1280x768')
    app.mainloop()
