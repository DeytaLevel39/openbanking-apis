from typing import Optional,List
from fastapi import FastAPI
import requests, json
from pydantic import BaseModel
from genson import SchemaBuilder
import pymongo



app = FastAPI()

def mongo_cnt(password, myFirstDatabase):
    mongo_cntstr = "mongodb+srv://admin:"+password+"@cluster0.jbbpl.mongodb.net/"+myFirstDatabase+"?retryWrites=true&w=majority"
    print(mongo_cntstr)
    client = pymongo.MongoClient(mongo_cntstr)
    db = client.test
    return db


def fetch_ob_urls():

    opendata_github_url="https://raw.githubusercontent.com/OpenBankingUK/opendata-api-spec-compiled/master/participant_store.json"

    resp = requests.get(opendata_github_url)

    urls = []

    if resp.status_code == 200:
        resp_json = resp.json()
        for d in resp_json['data']:
            base_url = d['baseUrl']
            for api in d['supportedAPIs']:
                if 'business-current-accounts' in d['supportedAPIs']:
                    api_version=d['supportedAPIs']['business-current-accounts']
                    append_str = [base_url+"/"+api_version[0]+"/"+api,api]
                    urls.append(append_str)
    else:
        print("Failed to receive participant list")

    return (urls)

def fetch_service(svc, col):
    json_objs = []
    col = db["atms"]
    col.delete_many({})
    for url in fetch_ob_urls():
        if url[1]==svc:
            print("Fetching ",url[1],"from",url[0])
            resp = requests.get(url[0])
            if resp.status_code == 200:
                json_objs.append(resp.json())
                x = col.insert_one(resp.json())
            else:
                print("Failed to get a proper response from", url[0])
    return json_objs

db = mongo_cnt("openbanking", "atms")
atm_json = fetch_service("atms", db)

example_json={
   "model":{"name":"string"},
  "example": {
      "meta": {
        "LastUpdated": "2021-03-29T09:01:00.441Z",
        "TotalResults": 0,
        "Agreement": "Use of the APIs and any related data will be subject to the terms of the Open Licence and subject to terms and conditions",
        "License": "https://www.openbanking.org.uk/open-licence",
        "TermsOfUse": "https://www.openbanking.org.uk/terms"
      },
      "data": [
        {
          "Brand": [
            {
              "BrandName": "string",
              "ATM": [
                {
                  "Identification": "string",
                  "SupportedLanguages": [
                    "string"
                  ],
                  "ATMServices": [
                    "Balance"
                  ],
                  "Accessibility": [
                    "AudioCashMachine"
                  ],
                  "Access24HoursIndicator": True,
                  "SupportedCurrencies": [
                    "string"
                  ],
                  "MinimumPossibleAmount": "string",
                  "Note": [
                    "string"
                  ],
                  "OtherAccessibility": [
                    {
                      "Code": "string",
                      "Name": "string",
                      "Description": "string"
                    }
                  ],
                  "OtherATMServices": [
                    {
                      "Code": "string",
                      "Name": "string",
                      "Description": "string"
                    }
                  ],
                  "Branch": {
                    "Identification": "string"
                  },
                  "Location": {
                    "LocationCategory": [
                      "BranchExternal"
                    ],
                    "OtherLocationCategory": [
                      {
                        "Code": "string",
                        "Name": "string",
                        "Description": "string"
                      }
                    ],
                    "Site": {
                      "Identification": "string",
                      "Name": "string"
                    },
                    "PostalAddress": {
                      "AddressLine": [
                        "string"
                      ],
                      "BuildingNumber": "string",
                      "StreetName": "string",
                      "TownName": "string",
                      "CountrySubDivision": [
                        "string"
                      ],
                      "Country": "string",
                      "PostCode": "string",
                      "GeoLocation": {
                        "GeographicCoordinates": {
                          "Latitude": "string",
                          "Longitude": "string"
                        }
                      }
                    }
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  }

# Data model
class Item(BaseModel):
    class Config:
        schema_extra = example_json


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/atms", response_model=List[Item])
def atms():
    return atm_json
