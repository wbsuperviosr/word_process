# %%
from functools import lru_cache
import os
import json
import requests
from zipfile import ZipFile
from datetime import datetime, date
from dateutil import tz
from requests import Response
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient
from boto3 import client as AWSClient

from word2json.models.base import BaseDocument
from word2json.utils import json_serial
from word2json.logger import logger


class SanityClient(object):
    def __init__(self, credential: "Sanity", dev: bool = False) -> None:
        self.credential = credential
        self.dev = dev

    @property
    def endpoint(self) -> str:
        return f"https://{self.project_id}.api.sanity.io/{self.credential.api_version}"

    @property
    def headers(self) -> dict[str, str]:
        return {"authorization": f"Bearer {self.token}"}

    def mutate_api(self, dataset: str = None) -> str:
        dataset = dataset if dataset is not None else self.credential.dataset
        return f"{self.endpoint}/data/mutate/{dataset}"

    def query_api(self, dataset: str = None) -> str:
        dataset = dataset if dataset is not None else self.credential.dataset
        return f"{self.endpoint}/data/query/{dataset}"

    def insert(self, documents: dict | list[dict], dataset: str = None) -> Response:
        documents = [documents] if isinstance(documents, dict) else documents
        payload = {"mutations": [{"createOrReplace": doc} for doc in documents]}
        logger.info(
            f"inserting document to {dataset if dataset is not None else self.credential.dataset}"
        )
        res = requests.post(
            self.mutate_api(dataset),
            headers=self.headers,
            data=json.dumps(payload, default=json_serial),
        )
        logger.info(res.json())
        return res

    def get(self, query: str, dataset: str = None) -> dict:
        response = requests.get(f"{self.query_api(dataset)}?query={query}").json()
        if "result" in response.keys():
            return response["result"]
        else:
            raise RuntimeError(response)

    def get_document(
        self, type: str, title: str, dataset: str = None
    ) -> Optional[BaseDocument]:
        query = f"*[_type=='{type}' %26%26 title=='{title}']"
        results = self.get(query, dataset=dataset)
        if len(results) == 0:
            return None
        return results[0]

    def get_documents(self, type: str, dataset: str = None) -> list[BaseDocument]:
        query = f"*[_type=='{type}']"
        return self.get(query, dataset=dataset)

    def delete(
        self,
        ids: Optional[list[str] | str] = None,
        delete_query: Optional[dict] = None,
        purge: Optional[bool] = None,
        dataset: str = None,
    ) -> Response:
        if ids is not None and delete_query is not None:
            raise ValueError("ids and delete_query can't both be provided")
        elif ids is None and delete_query is None:
            raise ValueError("ids and delete_query can't both be None")
        else:
            if ids is not None:
                ids = [ids] if isinstance(ids, str) else ids
                if purge is None:
                    payload = {"mutations": [{"delete": {"id": i}} for i in ids]}
                else:
                    payload = {
                        "mutations": [
                            {"delete": {"id": i, "purge": purge}} for i in ids
                        ]
                    }
            else:
                if purge is None:
                    payload = {"mutations": [{"delete": {"query": delete_query}}]}
                else:
                    payload = {
                        "mutations": [
                            {"delete": {"query": delete_query, "purge": purge}}
                        ]
                    }
            print(payload)
            return requests.post(
                self.mutate_api(dataset),
                headers=self.headers,
                data=json.dumps(payload, default=json_serial),
            )

    @property
    def project_id(self) -> str:
        if self.dev:
            return self.credential.dev_project_id
        return self.credential.project_id

    @property
    def token(self) -> str:
        if self.dev:
            return self.credential.dev_token
        return self.credential.token


class LocalClient(object):
    def __init__(self, local: "LocalFile") -> None:
        self.local = local

    @lru_cache(maxsize=None)
    def read(self, type: str, title: str, target: str):
        filepath = os.path.join(self.local.words_dir, type, f"{title}.docx")
        with ZipFile(filepath) as zf:
            return zf.read(target)

    def get_fileinfo(self, type: str, title: str):
        filepath = os.path.join(self.local.words_dir, type, f"{title}.docx")
        stats = os.stat(filepath)
        info = {
            "mtime": datetime.fromtimestamp(stats.st_mtime, tz=tz.UTC),
            "ctime": datetime.fromtimestamp(stats.st_ctime, tz=tz.UTC),
            "size": stats.st_size,
        }
        return info

    def get_imageinfo(self, filepath: str):
        with ZipFile(filepath) as f:
            images = []
            for d in f.filelist:
                fname = d.filename
                if fname.startswith("word/media/") and (not fname.endswith("/")):
                    images.append(
                        {
                            "filename": fname,
                            "ctime": datetime(*d.date_time).strftime(
                                "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            "size": d.file_size,
                        }
                    )
            return images


class Sanity(BaseModel):
    dataset: str
    api_version: str
    token: str
    project_id: str
    dev_token: Optional[str]
    dev_project_id: Optional[str]
    dev: bool

    def get_client(self, dev: bool = None) -> SanityClient:
        dev = self.dev if dev is None else dev
        return SanityClient(self, dev=dev)


class CloudFlare(BaseModel):
    account_id: str
    key_id: str
    secret: str

    def get_client(self) -> AWSClient:
        return AWSClient(
            service_name="s3",
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret,
            endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
        )


class MongoDBAtlas(BaseModel):
    username: str
    password: str
    endpoint: str

    @property
    def connection_uri(self):
        return f"mongodb+srv://{self.username}:{self.password}@{self.endpoint}"

    def get_client(self) -> MongoClient:
        return MongoClient(self.connection_uri)


class LocalFile(BaseModel):
    words_dir: str
    image_dir: str

    def get_client(self) -> LocalClient:
        return LocalClient(self)


class Services(BaseModel):
    sanity: Optional[Sanity]
    cloudflare: Optional[CloudFlare]
    mongodb: Optional[MongoDBAtlas]
    local: Optional[LocalFile]


if __name__ == "__main__":

    service = Services.parse_file("credential.json")
    sanity = service.sanity.get_client(dev=True)

    # res = sanity.get_document("casefile", "公审第1回检方陈述", "develop")
    cloud: AWSClient = service.cloudflare.get_client()
    # res = sanity_dev.delete(ids=todel)
    # print(res.content)

    # client = service.local.get_client()
