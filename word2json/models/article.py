# %%
from typing import Optional
from word2json.models.base import *


class Article(BaseDocument):
    articleUrls: Optional[list[ArticleUrl]]
    author: Optional[str]
    body: Optional[list[Body]]
    category: Optional[str]
    description: Optional[str]
    featured: Optional[bool]
    mainImageUrl: Optional[str]
    publishedAt: Optional[str]
    slug: Optional[Slug]
    tags: Optional[list[str]]
    title: Optional[str]
    writtenAt: Optional[str]
