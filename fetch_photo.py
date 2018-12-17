# encoding: utf-8
import base64
import json
import urllib3
import urllib.parse
import time
import os
def fetch_image(keyword):
    key_word = urllib.parse.urlencode({'q':keyword},encoding='utf-8')
    access_keys= "YOUR_AZURE_ACCESS_KEY"
    headers = {'Ocp-Apim-Subscription-Key': access_keys}
    url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search?%s&count=10&offset=0&mkt=en-us&safeSearch=Moderate" % key_word
    http = urllib3.PoolManager()
    photo_search = http.request('GET', url, headers=headers)
    results = json.loads(str(photo_search.data,encoding='utf-8'))

    for i in os.listdir("tmp/"): os.remove(os.path.join('tmp/',i))
    i = 0
    for result in results['value']:
        img_url = result['thumbnailUrl']
        img_data = http.request('GET',img_url)
        with open('tmp/%d.jpg' % i,'wb') as img_file:
            img_file.write(img_data.data)
        i += 1


def fetch_image_baidu(keyword):
    key_word = urllib.parse.urlencode({'word': keyword,'queryWord':keyword}, encoding='utf-8')
    url = "https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&cl=2&lm=-1" \
        "&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&" \
            "expermode=&selected_tags=&pn=0&rn=10&gsm=3c&%s" % key_word
    http = urllib3.PoolManager()
    photo_search = http.request('GET', url)
    results = json.loads(str(photo_search.data, encoding='utf-8'))
    for i in os.listdir("tmp/"): os.remove(os.path.join('tmp/', i))
    i = 0
    for result in results['data']:
        if 'thumbURL' in result:
            img_url = result['thumbURL']
            img_data = http.request('GET',img_url)
            with open('tmp/%d.jpg' % i,'wb') as img_file:
                img_file.write(img_data.data)
            i += 1
