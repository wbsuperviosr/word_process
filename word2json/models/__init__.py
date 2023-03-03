# %%
from word2json.models.base import BaseDocument
from word2json.models.about import About
from word2json.models.article import Article
from word2json.models.casefile import Casefile
from word2json.models.timeline import Timeline
from word2json.models.rumor import Rumor
from typing import Type


class Collection(object):
    def __init__(self, class_: Type[BaseDocument]) -> None:
        self.class_ = class_
        self.documents: list[BaseDocument] = []

    def __repr__(self) -> str:
        return repr(self.documents)

    def parse_obj(self, documents: list[dict]) -> "Collection":
        for doc in documents:
            self.documents.append(self.class_.parse_obj(doc))
        return self
