import requests
import json

export_button_url = f"https://ibdstockscreener.investors.com/research-tool/api/ibdlist/export/_IBDDataTables"

login_url = "https://login.investors.com/accounts.login"

login_api_key = "3_H1yN9UVDBc6ix9wBEAvcnQORVTJ5gA5vgWv_FrEQ9Xijk0CNrVuU6YRjWz2zHZAe"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76"

email = "Ubikdigital1@gmail.com"

password = "Minimu90"

login_payload = {
    "loginID": email,
    "password": password,
    "APIKey": login_api_key
}

headers = {
    "user-agent": user_agent
}

cookies = {}

session = requests.Session()

login_response = session.post(login_url, data=login_payload, headers=headers)
login_response_content = json.loads(login_response.content)

session.auth = (login_response_content.get("sessionInfo", {}).get("cookieName"), login_response_content.get("sessionInfo", {}).get("cookieName"))
session.cookies.set(login_response_content.get("sessionInfo", {}).get("cookieName"), login_response_content.get("sessionInfo", {}).get("cookieName"))

export_response = session.get(export_button_url, headers=headers)
print(export_response.content)

with open("data_ibd.xlsx", "wb") as f:
    f.write(export_response.content)
    f.close()