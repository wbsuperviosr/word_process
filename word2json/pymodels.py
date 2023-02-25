# %%
import json
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Child(BaseModel):
    key: str
    type: str
    marks: List[str]
    text: str


class MarkDef(BaseModel):
    key: str
    type: str
    href: str


class Body(BaseModel):
    key: str
    type: str
    children: List[Child]
    markDefs: List[MarkDef]
    style: str
    level: Optional[int] = None
    listItem: Optional[str] = None


class ImageUrl(BaseModel):
    key: Optional[str]
    type: Optional[str]
    urlFiled: Optional[str]
    url_title: Optional[str]
    height: Optional[int | float]
    width: Optional[int | float]


class Related(BaseModel):
    title: str
    urlField: str
    category: str


class Author(BaseModel):
    ref: str
    type: str


class Slug(BaseModel):
    type: str = Field(default="slug")
    current: str


class DictMixIn(object):
    def update(self, data: dict) -> "DictMixIn":
        update = self.dict()
        update.update(data)
        for k, v in self.validate(update).dict().items():
            setattr(self, k, v)
        return self

    def to_dict(self, **kwargs):
        d = super().dict(**kwargs)
        for key in ["id", "rev", "type", "updatedAt", "createdAt", "ref", "key"]:
            if key in d.keys():
                d["_" + key] = d.pop(key)
        return d

    def to_json(self, **kwargs):
        d = self.to_dict()

        return json.dumps(d, ensure_ascii=False)


class Casefile(DictMixIn, BaseModel):
    createdAt: Optional[str] = Field(None, alias="_createdAt")
    id: Optional[str] = Field(None, alias="_id")
    rev: Optional[str] = Field(None, alias="_rev")
    type: Optional[str] = Field("post", alias="_type")
    updatedAt: Optional[str] = Field(None, alias="_updatedAt")

    title: Optional[str] = Field(None, alias="标题")
    description: Optional[str] = Field(None, alias="摘要")
    header: Optional[str] = Field(None, alias="头文件")
    slug: Optional[Slug] = Field(None, alias="链接")
    order: Optional[int | float] = Field(None, alias="顺序")
    mainImageUrl: Optional[str] = Field(None, alias="配图链接")
    featured: Optional[bool] = Field(None, alias="置顶")
    tags: Optional[List[str]] = Field(None, alias="标签")
    image_urls: Optional[List[ImageUrl]]
    classification: Optional[str] = Field(None, alias="类别")
    publishedAt: Optional[str] = Field(None, alias="发布时间")
    writtenAt: Optional[str] = Field(None, alias="收录时间")

    body: Optional[List[Body]]
    related: Optional[List[Related]] = Field(None, alias="扩展阅读")

    class Config:
        allow_population_by_field_name = True

    @validator("slug", pre=True)
    def valid_slug(cls, value):
        if isinstance(value, str):
            return {"type": "slug", "current": value}

    @validator("tags", pre=True)
    def valid_tags(cls, value):
        if isinstance(value, str):
            return [value]
