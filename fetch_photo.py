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
