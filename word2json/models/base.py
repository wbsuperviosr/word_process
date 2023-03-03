# %%
from typing import Optional
from pydantic import BaseModel, Field


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


class BaseDocument(BaseModel):
    id: str = Field(alias="_id")
    rev: str = Field(alias="_rev")
    type: str = Field(alias="_type")
    createdAt: str = Field(alias="_createdAt")
    updatedAt: str = Field(alias="_updatedAt")
