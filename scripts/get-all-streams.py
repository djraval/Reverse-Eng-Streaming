# Fetch all channel ids from App using the /channels endpoint and then fetch the stream info for each channel

import requests
import json

# Fetch all channel ids
response = requests.get('http://localhost:9000/channels')
channel_ids = response.json()

# Fetch stream info for each channel and print it
for channel_id in channel_ids:
    response = requests.get(f'http://localhost:9000/stream/{channel_id}')
    stream_info = response.json()
    print(json.dumps(stream_info, indent=4))

'''
$ python scripts/get-all-streams.py 
{
    "url": "https://pol5.dunyapurkaraja.com:999/hls/starhindi.m3u8?md5=O2pZdGz-mWFfbrfLxkqJ5w&expires=1745258725",
    "announce": "https://web-lab3.com/v1",
    "token": "_Yiurmd7g",
    "proxied_url": "http://localhost:8081/proxy/pol5.dunyapurkaraja.com:999/hls/starhindi.m3u8?md5=O2pZdGz-mWFfbrfLxkqJ5w&expires=1745258725"
}
{
    "url": "https://pol5.dunyapurkaraja.com:999/hls/skyscric.m3u8?md5=82F0oolJ2UA4aX49SvAGzw&expires=1745258727",
    "token": "_Yiurmd7g",
    "proxied_url": "http://localhost:8081/proxy/pol5.dunyapurkaraja.com:999/hls/skyscric.m3u8?md5=82F0oolJ2UA4aX49SvAGzw&expires=1745258727"
}
{
    "url": "https://pol5.dunyapurkaraja.com:999/hls/willowusa.m3u8?md5=FuEqfxYn_jg9oC5jm31UCA&expires=1745258729",
    "announce": "https://web-lab3.com/v1",
    "token": "_Yiurmd7g",
    "proxied_url": "http://localhost:8081/proxy/pol5.dunyapurkaraja.com:999/hls/willowusa.m3u8?md5=FuEqfxYn_jg9oC5jm31UCA&expires=1745258729"
}
{
    "url": "https://pol7.dunyapurkaraja.com:999/hls/star1in.m3u8?md5=qM37Lb9VI_ufXd_8bRLWkg&expires=1745258731",
    "announce": "https://web-lab3.com/v1",
    "token": "_Yiurmd7g",
    "proxied_url": "http://localhost:8081/proxy/pol7.dunyapurkaraja.com:999/hls/star1in.m3u8?md5=qM37Lb9VI_ufXd_8bRLWkg&expires=1745258731"
}
'''