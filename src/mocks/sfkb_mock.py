import datetime
import json
import os
from typing import Set, Dict

import jwt

__all__ = ["SFKBToken", "SFKBMock"]

with open(os.path.join(os.path.dirname(__file__), "..", "..", "keys.json")) as f:
    KEYS = json.load(f)
FAKE_JWT_SECRET = "secret"


class SFKBToken:
    token: str
    expires_at: datetime

    def __init__(self, token: str, expires_at: datetime):
        self.token = token
        self.expires_at = expires_at


class SFKBMock:
    def authenticate(self, customer: str, username: str, password: str) -> SFKBToken:
        """
        Authenticate and return token for the provided customer, username and password

        :param customer: the customer to login as
        :param username: the customer's username
        :param password: the customer's password
        :return: customer's JWT token and expires_at
        """
        customer_keys = KEYS.get(customer)

        if customer_keys is not None and \
                customer_keys.get("sfkb_user_name") == username and \
                customer_keys.get("sfkb_password") == password:
            exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            token_content = {"sub": customer, "exp": exp}
            encoded_jwt = jwt.encode(token_content, FAKE_JWT_SECRET, algorithm="HS256")
            return SFKBToken(encoded_jwt, exp)
        raise ValueError("Wrong username or password")

    def _verify_token(self, token: str):
        try:
            decoded_jwt = jwt.decode(token, FAKE_JWT_SECRET, algorithms=["HS256"])
            return decoded_jwt["sub"]
        except:
            raise ValueError("Wrong token given.")

    def get_doc_ids(self, token: str) -> Set[str]:
        """
        Get the customer document IDs
        :param token: the API token
        :return: document IDs
        """
        self._verify_token(token)
        return {"DOC_ID_1", "DOC_ID_2", "DOC_ID_3"}

    def get_doc(self, token: str, doc_id: str) -> Dict:
        """
        Retrieve document data and metadata based on the provided document ID and token
        :param token: the API token
        :param doc_id: the document ID to get
        :return: document data
        """
        customer = self._verify_token(token)
        if doc_id == "DOC_ID_1":
            return {
                "URL": f"{customer}_URL2.1",
                "HTML": "HTML2.1",
                "LAST_UPDATED_BY": "USER1",
                "LAST_UPDATED_DATE": "DATE1"
            }
        if doc_id == "DOC_ID_2":
            return {
                "URL": f"{customer}_URL2.2",
                "HTML": "HTML2.2",
                "LAST_UPDATED_BY": "USER1",
                "LAST_UPDATED_DATE": "DATE2"
            }
        if doc_id == "DOC_ID_3":
            return {
                "URL": f"{customer}_URL2.3",
                "HTML": "HTML2.3",
                "LAST_UPDATED_BY": "USER2",
                "LAST_UPDATED_DATE": "DATE3"
            }
