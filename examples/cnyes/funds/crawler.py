"""
基金爬蟲
"""
import time
import requests
from typing import Dict, Iterator


WAIT_TIME = 0.0

class MainCrawler:
    """
    基金列表資訊抓取
    """
    @staticmethod
    def get_response(page: int) -> Dict:
        """
        取得基金列表分頁
        """
        url = 'https://fund.api.cnyes.com/fund/api/v2/search/fund'
        data = {
            'order': 'priceDate',
            'sort': 'desc',
            'page': str(page),
            'institutional': '0',
            'isShowTag': '1',
            'fields': 'categoryAbbr,classCurrencyLocal,cnyesId,displayNameLocal,inceptionDate,investmentArea,lastUpdate,saleStatus'
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'origin': 'https://fund.cnyes.com',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers,
            params=data
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()

    def generate_rows(self) -> Iterator[Dict]:
        """
        逐步抓取不同頁面的基金列表
        以 Iterator 方式逐行回傳
        """
        page_id = 1
        extract_keys = [
            'cnyesId',
            'displayNameLocal',
            'categoryAbbr',
            'investmentArea',
            'inceptionDate',
            'lastUpdate',
            'classCurrencyLocal',
            'saleStatus',
            'fundTags'
        ]
        while True:
            time.sleep(WAIT_TIME)
            data = self.get_response(page_id)['items']['data']
            if len(data):
                for fund in data:
                    yield dict([(key, fund[key]) for key in fund if key in extract_keys])
            else:
                break
            page_id += 1


class NavCrawler:
    """
    基金淨值資訊抓取
    """
    @staticmethod
    def get_response(cnyes_id: str, page: int) -> Dict:
        """
        取得特定基金的特定範圍的歷史淨值
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/nav'
        data = {
            'format': 'table',
            'page': str(page)
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'origin': 'https://fund.cnyes.com',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers,
            params=data
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()

    def generate_rows(self, cnyes_id: str) -> Iterator[Dict]:
        """
        Iterator 方式逐行回傳每分頁的基金淨值
        """
        page_id = 1
        extract_keys = [
            'tradeDate',
            'nav',
            'change',
            'changePercent'
        ]
        while True:
            time.sleep(WAIT_TIME)
            data = self.get_response(cnyes_id, page_id)['items']['data']
            if len(data):
                for nav in data:
                    yield dict([(key, nav[key]) for key in nav if key in extract_keys])
            else:
                break
            page_id += 1

class DividentCrawler:
    """
    基金配息資訊抓取
    """
    @staticmethod
    def get_response(cnyes_id: str, page: int) -> Dict:
        """
        取得基金配息資訊頁面
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/dividend'
        data = {
            'page': str(page)
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'origin': 'https://fund.cnyes.com',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers,
            params=data
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()

    def generate_rows(self, cnyes_id: str) -> Iterator[Dict]:
        """
        逐步抓取不同頁面的基金配息資訊
        以 Iterator 方式逐行回傳
        """
        page_id = 1
        extract_keys = [
            'excludingDate',
            'totalDistribution',
            'recordDate',
            'distributionYield',
            'fundClassId',
            'distributeTotalRatio',
            'distributeCapitalRatio',
            'nav',
            'sitcaYield'
        ]
        while True:
            time.sleep(WAIT_TIME)
            data = self.get_response(cnyes_id, page_id)['items']['data']
            if len(data):
                for nav in data:
                    yield dict([(key, nav[key]) for key in nav if key in extract_keys])
            else:
                break
            page_id += 1
    
class AssetsCrawler:
    """
    取得某基金的持有資產比例
    """
    @staticmethod
    def get_response(cnyes_id: str) -> Dict:
        """
        取得基金持有資產比例
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/assets'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()
    
class RegionCrawler:
    """
    取得投資地區資訊
    """
    @staticmethod
    def get_response(cnyes_id: str) -> Dict:
        """
        取得基金投資地區比例
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/regions'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()
    
class HoldingsCrawler:
    """
    取得基金的持股
    """
    @staticmethod
    def get_response(cnyes_id: str) -> Dict:
        """
        取得基金投資地區比例
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/holdings'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()

class IndustryCrawler:
    """
    取得基金產業投資比例
    """
    @staticmethod
    def get_response(cnyes_id: str) -> Dict:
        """
        取得基金投資地區比例
        """
        url = f'https://fund.api.cnyes.com/fund/api/v1/funds/{cnyes_id}/industries'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://fund.cnyes.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'x-platform': 'WEB',
            'x-system-kind': 'FUND-DESKTOP'
        }
        res = requests.request(
            method = 'GET',
            url = url,
            headers=headers
        )
        assert res.status_code == 200, f'status code should be 200 rather than {res.status_code}'
        return res.json()

    
if __name__ == '__main__':
    time.sleep(WAIT_TIME)
    result = IndustryCrawler().get_response('B610022')
    print(result)
    for fund in MainCrawler().generate_rows():
        print(fund)
        id = fund['cnyesId']
        for i, row in enumerate(NavCrawler().generate_rows(id)):
            print('nav', i)

        for i, row in enumerate(DividentCrawler().generate_rows(id)):
            print('divident', i)
    