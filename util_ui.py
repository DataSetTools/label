# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 16:31:45 2021

@author: Dominique
"""
from base64 import b64encode
import re
from imghdr import what
from json import dump, dumps
from pathlib import Path
from os.path import join, splitext, basename, exists, dirname
from os import walk, stat
from glob import glob
from copy import deepcopy
from configparser import SafeConfigParser
from tkinter import filedialog, Canvas

class Shape:
    def __init__(self, shape_type='polygon'):
        self.label = ""
        self.line_color = None
        self.fill_color = None
        self.points = []
        self.shape_type = shape_type
        self.flags = {}
        
    def clear(self):
        self.points = []
        self.label = ""
        
    def resize(self, zoom):
        self.points = [[a * b for a, b in zip(point , zoom)] for point in self.points] 
        # list(map(lambda x,y:x*y, self.points, zoom))


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
        
    def add_shape(self, shape):
        self.shapes.append(deepcopy(shape))  # shape.copy())
        shape.clear()
        
    def del_shape(self, idx):
        if self.shapes:
            del self.shapes[idx]
        
    def first_point(self):
        if self.shapes and self.shapes[0].points:
            # print('1st pt:', self.shapes[-1].points[0], [s.points for s in self.shapes])
            return self.shapes[-1].points[0]
        return None

    def resize(self, zoom):
        if zoom and self.shapes:
            for shape in self.shapes:
                shape.resize(zoom)
                
    def save_json(self, zoom=None, path=''):
        c_shapes = deepcopy(self.shapes)
        self.resize(zoom=zoom)
        with open(self.imagePath, "rb") as imageFile:
            self.imageData = b64encode(imageFile.read()).decode('utf-8')
            
        with open(Path(self.imagePath).with_suffix(".json"), "w") as write_file:
            dump(self, write_file, indent=4, default=lambda o: o.__dict__)
        print(Path(self.imagePath).with_suffix(".json"))
        self.shapes = c_shapes
        # print(as_dict)
        
    def to_json(self, indent=4):
        return dumps(self.__dict__, indent=indent)
    
    def save_json_without_img(self, path=''):
        with open(Path(self.imagePath).with_suffix(".json"), "w") as write_file:
            dump(self, write_file, indent=4, default=lambda o: o.__dict__)
        print(Path(self.imagePath).with_suffix(".json"))
        # print(json.dump(self, write_file, indent=4, default=lambda o: o.__dict__))
        
    def to_json_with_img(self, indent=4):
        with open(self.imagePath, "rb") as imageFile:
            self.imageData = b64encode(imageFile.read()).decode('utf-8')
        return dumps(self.__dict__, indent=indent)

    def dict(self):
        with open(self.imagePath, "rb") as imageFile:
            self.imageData = b64encode(imageFile.read()).decode('utf-8')
        return self.__dict__


class DataLoader:
    def __init__(self, input_dir, output_dir=''):
        self.input_dir = input_dir
        self.output_dir = input_dir if output_dir else output_dir
        self.imageFiles = None        
        self.index = 0 
        self.__len__ = 0
        self.init_files()
        
    def init_files(self):
        if not self.input_dir:
            img_list = filedialog.askopenfilenames(title='Select images', filetypes=[
                    ("image", ".jpeg"),
                    ("image", ".png"),
                    ("image", ".jpg"),
                ])
            self.imageFiles = img_list
            self.input_dir = dirname(img_list[0])
            self.output_dir = dirname(img_list[0])
            self.imageFiles = img_list
        else:            
            self.imageFiles = [join(self.input_dir, fn) for fn in next(walk(self.input_dir))[2]]
        self.imageFiles = [file for file in self.imageFiles if what(file)]
        self.__len__ = len(self.imageFiles)
    
    def next(self):
        self.index = 0 if self.__len__==self.index+1 else self.index+1
        return self.imageFiles[self.index]
        
    def prev(self):
        self.index = self.__len__-1 if 0 ==self.index else self.index-1
        return self.imageFiles[self.index]
    
    def current(self):
        return self.imageFiles[self.index]
    
    def sort(self, sep='_', last=0, reversed=True):
        if sep:
            return sorted(self.imageFiles, key=lambda file:int(splitext(basename(file).split(sep)[-1])[0]), reverse=reversed)
        
        if last:
            last = int(last)
            return sorted(self.imageFiles, key=lambda file: file[-last], reverse=reversed)
            
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(self.imageFiles, key = alphanum_key)
        
    def get_all_files(self, image_dir_path, framerate=25, start_img=0, img_ext="png", sep='_'):
        all_image_paths = [elem for idx, elem in enumerate(glob(image_dir_path + "/*." + img_ext))
                           if int(splitext(basename(elem).split(sep)[-1])[0]) % framerate == 0 and int(
                splitext(basename(elem).split(sep)[-1])[0]) >= start_img]
        all_image_paths.sort(key=lambda img: int(splitext(basename(img).split(sep)[-1])[0]))
        return all_image_paths


class Config:   
    def __init__(self):       
        self.cfg = 'label.ini'
        self.config = SafeConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]}) # configparser.ConfigParser()
        if not exists(self.cfg) or stat(self.cfg).st_size == 0:
            with open(self.cfg, 'w') as configfile:
                self.config.write(configfile)
        
    def get(self, key):
        self.config.read(self.cfg)
        return self.config['USER'].get(key) # self.config['DEFAULT']['in_dir']
    
    def update(self, key, value):
        if value:
            self.config.read(self.cfg)
            self.config.set('USER', key, value)
            with open(self.cfg, 'w') as configfile:
                self.config.write(configfile)
                
    def getlist(self, key):
        self.config.read(self.cfg)
        return self.config['USER'].getlist(key)
                
    def getlist_(self, option, sep=',', chars=None):
        """Return a list from a ConfigParser option. By default, 
           split on a comma and strip whitespaces."""
        return [ chunk.strip(chars) for chunk in option.split(sep) ]
                

import tkinter as tk

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, prompt="Choose class"):
        tk.Toplevel.__init__(self, parent)
        
        self.title(prompt)
        self.attributes('-toolwindow', True)
        self.minsize(120, 100) 

        self.ok_button = tk.Button(self, text="Submit", command=self.on_ok)        
        self.ok_button.pack(side="bottom")
        
        self.options = parent.controller.config.getlist('labels')          
        self.v = tk.IntVar()
        for i, option in enumerate(self.options):
            tk.Radiobutton(self, text=option, variable=self.v, value=i).pack(anchor="w")
        # self.entry.bind("<Return>", self.on_ok)

    def on_ok(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.options[self.v.get()]
    
class Controller:
    def __init__(self):
        self.dataloaer = None        
        self.config = Config()
        self.img_path = None
        self.size = (400, 300)
        self.zoom = (1,1)
        
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)
        
class Util:
    def mul(points, zoom, res=''):
        if res == '':
            points = [[a * b for a, b in zip(point , zoom)] for point in points]
        else:
            return [[a * b for a, b in zip(point , zoom)] for point in points]
        
    def ands(elements):
        for el in elements:
            if not el:
                return False
        return True