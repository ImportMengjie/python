from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
from PIL import ImageTk
import dream
from dream import *


def select_img_path(*args):
    filename = filedialog.askopenfilename()
    img_path.set(filename)
    img = cv2.imread(filename)
    mainloop.row_img_array = img
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    mainloop.row_img = img
    row_img_canvas.height = img.height()
    row_img_canvas.width = img.width()
    width = img.width()
    height = img.height()
    row_img_canvas.config(width=width, height=height)
    new_img_canvas.config(width=width, height=height)

    row_img_canvas.create_image((0, 0), anchor=NW, image=img)
    row_img_canvas.update()
    new_img_canvas.create_image((0, 0), anchor=NW, image=img)
    new_img_canvas.update()


def select_save_video_path(*args):
    filename = filedialog.asksaveasfilename()
    video_path.set(filename)


def start_dream(*args):
    _select_layers_name = select_layers_name.get()
    _loop_nums = loop_nums.get()
    _verbose = verbose.get()
    _img_path = img_path.get()
    _video_path = video_path.get()
    img = cv2.imread(_img_path)
    img = np.float32(img)
    dream.deep_dream(graph.get_tensor_by_name("import/%s:0" % _select_layers_name),
                     img, save_video=_video_path, verbose=_verbose, iter_n=_loop_nums, canvas=new_img_canvas)


if __name__ == '__main__':

    layers = [op.name for op in graph.get_operations() if op.type ==
              'Conv2D' and 'import/' in op.name]
    feature_nums = [int(graph.get_tensor_by_name(
        name+':0').get_shape()[-1]) for name in layers]

    can_select_layers = []
    for layer in layers:
        if 'mixed' in layer:
            short_layer_name = layer[layer.find('mixed'):layer.find('_')]
            if short_layer_name not in can_select_layers:
                can_select_layers.append(short_layer_name)
    can_select_layers.insert(0, 'conv2d1')
    can_select_layers.insert(1, 'conv2d2')
    can_select_layers.append('head0_bottleneck_pre_relu')
    can_select_layers.append('head1_bottleneck_pre_relu')

    # gui
    root = Tk()
    root.title("visualization")
    select_layers_name = StringVar()
    loop_nums = IntVar(value=1000)
    verbose = BooleanVar(value=True)
    img_path = StringVar()
    video_path = StringVar()

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    ttk.Label(mainframe, text="select layer").grid(
        column=1, row=1, sticky=(W, E))
    comboxlist = ttk.Combobox(
        mainframe, textvariable=select_layers_name)  # 初始化
    comboxlist["values"] = can_select_layers
    comboxlist.current(0)  # 选择第一个
    comboxlist.grid(column=2, row=1, sticky=(W, E))
    ttk.Label(mainframe, text="iteration times").grid(
        column=3, row=1, sticky=(W, E))
    Entry(mainframe, width=10, textvariable=loop_nums).grid(
        column=4, row=1, sticky=(W, E))
    ttk.Label(mainframe, text="verbose").grid(
        column=5, row=1, sticky=(W, E))
    ttk.Checkbutton(mainframe, variable=verbose).grid(
        column=6, row=1, sticky=(W, E))

    ttk.Button(mainframe, text="choose img", command=select_img_path).grid(
        column=1, row=2, sticky=(W, E))
    Entry(mainframe, textvariable=img_path).grid(
        column=2, row=2, sticky=(W, E))

    ttk.Button(mainframe, text="input save video path",
               command=select_save_video_path).grid(column=3, row=2, sticky=(W, E))
    Entry(mainframe, textvariable=video_path).grid(
        column=4, row=2, sticky=(W, E))

    ttk.Button(mainframe, text="start",
               command=start_dream).grid(column=5, row=2, sticky=(W, E))

    row_img_canvas = Canvas(mainframe)
    row_img_canvas.grid(column=1, row=3, sticky=(W, E))
    new_img_canvas = Canvas(mainframe)
    new_img_canvas.grid(column=4, row=3, sticky=(W, E))

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.mainloop()
