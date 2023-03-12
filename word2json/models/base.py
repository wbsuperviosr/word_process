# %%
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from functools import total_ordering


class ImageUrl(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    height: Optional[str]
    urlField: str
    urlTitle: str
    width: Optional[str]


class ArticleUrl(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    urlField: str
    urlTitle: str


class Child(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    marks: list[str] = Field(default_factory=list)
    text: str = Field()


class Reference(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    title: str
    urlField: str


class MarkDef(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    reference: Optional[list[Reference]]

    href: Optional[str]


class Slug(BaseModel):
    type: str = Field(alias="_type")
    current: str


class Body(BaseModel):
    key: str = Field(alias="_key")
    type: str = Field(alias="_type")
    children: list[Child]
    markDefs: list[MarkDef]
    style: Optional[str]
    level: Optional[int | float]
    listItem: Optional[str]


@total_ordering
class BaseDocument(BaseModel):
    id: str = Field(alias="_id")
    rev: str = Field(alias="_rev")
    type: str = Field(alias="_type")
    createdAt: datetime = Field(alias="_createdAt")
    updatedAt: datetime = Field(alias="_updatedAt")

    def __eq__(self, __o: "BaseDocument") -> bool:
        if self.id == __o.id:
            diff = (self.updatedAt - __o.updatedAt).total_seconds()
            if diff == 0:
                return True
            return False
        raise TypeError(f"you can't compare document with different id")

    def __lt__(self, __o: "BaseDocument") -> bool:
        if self.id == __o.id:
            diff = (self.updatedAt - __o.updatedAt).total_seconds()
            if diff < 0:
                return True
            return False
        raise TypeError(f"you can't compare document with different id")

    def __gt__(self, __o: "BaseDocument") -> bool:
        if self.id == __o.id:
            diff = (self.updatedAt - __o.updatedAt).total_seconds()
            if diff > 0:
                return True
            return False
        raise TypeError(f"you can't compare document with different id")

    # @validator("createdAt", pre=True)
    # def createdAt_validate(cls, v):
    #     return datetime.fromisoformat(v)

    # @validator("updatedAt", pre=True)
    # def createdAt_validate(cls, v):
    #     return datetime.fromisoformat(v)


class DocumentType(Enum):
    Casefile = "casefile"
    Voice = "voice"
    Rumor = "rumor"
    Timeline = "timeline"
    Post = "post"
    About = "about"
    Media = "media"
    Developer = "dev"
