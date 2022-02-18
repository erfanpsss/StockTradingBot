import requests
import json
import uuid
account_id = "DU4677076"

symbol = "TSLA"

conid = 265598

reply_id = "0b3dbf46-59f8-4a7b-a833-fb87fe8d0f9b"

base_url = "http://localhost:5000/v1/api/"

sso_validate_url = "sso/validate"

get_account_info_url = "portfolio/accounts"

get_balance_summary = f"portfolio/{account_id}/summary"

auth_status_url = "iserver/auth/status"

reauthenticate_url = "iserver/reauthenticate"

get_symbol_id_url = "iserver/secdef/search"

place_order_url = f"iserver/account/{account_id}/orders"

place_order_reply_url = f"iserver/reply/{reply_id}"

orders_url = f"iserver/account/orders"

trades_url = "iserver/account/trades"

get_symbol_id_payload = {
  "symbol": symbol,
  "name": True,
  "secType": "STK"
}

get_balance_payload = {
    "acctIds": [
        account_id
    ]
}

place_order_reply_payload = {
    "confirmed": True
}

place_order_payload = {
    "orders": [
        {
            "acctId": account_id,
            "conid": conid,
            "conidex": None,
            "secType": "STK",
            "cOID": str(uuid.uuid4()),
            "parentId": None,
            "orderType": "MKT",
            "listingExchange": "SMART",
            "isSingleGroup": True,
            "outsideRTH": False,
            "price": None,
            "auxPrice": None,
            "side": "BUY",
            "ticker": symbol,
            "tif": "GTC",
            "referrer": "test",
            "quantity": 1,
            "cashQty": None,
            "fxQty": None,
            "useAdaptive": False,
            "isCcyConv": False,
            "allocationMethod": "AvailableEquity",
            "strategy": None,
            "strategyParameters": {},
        },
    ],
}


#res1= requests.post(base_url+reauthenticate_url)
#print(111, res1.content,  "\n")

res2= requests.post(base_url+auth_status_url)
print(222, res2.content,  "\n")

res3=requests.get(base_url+sso_validate_url)
print(333, res3.content,  "\n")

res4=requests.get(base_url+get_account_info_url)
print(444, res4.content,  "\n")

#res5= requests.post(base_url+get_symbol_id_url, data=json.dumps(get_symbol_id_payload), headers={"Content-Type": "application/json"})
#print(555, res5.content,  "\n")
#print(555, json.loads(res5.content)[0]["conid"],  "\n")

#place_order_payload["orders"][0]["conid"] = json.loads(res5.content)[0]["conid"]
#res6= requests.post(base_url+place_order_url, data=json.dumps(place_order_payload), headers={"Content-Type": "application/json"})
#print(666, res6.content,  "\n")


#res7=requests.get(base_url+get_balance_summary)
#print(777, json.loads(res7.content),  "\n")
#with open("t.json", "w") as f:
#    f.write(res7.content.decode())

#print(json.loads(res7.content).get("availablefunds", {}).get("amount", ""))


res9= requests.get(base_url+orders_url)
print(999, res9.content,  "\n")


#res10= requests.post(base_url+place_order_reply_url, data=json.dumps(place_order_reply_payload), headers={"Content-Type": "application/json"})
#print(1010, res10.content,  "\n")


res11= requests.get(base_url+trades_url)
print(1111, res11.content,  "\n")


