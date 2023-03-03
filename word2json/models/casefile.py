# %%
from typing import Optional
from word2json.models.base import *


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
    writtenAt: Optional[str]
    publishedAt: Optional[str]
    imageUrls: Optional[list[ImageUrl]]
    articleUrls: Optional[list[ArticleUrl]]
