# %%
from typing import Optional
from word2json.models.base import *


class About(BaseDocument):
    body: Optional[list[Body]]
    footer: Optional[list[str]]
    mainImageUrl: Optional[str]
    quote: Optional[str]
    slug: Optional[Slug]
    subtitle: Optional[str]
    title: Optional[str]
