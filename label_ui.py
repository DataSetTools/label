import math
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from util_ui import Label, Shape, DataLoader, CustomDialog, Controller, ResizingCanvas, Util


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)             
        
    def show(self):
        self.lift()


class Setting(Page):
    def __init__(self, parent, controller, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        label = tk.Label(self, text="Settings")
        label.pack(side=tk.TOP, fill=tk.X, expand=1)
        
        self.controller = controller

        self.entry = tk.Entry(master=self, textvariable = tk.StringVar(self, value=self.controller.config.get('in_dir')))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.TRUE)
        self.button_dir = tk.Button(master=self, text="Browse", command=self.input_dir)
        self.button_dir.pack(side=tk.LEFT)
        
    def input_dir(self):     
        dir_ = filedialog.askdirectory()
        self.entry.delete(0,tk.END)
        self.entry.insert(0, dir_)
        
        self.controller.config.update('in_dir', dir_)
        self.controller.dataloaer = DataLoader(self.controller.config.get('in_dir'), self.controller.config.get('out_dir'))
        self.controller.img_path = self.controller.dataloaer.current()



class Labeling(Page):
    def __init__(self, parent, controller, *args, **kwargs):
        Page.__init__(self, parent, *args, **kwargs)
        self.current = None
        self.undoes = []
        self.olds_coordinates = []
        self.circle = 0
        self.radius = 10  # change this for the size of your circle
        self.line_id = None
        self.old_coordinate = None, None
        self.shape_origin_coordinate = None        
        
        self.controller = controller
        self.controller.dataloaer = DataLoader(self.controller.config.get('in_dir'), self.controller.config.get('out_dir'))
        self.controller.img_path = self.controller.dataloaer.current()
        self.image_annotation = Label(self.controller.img_path)
        self.annotation_shape = Shape()
        self.label = tk.Label(self, text="Labeling Tool")
        self.label.pack(side="top", fill="both", expand=0)

        self.image_ = Image.new('RGB', (300, 400)) #Image.open(self.controller.img_path)
        self.photo = ImageTk.PhotoImage(self.image_)
        self.canvas = ResizingCanvas(self, bd=0, highlightthickness=0)
        self.pack(fill=tk.BOTH, expand=1)

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Motion>", self.moved)
        self.bind("<Configure>", self.resize)
        
        self.image_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW, tags=('all', 'img'))
        # print(self.image_canvas, "Anfang")

    def put_image(self):
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.image_ = Image.open(self.controller.img_path)
        self.image_annotation.imageWidth, self.image_annotation.imageHeight = self.image_.size
        # self.image_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        #self.canvas.delete("all")
        self.photo = ImageTk.PhotoImage(self.image_.resize(self.controller.size, Image.ANTIALIAS))
        self.canvas.itemconfig(self.image_canvas, image = self.photo)
        # print(self.image_canvas, "Später")
        self.lift()

    def clicked(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.annotation_shape.points.append([x, y])
        
        self.old_coordinate = x, y
        self.undoes.append(self.line_id)

        self.line_id = None    # keep line on canvas
        self.canvas.addtag_all("all")    # used for resizing elemnets on canvas
        self.canvas.delete(self.circle)  # to refresh the circle each motion

        if self.shape_origin_coordinate:
            x1, y1 = self.shape_origin_coordinate
            dist = math.hypot(x - x1, y - y1)
            if dist < self.radius:                
                self.old_coordinate = -(len(self.image_annotation.shapes)+1), None
                self.olds_coordinates.append(self.old_coordinate)
                self.annotation_shape.label = CustomDialog(self).show()
                self.controller.zoom = (self.image_.size[0]/self.controller.size[0], self.image_.size[1]/self.controller.size[1])
                #self.annotation_shape.resize(self.controller.zoom)
                self.image_annotation.add_shape(self.annotation_shape)
                self.shape_origin_coordinate = None
            else:
                self.olds_coordinates.append(self.old_coordinate) 
        else:
            self.shape_origin_coordinate = x, y
            self.olds_coordinates.append(self.old_coordinate)

    def moved(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.current = x, y

        if self.line_id:
            self.canvas.delete(self.line_id)

        if self.old_coordinate[1]:
            x1, y1 = self.old_coordinate
            self.line_id = self.canvas.create_line(x, y, x1, y1, fill='green', activewidth=1, smooth=False, tags=('all', 'line'))

        if self.shape_origin_coordinate:
            x1, y1 = self.shape_origin_coordinate
            dist = math.hypot(x - x1, y - y1)

            self.canvas.delete(self.circle)  # to refresh the circle each motion
            if dist < self.radius:
                self.circle = self.canvas.create_oval(x + self.radius, y + self.radius, x - self.radius,
                                                      y - self.radius, outline="tomato")
                self.canvas.delete(self.line_id)
                if self.old_coordinate[1]:
                    x, y = self.old_coordinate
                    x1, y1 = self.shape_origin_coordinate
                    self.line_id = self.canvas.create_line(x, y, x1, y1, fill='green2', activewidth=1, smooth=False, tags=('all', 'line'))

    def save(self):
        self.image_annotation.save_json(self.controller.zoom)
        
    def open_ing(self):        
        self.controller.dataloaer = DataLoader('')
        self.controller.img_path = self.controller.dataloaer.current()
        self.image_annotation = Label(self.controller.img_path)
        self.put_image()

    def next(self):
        self.canvas.delete("line")
        self.controller.img_path = self.controller.dataloaer.next()
        self.image_annotation = Label(self.controller.img_path)
        self.put_image()
        
    def prev(self):
        self.canvas.delete("line")
        self.controller.img_path = self.controller.dataloaer.prev()
        self.image_annotation = Label(self.controller.img_path)
        self.put_image()

    def undo(self):
        if self.olds_coordinates and (self.olds_coordinates[-1][0]) < 0.0:
            self.shape_origin_coordinate = self.image_annotation.first_point()
            self.image_annotation.del_shape(-1)                
            # print('0 #### removed last shape')
            
        if self.undoes and self.olds_coordinates:
            self.canvas.delete(self.undoes[-1])
            del self.undoes[-1]
            del self.olds_coordinates[-1]
            if self.olds_coordinates:
                self.old_coordinate = self.olds_coordinates[-1]
                if self.line_id:
                    x1, y1 = self.current
                    x, y = self.old_coordinate
                    self.canvas.delete(self.line_id)
                    if Util.ands([x,y,x1,y1]):
                        self.line_id = self.canvas.create_line(x, y, x1, y1, fill='green', activewidth=1, smooth=False, tags=('all', 'line'))
            else:
                self.shape_origin_coordinate = None
                self.old_coordinate = None, None
            # print('1 #### removed last point/click')
 

    def resize(self, event):        
        self.controller.size = (event.width, event.height)
        self.controller.zoom = (self.image_.size[0]/self.controller.size[0], self.image_.size[1]/self.controller.size[1])
        # self.annotation_shape.resize(self.controller.zoom)
        #self.image_annotation.resize(self.controller.zoom)
        #Util.mul(self.olds_coordinates, self.controller.zoom)
        
        resized = self.image_.resize(self.controller.size, Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(resized)
        self.canvas.itemconfig(self.image_canvas, image = self.photo)
        self.controller.zoom = (self.image_.size[0]/self.controller.size[0], self.image_.size[1]/self.controller.size[1])
        # print(self.image_canvas, "In zoom")
        

class Help(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="Help Page")
        label.pack(side="top", fill="both", expand=True)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.controller = Controller()
        setting = Setting(self, self.controller)
        labeling = Labeling(self, self.controller)
        help_ = Help(self)

        button_frame = tk.Frame(self)
        container = tk.Frame(self)
        button_frame.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        setting.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        labeling.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        help_.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(button_frame, text="Setting", command=setting.lift)
        b2 = tk.Button(button_frame, text="Labeling", command=labeling.put_image)
        b3 = tk.Button(button_frame, text="Help", command=help_.lift)
        b4 = tk.Button(button_frame, text="Save", command=labeling.save)
        b5 = tk.Button(button_frame, text="Open Image", command=labeling.open_ing)
        b6 = tk.Button(button_frame, text="Previous", command=labeling.prev)
        b7 = tk.Button(button_frame, text="Next", command=labeling.next)
        b8 = tk.Button(button_frame, text="Undo", command=labeling.undo)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")
        b5.pack(side="left")
        b6.pack(side="left")
        b7.pack(side="left")
        b8.pack(side="left")

        setting.show()


if __name__ == "__main__":
    app = tk.Tk()
    main = MainView(app)
    main.pack(side="top", fill="both", expand=True)
    app.title("Labeling")
    app.geometry('1280x768')
    app.minsize(400, 326) 
    app.mainloop()