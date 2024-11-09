from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.utils import decode



driver = webdriver.Chrome(
    service=Service(executable_path=ChromeDriverManager().install()),
)
result = driver.get("https://www.cnyes.com/")
for i, request in enumerate(driver.requests):
    if request.response:
        print(f'REQUEST No.{i}', request.response.status_code, request.method, request.response.headers['Content-Type'])
        print(request.url)
        body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        print('Body Size:', len(body))
        print('=================================================')
driver.close()