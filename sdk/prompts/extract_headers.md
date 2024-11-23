# 幫我根據以下需求進行資料轉換：

## 抓出這個 HTML POST Rawdata中的Headers資訊並轉成一個可以放入python
 `requests.requests(method='POST', ..., headers=headers)` 的python dictionary

## 此為輸入的 Rawdata: 

```
:authority:
data.gov.tw
:method:
POST
:path:
/api/front/dataset/download-times/add
:scheme:
https
accept:
application/json
accept-encoding:
gzip, deflate, br, zstd
accept-language:
zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6
content-length:
15
content-type:
application/json
cookie:
_ga=GA1.1.1124121952.1729915187; __cf_bm=AlLCV8dlWENjpMy.CNuVLYmIyWuV5.bSvJ3WWdfqVus-1732092356-1.0.1.1-FJ0mugRBkRePQPWr_puTGn4dUyZvX0C_SOV.53QSFbhSthFg3E7oCAC1Rzo04YrAOMmqm3s8vfeXaY2IznHNDQ; PHPSESSID=jvmrlo0middsstc2v6fe7eocg6; _ga_68L77FMJ2H=GS1.1.1732092357.2.1.1732092412.5.0.0
origin:
https://data.gov.tw
priority:
u=1, i
referer:
https://data.gov.tw/dataset/79641
sec-ch-ua:
"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile:
?1
sec-ch-ua-platform:
"Android"
sec-fetch-dest:
empty
sec-fetch-mode:
cors
sec-fetch-site:
same-origin
user-agent:
Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36
```

**ANS:**


