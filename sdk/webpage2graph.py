"""
將網頁資訊轉成Graph來進行視覺化

節點：
1. EndPoint - labels: domain, method (post/get/...)
    - properties:
        - request header
        - request payload
        - response header
2. Response Schema - labels: content-type (json/html...), 
    - Response schema (JSON schema)
3. Request Schema - (request section: header/payload)
    - Request schema (JSON schema)

4. Response instance 
    - header instance 
    - body 
5. Request instance
    - header instance 
    - payload

連線：

1. EndPoint -> Response Schema
2. EndPoint <- Request Schema
3. Response Schema <- belong to - Response instance
4. Request Schema <- belong to - Request instance
5. Request instance - has_response -> Response instance

進一步拆解：
1. JSON Request schema 展開
2. JSON Response schema 展開
3. JSON Request 內容展開
4. JSON Response 內容展開
5. HTML Response 提取出 結構化區域
(https://www.researchgate.net/publication/332666543_Web_Page_Structured_Content_Detection_Using_Supervised_Machine_Learning)
"""