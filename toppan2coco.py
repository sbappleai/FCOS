#
"""
Toppan tomato dataset形式をCOCO形式にする

ref: https://qiita.com/harmegiddo/items/da131ae5bcddbbbde41f
"""

import argparse
import json
import os
import csv
import glob
from collections import OrderedDict
from turtle import width

from PIL import Image
import tqdm

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('srcdir')
    args = p.parse_args()
    return args

def info():
    info = OrderedDict()
    info['description'] = 'SBAppleAI 2021 winter'
    info['url'] = 'https://github.com/sbappleai/SBAppleAI/'
    info['version'] = '1.00'
    info['year'] = 2021
    info['contributor'] = 'Toppan printing Co., Ltd'
    info['data_created'] = '2022/01/07'
    return info

def license():
    li = OrderedDict()
    li['id'] = 1
    li['url'] = 'https://github.com/sbappleai/SBAppleAI/'
    li['name'] = 'Toppan'
    return li

def get_image_size(img_fname):
    img = Image.open(img_fname)
    return img.width, img.height

def conv_float2pos(center_x, center_y, w, h, img_width, img_height):
    x = center_x - w / 2
    y = center_y - h / 2
    ret_x = int(x * img_width)
    ret_y = int(y * img_height)
    ret_w = int(w * img_width)
    ret_h = int(h * img_height)
    return ret_x, ret_y, ret_w, ret_h

def has_label(fname):
    basedir, basename = os.path.split(fname)
    basename = os.path.splitext(basename)[0]
    labelname = f'{basedir}/{basename}.csv'
    if not os.path.exists(labelname):
        return False
    bboxes = []
    img_width, img_height = get_image_size(fname)
    # ref: https://github.com/sbappleai/SBAppleAI/issues/74#issuecomment-871083033
    with open(labelname) as f:
        for line in f:
            vals = [float(v) for v in line.strip().split(',')]
            l, x, y, w, h = (vals[-1], vals[2], vals[3], vals[4], vals[5])
            l = int(l)
            ix, iy, iw, ih = conv_float2pos(x, y, w, h, img_width, img_height)
            bboxes.append((ix, iy, iw, ih, l))
    return bboxes

def images(basedir):
    imgs = []
    annos = []
    idx = 0
    a_idx = 0
    # files = glob.glob(os.path.join(basedir, 'images/*.jpg'))
    files = glob.glob(os.path.join(basedir, '*.jpg'))
    for fname in tqdm.tqdm(files):
        bbox = has_label(fname)
        if bbox is False or len(bbox) == 0: # csvがない or 空
            continue
        idx += 1
        ii = OrderedDict()
        ii['license'] = 1
        ii['id'] = idx
        ii['file_name'] = os.path.basename(fname)
        img = Image.open(fname)
        ii['width'] = str(img.width)
        ii['height'] = str(img.height)
        del img
        ii['date_captured'] = '2021-11-20 12:00:00'
        ii['coco_url'] = ''
        ii['flickr_url'] = ''
        imgs.append(ii)
        for bx in bbox:
            a_idx += 1
            an = OrderedDict()
            an['segmentation'] = []
            an['area'] = 0
            an['iscroud'] = 0
            an['image_id'] = idx
            an['bbox'] =[bx[0], bx[1], bx[2], bx[3]]
            an['category_id'] = bx[4]
            an['id'] = a_idx
            annos.append(an)
    return imgs, annos

def categories():
    spc = 'object'
    cats = [ 'IDX_FOREGROUND',
'IDX_IPHONE',
'IDX_IPAD',
'IDX_PRICE',
'IDX_POP',
'IDX_BP1',
'IDX_BP2',
'IDX_BP3',
'IDX_BP4',
'IDX_BP5',
'IDX_BP6',
'IDX_BP7',
'IDX_BP8',
'IDX_BP9',
'IDX_BP10',
'IDX_BP11',
'IDX_BP12',
'IDX_BP13',
'IDX_BP14',
'IDX_BP15']

    cs = []
    idx = 0
    for i in range(len(cats)):
        idx += 1
        ci = OrderedDict()
        ci['id'] = idx
        ci['supercategory'] = spc
        ci['name'] = cats[i]
        cs.append(ci)
    return cs

def main():
    args = get_args()
    jdata = OrderedDict()
    jinfo = info()
    jdata['info'] = jinfo
    jlic = license()
    jdata['licenses'] = [jlic]
    jimage, janno = images(args.srcdir)
    jdata['images'] = jimage
    jdata['annotations'] = janno
    jcat = categories()
    jdata['categories'] = jcat
    print(json.dumps(jdata))

if __name__ == '__main__':
    main()
