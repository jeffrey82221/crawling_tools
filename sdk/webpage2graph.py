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
4. Response instance （需點兩次才能有 schema/instance 之間的差別）
    - header instance 
    - body 
5. Request instance （需點兩次才能有 schema/instance 之間的差別）
    - header instance 
    - payload

連線：

1. EndPoint -> Response Schema
2. EndPoint <- Request Schema
3. Response Schema <- belong to - Response instance
4. Request Schema <- belong to - Request instance
5. Request Instance - has_response -> Response instance

進一步拆解：
1. JSON Request Schema 展開 -> JSONEntries 節點
2. JSON Response Schema 展開 -> JSONEntries 節點
3. JSON Request 內容展開 -> JSONEntity 節點
4. JSON Response 內容展開 -> JSONEntity 節點
5. HTML Response 提取出 結構化區域
(https://www.researchgate.net/publication/332666543_Web_Page_Structured_Content_Detection_Using_Supervised_Machine_Learning)
6. Endpoint URL 展開 -> EndPointEntries

進一步關聯：
1. 關鍵的 schema keys 可以連起來 (Schema <-> key <-> Schema) 類似 foreign key
(此為推論類型的連線，應該要能夠有足夠的彈性去調整）

2. Instance 可以跟 schema 節點相連
"""
