# %%
from typing import Optional
from word2json.models.base import *


class Media(BaseDocument):
    title: Optional[str]
    subtitle: Optional[str]
    slug: Optional[Slug]
    author: Optional[str]
    mediaUrl: Optional[str]
    category: Optional[str]
    tags: Optional[list[str]]
    mainImageUrl: Optional[str]
    description: Optional[str]
    body: Optional[list[Body]]
    writtenAt: Optional[str]
    publishedAt: Optional[str]
    downloadLink: Optional[str]
    downloadMeta: Optional[str]
