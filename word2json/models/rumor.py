# %%
from typing import Optional
from word2json.models.base import *


class Rumor(BaseDocument):
    author: Optional[str]
    importance: Optional[int | float]
    rumorSpreader: Optional[list[str]]
    rumorVictim: Optional[list[str]]

    rumor: Optional[str]
    rumorArticleUrls: Optional[list[ArticleUrl]]
    rumorImageUrls: Optional[list[ImageUrl]]

    tags: Optional[list[str]]
    title: Optional[str]

    truth: Optional[str]
    truthArticleUrls: Optional[list[ArticleUrl]]
    truthImageUrls: Optional[list[ImageUrl]]
