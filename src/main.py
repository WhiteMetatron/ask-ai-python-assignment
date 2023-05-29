import os
import json
import utils
from enum import Enum
from collections import defaultdict
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel
from mocks.google_docs_client_mock import GoogleDocsClientMock
from mocks.sfkb_mock import SFKBToken, SFKBMock

# Initial load of keys from keys.json
with open(os.path.join(os.path.dirname(__file__), "..", "keys.json"), mode='r') as fi:
    keys_data: Dict[str, Dict[str, str]] = json.load(fi)


class Valid(Enum):
    NO_DATA = 0
    NO_KEY = 1
    NO_ACCESS = 2
    VALIDATED = 3


# In-memory storage
# customer_data: Dict[str, List[str]] = {}
source_validated_dict: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))


# The server object
app = FastAPI()

# Currently, approved sources
approved_sources = ["google_docs", "sfkb_user_name"]


def validate_source(customer, key_source):
    main_key = keys_data.get(customer, {}).get(key_source)

    # google_docs logic
    if key_source == "google_docs":
        gd_client = GoogleDocsClientMock(customer, main_key)
        try:
            _ = gd_client.get_docs_call()
        except ValueError:
            source_validated_dict[customer][key_source] = Valid.NO_ACCESS
            return {"source_validated": "NO_ACCESS"}

        # else (no exception)
        source_validated_dict[customer][key_source] = Valid.VALIDATED
        return {"source_validated": "VALIDATED"}

    # salesforce logic
    elif key_source == "sfkb_user_name":
        sfkb_password = keys_data.get(customer).get("sfkb_password")
        sfkb_client = SFKBMock()
        try:
            _ = sfkb_client.authenticate(customer, main_key, sfkb_password)
        except ValueError:
            source_validated_dict[customer][key_source] = Valid.NO_ACCESS
            return {"source_validated": "NO_ACCESS"}

        # else (no exception)
        source_validated_dict[customer][key_source] = Valid.VALIDATED
        return {"source_validated": "VALIDATED"}


@app.get("/")
async def root():
    return {"message": "Server is working.."}


# Save key request body model
class SaveKeyRequest(BaseModel):
    key_customer: str
    key_source: str
    key_value: str


# Save key endpoint
@app.post("/save_key")
async def save_key(request: SaveKeyRequest):
    # Logic to save the keys in memory and
    keys_data[request.key_customer] = keys_data.get(request.key_customer, {})
    keys_data[request.key_customer][request.key_source] = request.key_value

    # Very not optimized (and risky) way to store new\updates keys to the keys.json
    with open(os.path.join(os.path.dirname(__file__), "..", "keys.json"), mode='w') as fo:
        json.dump(keys_data, fo)

    # Return response
    return {}


# Is source validated request body model
class IsSourceValidatedRequest(BaseModel):
    key_customer: str
    key_source: str


# Is source validated endpoint
@app.get("/is_source_validated")
async def is_source_validated(request: IsSourceValidatedRequest):
    # Not approved source
    # if request.key_source not in approved_sources:
    #     return {"error": f"{request.key_source} not in approved sources: {approved_sources}"}

    customer = request.key_customer
    key_source = request.key_source

    status = source_validated_dict[customer][key_source]

    return {"source_validated": status}


# Index customer request body model
class IndexCustomerRequest(BaseModel):
    customer: str


# Index customer endpoint
@app.post("/index_customer")
async def index_customer(request: IndexCustomerRequest):
    customer = request.customer

    if customer not in keys_data.keys():
        return {"message": f"Customer '{customer}' not found"}

    validate_sources = source_validated_dict[customer]
    customer_data: List[Dict] = []

    for source, validated_status in validate_sources.items():
        if validated_status == Valid.VALIDATED:
            # Index validated source
            # Assuming no error handling is needed here (but sure in life we do need some..)

            if source == "google_docs":
                credential = keys_data[customer][source]
                gd_client = GoogleDocsClientMock(customer, credential)
                gd_customer_data = gd_client.get_docs_call()
                customer_data.extend(gd_customer_data)

            elif source == "sfkb_user_name":
                sfkb_user_name = keys_data.get(customer).get("sfkb_user_name")
                sfkb_password = keys_data.get(customer).get("sfkb_password")
                sfkb_client = SFKBMock()
                token = sfkb_client.authenticate(customer, sfkb_user_name, sfkb_password)
                docs_ids = sfkb_client.get_doc_ids(token.token)
                for doc_id in docs_ids:
                    sf_customer_data = sfkb_client.get_doc(token.token, doc_id)
                    customer_data.append(sf_customer_data)

        else:
            # Source not validated
            pass

        # Save to the cloud logic
        for data in customer_data:
            utils.save_file_to_cloud_mock(data["URL"], data["HTML"])

        num_docs = len(customer_data)
        return {"num_docs": num_docs}


# Run when server starts
for customer, customer_data in keys_data.items():
    for key_name, key_info in customer_data.items():
        if key_name in approved_sources:
            validate_source(customer, key_name)

