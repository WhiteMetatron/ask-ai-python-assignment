# google docs mock

import json
import os
from typing import List, Dict

with open(os.path.join(os.path.dirname(__file__), "..", "..", "keys.json")) as f:
    KEYS = json.load(f)

__all__ = ["GoogleDocsClientMock"]


class GoogleDocsClientMock:
    def __init__(self, customer: str, secret: str):
        self.customer = customer
        self.secret = secret

    def get_docs_call(self) -> List[Dict]:
        """
        Get customer documents
        :return:
        """
        if self.customer in KEYS and self.secret is not None and KEYS[self.customer].get("google_docs") != self.secret:
            raise ValueError("Wrong token given.")

        return [{
            "URL": f"{self.customer}_URL1.1",
            "HTML": "HTML1.1"
        }, {
            "URL": f"{self.customer}_URL1.2",
            "HTML": "HTML1.2"
        }]
