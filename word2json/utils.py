import random
import string
from urllib.parse import urlparse
from pathlib import PurePosixPath

random.seed(123)


def infer_hyperlink_category(url: str):
    url = urlparse(url)
    if url.hostname == "liuxin.express":
        path = PurePosixPath(url.path)
        match path.parts[1]:
            case "voices":
                return "观者评说"
            case "casefiles":
                return "部分卷宗"
            case "rumor":
                return "辟谣问答"
            case "media":
                return "影音合集"
            case "posts":
                return "暖曦话语"
            case "timeline":
                return "时光回溯"
            case _:
                return "更多阅读"
    else:
        return "外部阅读"


def genKey(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
