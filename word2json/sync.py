# %%
import os
import sys
import json
import subprocess
from enum import Enum, auto
from functools import cached_property, lru_cache
from typing import Type, Tuple

sys.path.append(os.getcwd())
from word2json.parser import (
    CasefileParser,
    RumorParser,
    AboutParser,
    ArticleParser,
    TimelineParser,
    MediaParser,
)


from word2json.logger import logger
from word2json.service import SanityClient, Services
from word2json.parseargs import make_parseargs
from word2json.parser.engine import DocXConfig, DocXParser
from word2json.models import About, Article, Casefile, Media, Rumor, Timeline
from word2json.utils import json_serial


DOCTYPE = About | Article | Casefile | Media | Rumor | Timeline


def make_parser(config: DocXConfig) -> Tuple[Type[DocXParser], Type[DOCTYPE]]:
    match config.type:
        case "casefile":
            return CasefileParser, Casefile
        case "rumor":
            return RumorParser, Rumor
        case "timeline":
            return TimelineParser, Timeline
        case "about":
            return AboutParser, About
        case "post" | "voice":
            return ArticleParser, Article
        case "media":
            return MediaParser, Media
        case _:
            raise ValueError(f"unknown document type {config.type}")


def make_task(docx: DOCTYPE, prod: DOCTYPE, dev: DOCTYPE):
    if (docx is None) and (prod is None) and (dev is None):
        msg = f"doc is not found in production, develop or local"
        logger.error(msg)
        raise ValueError(msg)

    elif (docx is not None) and (dev is None) and (prod is None):
        logger.info("Local file not present in dev or prod, prepare uploading")
        return TaskType.UPLOAD_DOCX

    elif (docx is None) and (dev is not None) and (prod is None):
        logger.info("new file found in dev, overwrite local and prod")
        return TaskType.DEV_OVERWRITE_LOCAL_AND_PROD

    elif (docx is None) and (dev is None) and (prod is not None):
        msg = "file in prod but not in dev and local, abort. Sync your database first"
        logger.error(msg)
        raise RuntimeError(msg)

    elif (docx is not None) and (dev is not None) and (prod is None):
        logger.warning("new file in local and dev, but not in production")
        logger.warning(
            "unable to track difference, merge local and dev then overwrite production"
        )
        if docx > dev:
            return TaskType.LOCAL_UPDATE_DEV_OVERWRITE_PROD
        elif docx == dev:
            return TaskType.LOCAL_OVERWRITE_PROD
        else:
            return TaskType.DEV_UPDATE_LOCAL_OVERWRITE_PROD

    elif (docx is None) and (dev is not None) and (prod is not None):
        return TaskType.DEV_UPDATE_PROD_OVERWRITE_LOCAL

    elif (docx is not None) and (dev is None) and (prod is not None):
        msg = "doc in prod and local but not in dev, abort. Sync your database first"
        logger.error(msg)
        raise RuntimeError(msg)

    elif (docx is not None) and (dev is not None) and (prod is not None):
        if dev <= prod:
            if docx > dev:
                return TaskType.LOCAL_UPDATE_DEV_OVERWRITE_PROD
            elif docx == dev:
                return TaskType.SYNCED
            else:
                return TaskType.DEV_UPDATE_LOCAL
        else:
            if dev > prod:
                if docx > dev:
                    return TaskType.LOCAL_UPDATE_DEV_OVERWRITE_PROD
                elif docx == dev:
                    return TaskType.DEV_UPDATE_PROD
                else:
                    return TaskType.DEV_UPDATE_LOCAL_OVERWRITE_PROD
            else:
                logger.debug(
                    f"dev update:{dev.updatedAt}, prod update: {prod.updatedAt}, local update: {docx.updatedAt}"
                )
                raise RuntimeError("database out of sync")


class TaskType(Enum):
    UPLOAD_DOCX = auto()
    LOCAL_UPDATE_DEV_OVERWRITE_PROD = auto()
    LOCAL_OVERWRITE_PROD = auto()
    DEV_UPDATE_LOCAL_OVERWRITE_PROD = auto()
    DEV_OVERWRITE_LOCAL_AND_PROD = auto()
    DEV_UPDATE_PROD_OVERWRITE_LOCAL = auto()
    DEV_OVERWRITE_LOCAL = auto()
    DEV_UPDATE_LOCAL = auto()
    DEV_UPDATE_PROD = auto()
    SYNCED = auto()
    ERROR = auto()


class Syncronizer(object):
    def __init__(self, config: DocXConfig, service: Services) -> None:
        self.config = config
        self.service = service
        self.docx_parser, self.doctype = make_parser(config)

    def determine_task(self, title: str) -> tuple[TaskType, DOCTYPE, DOCTYPE]:
        docx = self.docx_json(title)
        prod = self.prod_json(title)
        dev = self.dev_json(title)
        return make_task(docx, prod, dev), docx, dev

    def commit(self, title: str):
        task, docx, dev = self.determine_task(title)
        logger.info(f"task type found: {task}")
        match task:
            case TaskType.UPLOAD_DOCX:
                self.upload_docx(title, docx)
            case TaskType.LOCAL_UPDATE_DEV_OVERWRITE_PROD:
                self.local_update_dev_overwrite_prod(docx, dev)
            case TaskType.LOCAL_OVERWRITE_PROD:
                self.local_overwrite_prod(docx)
            case TaskType.DEV_UPDATE_LOCAL_OVERWRITE_PROD:
                self.dev_update_local_overwrite_prod(docx, dev, title)
            case TaskType.DEV_OVERWRITE_LOCAL_AND_PROD:
                self.dev_overwrite_local_and_prod(dev, title)
            case TaskType.DEV_UPDATE_PROD_OVERWRITE_LOCAL:
                self.dev_update_prod_overwrite_local(dev, title)
            case TaskType.DEV_OVERWRITE_LOCAL:
                self.dev_overwrite_local(dev, title)
            case TaskType.DEV_UPDATE_LOCAL:
                self.dev_update_local(docx, dev, title)
            case TaskType.DEV_UPDATE_PROD:
                self.dev_update_prod(dev)
            case TaskType.SYNCED:
                logger.info("all files synced!")
            case _:
                logger.error(TaskType.ERROR)

    def dev_update_prod(self, dev):
        payload = dev.dict(by_alias=True, exclude_none=True)
        self.sanity.insert(payload, "production")

    def dev_overwrite_local(self, dev: DOCTYPE, title):
        payload = dev.dict(by_alias=True, exclude_none=True)
        self.write_local_docx(payload, title)

    def dev_update_prod_overwrite_local(self, dev: DOCTYPE, title: str):
        payload = dev.dict(by_alias=True, exclude_none=True)
        self.sanity.insert(payload, "production")
        self.write_local_docx(payload, title)

    def dev_overwrite_local_and_prod(self, dev: DOCTYPE, title: str):
        payload = dev.dict(by_alias=True, exclude_none=True)
        self.sanity.insert(payload, "production")
        self.write_local_docx(payload, title)

    def dev_update_local_overwrite_prod(self, docx: DOCTYPE, dev: DOCTYPE, title: str):
        payload = docx.dict(by_alias=True, exclude_none=True)
        payload.update(dev.dict(by_alias=True, exclude_none=True))
        self.sanity.insert(payload, "production")
        self.write_local_docx(payload, title)

    def dev_update_local(self, docx: DOCTYPE, dev: DOCTYPE, title: str):
        payload = docx.dict(by_alias=True, exclude_none=True)
        payload.update(dev.dict(by_alias=True, exclude_none=True))
        self.write_local_docx(payload, title)
        self.sanity.insert(payload, "develop")

    def local_overwrite_prod(self, docx: DOCTYPE):
        payload = docx.dict(by_alias=True, exclude_none=True)
        self.sanity.insert(payload, "production")

    def local_update_dev_overwrite_prod(self, docx: DOCTYPE, dev: DOCTYPE):
        payload = dev.dict(by_alias=True, exclude_none=True)
        payload.update(docx.dict(by_alias=True, exclude_none=True))
        self.sanity.insert(payload, "production")
        self.sanity.insert(payload, "develop")

    def upload_docx(self, title: str, docx: DOCTYPE):
        payload = docx.dict(by_alias=True, exclude_none=True)
        self.sanity.insert(payload, "production")
        self.sanity.insert(payload, "develop")
        self.write_local_docx(payload, title)

    def write_local_docx(self, doc: dict, title: str):
        filepath = os.path.join(
            self.service.local.words_dir, self.config.type, f"{title}.json"
        )
        logger.info(f"{filepath} is saved")
        json.dump(
            doc,
            open(filepath, "w", encoding="utf8"),
            ensure_ascii=False,
            default=json_serial,
        )
        logger.info("initiate TS Engine")
        subprocess.run(
            ["ts-node", "json2word/cli.ts", "-t", self.config.type, "-n", title, "-l"],
            shell=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    @lru_cache(maxsize=None)
    def docx_json(self, title: str) -> DOCTYPE | None:
        filedir = os.path.join(self.config.output_dir, self.config.type)
        if f"{title}.docx" not in os.listdir(filedir):
            return None
        doc = self.docx_parser(title, self.config, self.service).json()
        return self.doctype.parse_obj(doc)

    @lru_cache(maxsize=None)
    def prod_json(self, title: str) -> DOCTYPE | None:
        doc = self.sanity.get_document(self.type, title, "production")
        return self.doctype.parse_obj(doc) if doc is not None else None

    @lru_cache(maxsize=None)
    def dev_json(self, title: str) -> DOCTYPE | None:
        doc = self.sanity.get_document(self.type, title, "develop")
        return self.doctype.parse_obj(doc) if doc is not None else None

    @property
    def type(self) -> str:
        return self.config.type

    @cached_property
    def sanity(self) -> SanityClient:
        return self.service.sanity.get_client()


if __name__ == "__main__":

    config = make_parseargs(["--type", "about", "--title", "测试文档2"])
    service = Services.parse_file("credential.json")

    sync = Syncronizer(config, service)
    docx = sync.docx_json(config.title)
    # sync.docx_json(config.title)
    task = sync.commit(config.title)
    # subprocess.run(
    #     ["ts-node", "json2word/cli.ts", "-t", config.type, "-n", config.title, "-l"],
    #     shell=True,
    #     stdout=sys.stdout,
    #     stderr=sys.stderr,
    # )
