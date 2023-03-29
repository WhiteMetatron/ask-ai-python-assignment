# google docs mock

from typing import List, Dict
import json

f = open('../../keys.json')
KEYS = json.load(f)


class GoogleDocsClientMock:
    def __init__(self, customer: str, secret: str):
        self.customer = customer
        self.secret = secret

    def get_docs_call(self) -> List[Dict]:

        if KEYS.get(self.customer).get("google_docs") != self.secret:
            raise ValueError("Wrong token given.")

        return [{
            "URL": f"{self.customer}_URL1.1",
            "HTML": "HTML1.1"
        }, {
            "URL": f"{self.customer}_URL1.2",
            "HTML": "HTML1.2"
        }]
