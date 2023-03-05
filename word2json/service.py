# %%
import os
import json
import requests
from zipfile import ZipFile
from datetime import datetime
from requests import Response
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient
from boto3 import client as AWSClient
from functools import cached_property


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

    @property
    def mutate_api(self) -> str:
        return f"{self.endpoint}/data/mutate/{self.credential.dataset}"

    @property
    def query_api(self) -> str:
        return f"{self.endpoint}/data/query/{self.credential.dataset}"

    def insert(self, documents: dict | list[dict]) -> Response:
        documents = [documents] if isinstance(documents, dict) else documents
        payload = {"mutations": [{"createOrReplace": doc} for doc in documents]}
        return requests.post(
            self.mutate_api, headers=self.headers, data=json.dumps(payload)
        )

    def get(self, query: str) -> dict:
        response = requests.get(f"{self.query_api}?query={query}").json()
        if "result" in response.keys():
            return response["result"]
        else:
            raise RuntimeError(response)

    def delete(
        self,
        ids: Optional[list[str] | str] = None,
        delete_query: Optional[dict] = None,
        purge: Optional[bool] = None,
    ) -> Response:
        if ids is not None and delete_query is not None:
            raise ValueError("ids and delete_query can't both be provided")
        elif ids is None and delete_query is None:
            raise ValueError("ids and delete_query can't both be None")
        else:
            if ids is not None:
                ids = [ids] if isinstance(ids, str) else ids
                if purge is None:
                    payload = {"mutations": [{"delete": i} for i in ids]}
                else:
                    payload = {
                        "mutations": [{"delete": i, "purge": purge} for i in ids]
                    }
            else:
                if purge is None:
                    payload = {"mutations": [{"delete": delete_query}]}
                else:
                    payload = {"mutations": [{"delete": delete_query, "purge": purge}]}

            return requests.post(
                self.mutate_api, headers=self.headers, data=json.dumps(payload)
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

    def get_fileinfo(self, type: str, filename: str):
        stats = os.stat(self.path(type, filename))
        info = {
            "mtime": stats.st_mtime,
            "ctime": stats.st_ctime,
            "size": stats.st_size,
            "type": type,
            "filename": filename,
        }
        return info

    def list_files(self, type: str) -> list[str]:
        return os.listdir(os.path.join(self.local.root, type))

    def list_fileinfos(self, type: str) -> list[dict]:
        return [self.get_fileinfo(type, f) for f in self.list_files(type)]

    def get_imageinfo(self, type: str, filename: str):
        with ZipFile(self.path(type, filename)) as f:
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

    def path(self, type: str, filename: str) -> str:
        return os.path.join(self.local.root, type, filename)


class Sanity(BaseModel):
    dataset: str
    api_version: str
    token: str
    project_id: str
    dev_token: Optional[str]
    dev_project_id: Optional[str]

    def get_client(self, dev: bool = False) -> SanityClient:
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
    root: str

    def get_client(self) -> LocalClient:
        return LocalClient(self)


class Services(BaseModel):
    sanity: Optional[Sanity]
    cloudflare: Optional[CloudFlare]
    mongodb: Optional[MongoDBAtlas]
    local: Optional[LocalFile]


service = Services.parse_file("credential.json")
sanity = service.sanity.get_client(dev=True)
client = service.local.get_client()
