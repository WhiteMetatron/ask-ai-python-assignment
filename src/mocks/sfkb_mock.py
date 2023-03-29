from typing import Set, Dict
import json

f = open('../..keys.json')
KEYS = json.load(f)
FAKE_SFKB_TOKEN = "z"


class SFKBMock:
    def __init__(self):
        self.token = FAKE_SFKB_TOKEN

    def authenticate(self, customer: str, username: str, password: str) -> str:
        customer_keys = KEYS.get(customer)
        if customer_keys.get(
                "sfkb_user_name") == username and customer_keys.get(
                    "sfkb_password") == password:
            return self.token

    def _verify_token(self, token: str):
        if token != self.token:
            raise ValueError("Wrong token given.")

    def get_doc_ids(self, token: str) -> Set[str]:
        self._verify_token(token)
        return {"DOC_ID_1", "DOC_ID_2", "DOC_ID_3"}

    def get_doc(self, token: str, doc_id: str) -> Dict:
        self._verify_token(token)
        if doc_id == "DOC_ID_1":
            return {
                "URL": f"{self.customer}_URL2.1",
                "HTML": "HTML2.1",
                "LAST_UPDATED_BY": "USER1",
                "LAST_UPDATED_DATE": "DATE1"
            }
        if doc_id == "DOC_ID_2":
            return {
                "URL": f"{self.customer}_URL2.2",
                "HTML": "HTML2.2",
                "LAST_UPDATED_BY": "USER1",
                "LAST_UPDATED_DATE": "DATE2"
            }
        if doc_id == "DOC_ID_3":
            return {
                "URL": f"{self.customer}_URL2.3",
                "HTML": "HTML2.3",
                "LAST_UPDATED_BY": "USER2",
                "LAST_UPDATED_DATE": "DATE3"
            }
