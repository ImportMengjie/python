# -*- coding: utf-8 -*-
from tkinter import *
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
from PIL import ImageTk


# deep dream
inception_model = 'data/tensorflow_inception_graph.pb'

# 加载inception模型
graph = tf.Graph()
sess = tf.InteractiveSession(graph=graph)

X = tf.placeholder(np.float32, name='input')
with tf.gfile.FastGFile(inception_model, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
imagenet_mean = 117.0
preprocessed = tf.expand_dims(X-imagenet_mean, 0)
tf.import_graph_def(graph_def, {'input': preprocessed})


def deep_dream(obj, img_noise=np.random.uniform(size=(224, 224, 3)) + 100.0, iter_n=10, step=1.5, octave_n=1, octave_scale=1.4, save_video='', canvas=None, verbose=True):
    vw = None
    if save_video is not None and save_video != '':
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        height = img_noise.shape[0]
        width = img_noise.shape[1]
        vw = cv2.VideoWriter(save_video, fourcc, 20.0, (width, height))

    score = tf.reduce_mean(obj)
    gradi = tf.gradients(score, X)[0]

    img = img_noise
    octaves = []

    def tffunc(*argtypes):
        placeholders = list(map(tf.placeholder, argtypes))

        def wrap(f):
            out = f(*placeholders)

            def wrapper(*args, **kw):
                return out.eval(dict(zip(placeholders, args)), session=kw.get('session'))
            return wrapper
        return wrap

    def resize(img, size):
        img = tf.expand_dims(img, 0)
        return tf.image.resize_bilinear(img, size)[0, :, :, :]

    resize = tffunc(np.float32, np.int32)(resize)
    for _ in range(octave_n-1):
        hw = img.shape[:2]
        lo = resize(img, np.int32(np.float32(hw)/octave_scale))
        hi = img-resize(lo, hw)
        img = lo
        octaves.append(hi)

    def calc_grad_tiled(img, t_grad, tile_size=512):
        sz = tile_size
        h, w = img.shape[:2]
        sx, sy = np.random.randint(sz, size=2)
        img_shift = np.roll(np.roll(img, sx, 1), sy, 0)
        grad = np.zeros_like(img)
        for y in range(0, max(h-sz//2, sz), sz):
            for x in range(0, max(w-sz//2, sz), sz):
                sub = img_shift[y:y+sz, x:x+sz]
                g = sess.run(t_grad, {X: sub})
                grad[y:y+sz, x:x+sz] = g
        return np.roll(np.roll(grad, -sx, 1), -sy, 0)

    for octave in range(octave_n):
        if octave > 0:
            hi = octaves[-octave]
            img = resize(img, hi.shape[:2])+hi
        for _ in range(iter_n):
            g = calc_grad_tiled(img, gradi)
            img += g*(step / (np.abs(g).mean()+1e-7))
            img_array = np.clip(img, 0, 255) .astype(np.uint8)
            if vw is not None:
                print('frame{}'.format(_))
                img_array_copy = img_array.copy()
                cv2.putText(img_array_copy, 'frame:{}'.format(
                    _), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                vw.write(img_array_copy)
            image = Image.fromarray(img_array)
            image = ImageTk.PhotoImage(image)
            canvas.cur_img = image
            canvas.create_image((0, 0), anchor=NW, image=image)
            canvas.update()
    if vw is not None:
        vw.release()


if __name__ == '__main__':
    inception_model = 'data/tensorflow_inception_graph.pb'

    # 加载inception模型
    graph = tf.Graph()
    sess = tf.InteractiveSession(graph=graph)

    X = tf.placeholder(np.float32, name='input')
    with tf.gfile.FastGFile(inception_model, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    imagenet_mean = 117.0
    preprocessed = tf.expand_dims(X-imagenet_mean, 0)
    tf.import_graph_def(graph_def, {'input': preprocessed})

    layers = [op.name for op in graph.get_operations() if op.type ==
              'Conv2D' and 'import/' in op.name]
    print(layers)
    feature_nums = [int(graph.get_tensor_by_name(
        name+':0').get_shape()[-1]) for name in layers]

    print('layers:', len(layers))   # 59
    print('feature:', sum(feature_nums))  # 7548

    # 加载输入图像
    input_img = cv2.imread('input.jpg')
    input_img = np.float32(input_img)

    # 选择层
    layer = 'mixed5b'
    layer = 'conv2d1'
    layer = 'head1_bottleneck_pre_relu'
    deep_dream(graph.get_tensor_by_name(
        "import/%s:0" % layer), input_img)

    """
    'import/conv2d1_pre_relu/conv', 
    'import/conv2d2_pre_relu/conv', 
    'import/mixed3a_1x1_pre_relu/conv', 
    'import/mixed3a_3x3_bottleneck_pre_relu/conv', 
    'import/mixed3a_3x3_pre_relu/conv', 
    'import/mixed3a_5x5_bottleneck_pre_relu/conv', 
    'import/mixed3a_5x5_pre_relu/conv', 
    'import/mixed3a_pool_reduce_pre_relu/conv', 
    'import/mixed3b_1x1_pre_relu/conv', 
    'import/mixed3b_3x3_bottleneck_pre_relu/conv', 
    'import/mixed3b_3x3_pre_relu/conv', 
    'import/mixed3b_5x5_bottleneck_pre_relu/conv', 
    'import/mixed3b_5x5_pre_relu/conv', 
    'import/mixed3b_pool_reduce_pre_relu/conv', 
    'import/mixed4a_1x1_pre_relu/conv', 
    'import/mixed4a_3x3_bottleneck_pre_relu/conv', 
    'import/mixed4a_3x3_pre_relu/conv', 
    'import/mixed4a_5x5_bottleneck_pre_relu/conv', 
    'import/mixed4a_5x5_pre_relu/conv', 
    'import/mixed4a_pool_reduce_pre_relu/conv', 
    'import/mixed4b_1x1_pre_relu/conv', 
    'import/mixed4b_3x3_bottleneck_pre_relu/conv', 
    'import/mixed4b_3x3_pre_relu/conv', 
    'import/mixed4b_5x5_bottleneck_pre_relu/conv', 
    'import/mixed4b_5x5_pre_relu/conv', 
    'import/mixed4b_pool_reduce_pre_relu/conv', 
    'import/mixed4c_1x1_pre_relu/conv', 
    'import/mixed4c_3x3_bottleneck_pre_relu/conv',
    'import/mixed4c_3x3_pre_relu/conv', 
    'import/mixed4c_5x5_bottleneck_pre_relu/conv', 
    'import/mixed4c_5x5_pre_relu/conv', 
    'import/mixed4c_pool_reduce_pre_relu/conv', 
    'import/mixed4d_1x1_pre_relu/conv', 
    'import/mixed4d_3x3_bottleneck_pre_relu/conv', 
    'import/mixed4d_3x3_pre_relu/conv', 
    'import/mixed4d_5x5_bottleneck_pre_relu/conv', 
    'import/mixed4d_5x5_pre_relu/conv', 
    'import/mixed4d_pool_reduce_pre_relu/conv', 
    'import/mixed4e_1x1_pre_relu/conv', 
    'import/mixed4e_3x3_bottleneck_pre_relu/conv', 
    'import/mixed4e_3x3_pre_relu/conv', 
    'import/mixed4e_5x5_bottleneck_pre_relu/conv', 
    'import/mixed4e_5x5_pre_relu/conv', 
    'import/mixed4e_pool_reduce_pre_relu/conv', 
    'import/mixed5a_1x1_pre_relu/conv', 
    'import/mixed5a_3x3_bottleneck_pre_relu/conv', 
    'import/mixed5a_3x3_pre_relu/conv', 
    'import/mixed5a_5x5_bottleneck_pre_relu/conv', 
    'import/mixed5a_5x5_pre_relu/conv', 
    'import/mixed5a_pool_reduce_pre_relu/conv', 
    'import/mixed5b_1x1_pre_relu/conv', 
    'import/mixed5b_3x3_bottleneck_pre_relu/conv', 
    'import/mixed5b_3x3_pre_relu/conv', 
    'import/mixed5b_5x5_bottleneck_pre_relu/conv', 
    'import/mixed5b_5x5_pre_relu/conv', 
    'import/mixed5b_pool_reduce_pre_relu/conv', 
    'import/head0_bottleneck_pre_relu/conv', 
    'import/head1_bottleneck_pre_relu/conv'
    """
