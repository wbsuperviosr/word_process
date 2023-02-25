# %%
import abc
import bs4
import io
import re
import zipfile
import string
import random
from enum import Enum
from typing import Mapping
from functools import cached_property
from pprint import pprint
from PIL import Image

import json
from urllib.parse import urlparse
from pathlib import PurePosixPath

random.seed(123)


def infer_hyperlink_category(url: str):
    url = urlparse(url)
    if url.hostname == "liuxin.express":
        path = PurePosixPath(url.path)
        match path.parts[1]:
            case "voices":
                return "观者评说"
            case "casefiles":
                return "部分卷宗"
            case "rumor":
                return "辟谣问答"
            case "media":
                return "影音合集"
            case "posts":
                return "暖曦话语"
            case "timeline":
                return "时光回溯"
            case _:
                return "更多阅读"
    else:
        return "外部阅读"


def genKey(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def parse_fm_field(string: str):
    if string.isdigit():
        if "." in string:
            return float(string)
        else:
            return int(string)
    elif string == "":
        return None
    elif string in ["true", "false"]:
        if string == "false":
            return False
        else:
            return True
    else:
        return string


class ParagraphType(Enum):
    Heading = 0
    Image = 1
    Text = 2
    Misc = 3


class UploadTask(object):
    def __init__(self, target: str, name: str) -> None:
        self.target = target
        self.name = name


class Run(object):
    def __init__(self, paragraph: "Paragraph", r: bs4.element.Tag) -> None:
        self.r = r
        self.key = genKey(10)
        self.paragraph = paragraph

    @cached_property
    def text(self) -> str:
        return self.r.text

    @cached_property
    def rels(self) -> bs4.element.Tag:
        return self.paragraph.rels

    @cached_property
    def marks(self) -> list[str]:
        marks = []
        if self.r.find("w:u") is not None:
            marks.append("u")
        if self.r.find("w:b") is not None:
            marks.append("strong")
        if self.r.find("w:i") is not None:
            marks.append("em")
        if self.is_reference:
            key = genKey(10)
            self.register_markdef(key)
            marks.append(key)
        return marks

    def register_markdef(self, key):
        refid = self.r.parent.get("r:id")
        rel = self.rels.find("Relationship", {"Id": refid})
        link = rel.get("Target")
        self.markDefs.append({"_key": key, "_type": "link", "href": link})

    @cached_property
    def is_reference(self) -> bool:
        if self.r.parent.name == "hyperlink":
            return True
        return False

    @property
    def markDefs(self) -> list[str]:
        if hasattr(self, "_markDefs"):
            return self._markDefs
        self._markDefs = []
        return self._markDefs

    @property
    def json(self) -> Mapping:
        return {
            "_key": self.key,
            "_type": "span",
            "marks": self.marks,
            "text": self.text,
        }


class Paragraph(object):
    def __init__(self, p: bs4.element.Tag, docx: "DocX") -> None:
        self.p = p
        self.docx = docx
        self.key = genKey(10)

    def __repr__(self) -> str:
        return str(self.type)

    def regiser_upload_task(self, task):
        self.docx.regiser_upload_task(task)

    @cached_property
    def runs(self) -> list[bs4.element.Tag]:
        runs = self.p.find_all("w:r")
        return [Run(self, r) for r in runs]

    @cached_property
    def text(self) -> str:
        return self.p.text

    @cached_property
    def is_text(self):
        if self.is_reference:
            return False
        return self.p.text != ""

    @cached_property
    def is_heading(self):
        # return self.p.find("w:pStyle", {"w:val": "Heading1"}) is not None
        pstyle = self.p.find("w:pStyle")
        if pstyle is not None and pstyle.get("w:val").startswith("Heading"):
            return True
        return False

    @cached_property
    def is_image(self):
        return self.p.find("w:drawing") is not None

    @cached_property
    def is_reference(self):
        ref = self.p.find("w:hyperlink")
        return ref is not None

    @cached_property
    def type(self) -> ParagraphType:
        if self.is_heading:
            return ParagraphType.Heading
        elif self.is_image:
            return ParagraphType.Image
        else:
            return ParagraphType.Text

    @cached_property
    def rels(self) -> bs4.element.Tag:
        return self.docx.rels

    @cached_property
    def pStyle(self) -> str:
        pstyle = self.p.find("w:pStyle")
        if pstyle is None:
            return "normal"
        else:
            match pstyle.get("w:val").lower():
                case "listparagraph":
                    return "blockquote"
                case "heading1":
                    return "h1"
                case "heading2":
                    return "h2"
                case "heading3":
                    return "h3"
                case "heading4":
                    return "h4"
                case "heading5":
                    return "h5"
                case "heading6":
                    return "h6"
                case _:
                    return "normal"

    @property
    def json(self) -> Mapping:

        if self.is_image:
            rId = self.p.find("a:blip").get("r:embed")
            target = f"word/{self.docx.get_reference(rId)}"
            image = Image.open(io.BytesIO(self.docx.package.read(target)))
            ext = target.split(".")[-1]
            name = f"{self.docx.image_name}_{self.key}.{ext}"

            if self.p.find("w:hyperlink") is not None:
                rId = self.p.find("w:hyperlink").get("r:id")
                link = self.docx.get_reference(rId)
            else:
                link = f"{self.docx.endpoint}/{name}"
            task = UploadTask(target=target, name=name)
            self.regiser_upload_task(task)

            return {
                "_key": self.key,
                "_type": "image_urlObject",
                "width": image.width,
                "height": image.height,
                "urlField": link,
                "url_title": name,
            }
        else:
            children = [child.json for child in self.runs]
            markDefs = sum([child.markDefs for child in self.runs], [])
            return {
                "_key": self.key,
                "_type": "block",
                "children": children,
                "markDefs": markDefs,
                "style": self.pStyle,
            }

    def print(self):
        pprint(self.p.prettify())


class DocX(metaclass=abc.ABCMeta):
    def __init__(self, package: zipfile.ZipFile) -> None:
        self.package = package
        self.upload_task = []

    @classmethod
    def fromfile(cls, filename: str):
        return cls(zipfile.ZipFile(filename))

    def regiser_upload_task(self, task):
        self.upload_task.append(task)

    @cached_property
    def paragraphs(self) -> list[bs4.element.Tag]:
        return [Paragraph(p, self) for p in self.body.find_all("w:p", recursive=False)]

    @cached_property
    def document(self) -> bs4.element.Tag:
        return self.parse_xml("document", "word/document.xml")

    @cached_property
    def rels(self) -> bs4.element.Tag:
        return self.parse_xml("Relationships", "word/_rels/document.xml.rels")

    @cached_property
    def body(self) -> bs4.element.Tag:
        return self.document.find("body")

    @cached_property
    def table(self) -> bs4.element.Tag:
        return self.body.find("w:tbl")

    @abc.abstractproperty
    def front_matter(self) -> dict:
        pass

    @abc.abstractproperty
    def field_map(self) -> dict:
        pass

    @abc.abstractproperty
    def endpoint(self) -> str:
        pass

    def get_reference(self, rId: str):
        return self.rels.find("Relationship", {"Id": rId}).get("Target")

    def parse_xml(self, tagname: str, filename: str):
        doc = self.package.read(filename)
        soup = bs4.BeautifulSoup(doc, features="lxml-xml")
        return soup.find(tagname)

    def parse_table(self, field_name: str, field: bs4.element.Tag):
        match field_name:
            case "slug":
                return {"slug": {"_type": "slug", "current": field.text}}
            case "tags":
                return re.split("[,，、]", field.text)
            case "related":
                links = field.find_all("w:hyperlink")
                return [
                    {
                        "title": l.text,
                        "urlField": self.get_reference(l.get("r:id")),
                        "category": infer_hyperlink_category(
                            self.get_reference(l.get("r:id"))
                        ),
                    }
                    for l in links
                ]
            case _:
                return parse_fm_field(field.text)

    @cached_property
    def json(self) -> list[Mapping]:
        return [p.json for p in self.paragraphs]

    @cached_property
    def image_name(self) -> str:
        return f"{self.front_matter['title']}"

    def print(self):
        pprint(self.body.prettify())


class ArticleParser(DocX):
    @cached_property
    def front_matter(self) -> dict:
        fm = {}
        rows = self.table.find_all("w:tr")
        for row in rows:
            cols = row.find_all("w:tc")
            field_name = self.field_map[cols[0].text]
            fm[field_name] = self.parse_table(field_name, cols[1])

        return fm


class CasefileParser(ArticleParser):
    @cached_property
    def field_map(self) -> dict:
        map = dict(
            title="标题",
            description="摘要",
            header="头文件",
            slug="链接",
            order="顺序",
            mainImageUrl="配图链接",
            featured="置顶",
            tags="标签",
            classification="类别",
            publishedAt="发布时间",
            writtenAt="收录时间",
            related="扩展阅读",
        )
        return {v: k for k, v in map.items()}

    @property
    def endpoint(self) -> str:
        return f"6部分卷宗/{self.field_map['标题']}"


class PostParser(ArticleParser):
    @cached_property
    def field_map(self) -> dict:
        map = dict(
            title="标题",
            description="摘要",
            slug="链接",
            mainImageUrl="配图链接",
            featured="置顶",
            tags="标签",
            category="类别",
            author="作者",
            publishedAt="发布时间",
            writtenAt="收录时间",
            related="扩展阅读",
        )
        return {v: k for k, v in map.items()}

    @property
    def endpoint(self) -> str:
        return f"3观者评说/{self.field_map['作者']/{self.field_map['标题']}}"


docx = PostParser.fromfile("mswords/post/支持刘鑫的人怎么想的【1定义优先】.docx")
print(docx.json)
