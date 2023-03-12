# %%
from typing import Optional
from word2json.models.base import *
from datetime import datetime, date


class Casefile(BaseDocument):

    body: Optional[list[Body]]
    category: Optional[str]
    description: Optional[str]
    featured: Optional[bool]
    header: Optional[str]
    mainImageUrl: Optional[str]
    order: Optional[int | float]
    slug: Optional[Slug]
    tags: Optional[list[str]]
    title: Optional[str]
    writtenAt: Optional[datetime]
    publishedAt: Optional[datetime]
    imageUrls: Optional[list[ImageUrl]]
    articleUrls: Optional[list[ArticleUrl]]
