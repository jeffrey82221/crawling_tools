# 幫我檢查以下兩個string的差異

## 第一個string：

```
POST /mops/web/ajax_t51sb01 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6
Connection: keep-alive
Content-Length: 53
Content-Type: application/x-www-form-urlencoded
Cookie: jcsession=jHttpSession@369b4ff0; _ga=GA1.1.397712912.1730944133; _ga_LTMT28749H=GS1.1.1730944132.1.1.1730944197.0.0.0
Host: mops.twse.com.tw
Origin: https://mops.twse.com.tw
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
sec-ch-ua: "Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
```

## 第二個string：

```
POST /mops/web/ajax_t51sb01 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6
Connection: keep-alive
Content-Length: 53
Content-Type: application/x-www-form-urlencoded
Cookie: jcsession=jHttpSession@369b4ff0; _ga=GA1.1.397712912.1730944133; _ga_LTMT28749H=GS1.1.1730944132.1.1.1730944197.0.0.0
Host: mops.twse.com.tw
Origin: https://mops.twse.com.tw
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
sec-ch-ua: "Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
```

**ANS:**：

# 幫我根據以下需求進行資料轉換：

## 抓出這個 HTML POST Rawdata中的Headers資訊並轉成一個可以放入python
 `requests.requests(method='GET', ..., headers=headers)` 的python dictionary

## 此為輸入的 Rawdata: 

```
POST /server-java/t105sb02 HTTP/1.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6
Cache-Control: max-age=0
Connection: keep-alive
Content-Length: 60
Content-Type: application/x-www-form-urlencoded
Cookie: _ga=GA1.1.397712912.1730944133; _ga_LTMT28749H=GS1.1.1730946656.2.1.1730946656.0.0.0
Host: mops.twse.com.tw
Origin: null
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
sec-ch-ua: "Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
```

**ANS:**



# 幫我根據以下需求進行資料轉換：

## 抓出這個 HTML POST payload 資訊並轉成一個可以放入python
 `requests.requests(method='GET', ..., data=data)` 的python dictionary


## 以下為 payload字串：

```
order=priceDate&sort=desc&page=2&institutional=0&isShowTag=1&fields=categoryAbbr,change,changePercent,classCurrencyLocal,cnyesId,displayNameLocal,displayNameLocalWithKwd,forSale,forSale,inceptionDate,investmentArea,lastUpdate,nav,prevPrice,priceDate,return1Month,saleStatus

```

**ANS:**