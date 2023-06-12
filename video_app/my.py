import requests

import json


yt_vidio = 'https://www.youtube.com/watch?v=qux4-yWZvo'

r = requests.get(f"https://www.youtube.com/oembed?format=json&url={yt_vidio}")

data = r.text

try:

    data = json.loads(data)
    print
except Exception as e:
    print(e)