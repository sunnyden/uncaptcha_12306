from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import requests
from PIL import Image
import json
import base64
import os
import random


import argparse
import os.path
import re
import sys
import tarfile
import glob

import numpy as np
from six.moves import urllib
import tensorflow as tf

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import base64
import json
import urllib3
import certifi
import time
from fetch_photo import fetch_image_baidu
from classify import classify

_g_access_token = None

def get_baidu_token():
    global _g_access_token
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
    secret_key = "YOUR_BAIDU_API_SECRET"
    api_key = "YOUR_BAIDU_API_KEY"
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s" % \
          (api_key, secret_key)
    token_request = http.request('GET', url)
    _g_access_token = json.loads(str(token_request.data, encoding='utf-8'))['access_token']


def recog_chinese():
    global _g_access_token
    if _g_access_token is None: get_baidu_token()
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
    ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=%s" % _g_access_token
    with open("images/label.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    recog = http.request_encode_body('POST', ocr_url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                     encode_multipart=False,
                                     fields={'image': encoded_string, 'probability': 'true'})
    resp = json.loads(str(recog.data, encoding='utf-8'))
    if resp['words_result_num'] == 0:
        print("recognition failed")
        return "N/A"
    return resp['words_result'][0]['words']



def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with tf.gfile.FastGFile('model.pb', 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')


def run_inference_on_image(images, count, add_id = True):
  """Runs inference on an image.
  Args:
    images: Path to image files.
    count: number of the images.
    add_id: whether or not adding label in the returned array
  Returns:
    array of logits from different images
  """
  # Creates graph from saved GraphDef.
  predictions_arr = []
  for i in range(count):
      if not tf.gfile.Exists(os.path.join(images,"%d.jpg" % i)):
        tf.logging.fatal('File does not exist %s', os.path.join(images,"%d.jpg" % i))
      image_data = tf.gfile.FastGFile(os.path.join(images,"%d.jpg" % i), 'rb').read()
      print(os.path.join(images,"%d.jpg" % i))
      with tf.Session() as sess:
        # Some useful tensors:
        # 'softmax:0': A tensor containing the normalized prediction across
        #   1000 labels.
        # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
        #   float description of the image.
        # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
        #   encoding of the image.
        # Runs the softmax tensor by feeding the image_data as input to the graph.
        softmax_tensor = sess.graph.get_tensor_by_name('pool_3:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions_arr.append(np.squeeze(predictions).tolist())
        if add_id:
            predictions_arr[-1].insert(0, i)
  return predictions_arr

def getCaptcha():
    '''return (rawimage, cookies)'''
    r = requests.get('https://kyfw.12306.cn/passport/captcha/captcha-image64', cookies=dict())
    j = json.loads(r.content)
    if int(j['result_code']) != 0:
        raise ValueError('#%d: %s' % (int(j['result_code']), j['result_message']))
    img = base64.b64decode(j['image'])
    return img, dict(r.cookies)


def checkCaptcha(answer, cookies):
    '''answer: index in picture (i.e. [0, 1, ... 7])'''

    def safeGauss(mu, sigma):
        '''return val in [mu - 3 * sigma, mu + 3 * sigma]'''
        r = random.gauss(0, sigma)
        if r > 3 * sigma:
            r = 3 * sigma
        elif r < -3 * sigma:
            r = -3 * sigma
        return r + mu

    def indexToXy(answer):
        '''from index to xy, with some random'''
        xys = []
        for i in answer:
            x = (i % 4) * 72 + 38
            y = (i // 4) * 72 + 44
            xys.append(str(int(safeGauss(x, 6))))
            xys.append(str(int(safeGauss(y, 6))))
        return ','.join(xys)

    answer_xy = indexToXy(answer)
    r = requests.get('https://kyfw.12306.cn/passport/captcha/captcha-check',
                     params={'answer': answer_xy},
                     cookies=cookies)
    j = json.loads(r.content)
    return int(j['result_code']), j['result_message']


def crop_image():
    im = Image.open('test.jpg')
    for i in os.listdir("images/"): os.remove(os.path.join('images/', i))
    x, y = 5, 41
    im.crop((x, y, x + 67, y + 67)).save("images/0.jpg")
    x, y = 77, 41
    im.crop((x, y, x + 67, y + 67)).save("images/1.jpg")
    x, y = 149, 41
    im.crop((x, y, x + 67, y + 67)).save("images/2.jpg")
    x, y = 221, 41
    im.crop((x, y, x + 67, y + 67)).save("images/3.jpg")
    x, y = 5, 113
    im.crop((x, y, x + 67, y + 67)).save("images/4.jpg")
    x, y = 77, 113
    im.crop((x, y, x + 67, y + 67)).save("images/5.jpg")
    x, y = 149, 113
    im.crop((x, y, x + 67, y + 67)).save("images/6.jpg")
    x, y = 221, 113
    im.crop((x, y, x + 67, y + 67)).save("images/7.jpg")
    x, y = 118, 2
    im.crop((x, y, x + 56, y + 22)).save("images/label.jpg")


def main(_):
    img, cookies = getCaptcha()
    with open('test.jpg', 'wb') as f:
        f.write(img)
    crop_image()
    create_graph()
    chinese = recog_chinese()
    fetch_image_baidu(chinese)
    img = mpimg.imread('test.jpg')
    plt.imshow(img)
    plt.show()
    result = run_inference_on_image("images/",8)
    for item in result:
        print(item)
    result_reference = run_inference_on_image("tmp/",10,add_id=False)
    for item in result_reference:
        print(item)
    res = classify(result, result_reference)
    print('Check "test.jpg"')
    print(chinese)
    (code, msg) = checkCaptcha(res, cookies)
    if code != 4:
        print('Error #%d: %s' % (code, msg))
    else:
        print('Pass!')


if __name__ == '__main__':
    tf.app.run(main=main, argv=[sys.argv[0]])
