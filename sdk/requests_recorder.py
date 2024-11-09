"""
應該要有一個關聯排序功能：

把endpoint與網頁輸入的網址做比對
從最相關排到最不相關
"""

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.utils import decode


driver = webdriver.Chrome(
    service=Service(executable_path=ChromeDriverManager().install()),
)
result = driver.get("https://findbiz.nat.gov.tw/fts/query/QueryCmpyDetail/queryCmpyDetail.do")
for i, request in enumerate(driver.requests):
    if request.response:
        if request.response.headers['Content-Type'] not in [
                'image/gif', 'text/javascript'
            ] and 'google' not in request.url and 'facebook' not in request.url:
            print(f'REQUEST No.{i}', request.response.status_code, request.method, request.response.headers['Content-Type'])
            print(request.url)
            body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            print('Body Size:', len(body))
            print('=================================================')
driver.close()