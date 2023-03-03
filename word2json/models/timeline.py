# %%
from typing import Optional
from word2json.models.base import *


class Timeline(BaseDocument):
    body: Optional[list[Body]]
    category: Optional[str]
    date: Optional[str]
    time: Optional[str]
    order: Optional[int | float]
    tags: Optional[list[str]]
    title: Optional[str]
    source: Optional[str]
    people: Optional[list[str]]
    imageUrls: Optional[list[ImageUrl]]
    articleUrls: Optional[list[ArticleUrl]]
