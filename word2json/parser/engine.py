# %%
import abc
import io
import json
import os
import re
import sys
import hashlib
import pathlib
from datetime import datetime
from dateutil import parser, tz
from functools import cached_property
from typing import Mapping

from bs4 import BeautifulSoup
from bs4.element import Tag
from PIL import Image


sys.path.append(os.getcwd())
from word2json.parseargs import DocXConfig
from word2json.service import Services


literals = dict(json.load(open("literals.json", "r", encoding="utf8"))["literal"])
zhen = {v: k for k, v in json.load(open("EnZh.json", "r", encoding="utf8")).items()}


class ObjectParser(metaclass=abc.ABCMeta):
    def __init__(self, tag: Tag, docx: "DocXParser") -> None:
        self.tag = tag
        self.docx = docx

    @abc.abstractmethod
    def json(self) -> Mapping:
        pass


class ArticleUrlParser(ObjectParser):
    def json(self) -> Mapping:
        payload = []
        for hlink in self.tag.find_all("w:hyperlink"):
            obj = {}
            obj["urlTitle"] = hlink.text
            obj["urlField"] = self.docx.get_reference(hlink.get("r:id"))
            obj["_type"] = "articleUrlObject"
            obj["_key"] = hashlib.sha1(
                f"{obj['urlTitle']}{obj['urlField']}".encode()
            ).hexdigest()[:12]
            payload.append(obj)
        return payload


class ImageHandle(ObjectParser):
    def __init__(self, tag: Tag, docx: "DocXParser") -> None:
        super().__init__(tag, docx)
        self.docx.images.append(self)

    @property
    def key(self) -> str:
        return self.hashbytes[:12]

    @property
    def key2(self) -> str:
        return self.hashbytes[12:24]

    @property
    def key3(self) -> str:
        return self.hashbytes[24:36]

    @cached_property
    def hashbytes(self) -> str:
        return hashlib.sha1(self.bytes).hexdigest()

    @cached_property
    def link_key(self) -> str:
        return hashlib.sha1(self.link.encode()).hexdigest()[:10]

    @property
    def text(self) -> str:
        return self.tag.text

    @property
    def width(self) -> str:
        return self.image_obj.width

    @property
    def height(self) -> str:
        return self.image_obj.height

    @property
    def link(self) -> str:
        if self.tag.find("w:hyperlink") is not None:
            rId = self.tag.find("w:hyperlink").get("r:id")
            link = self.docx.get_reference(rId)
        else:
            link = f"{self.docx.endpoint}/{self.image_name}"
        return link

    @cached_property
    def image_obj(self) -> Image.Image:
        return Image.open(io.BytesIO(self.bytes))

    @cached_property
    def bytes(self) -> bytes:
        return self.docx.read_media(self.target.as_posix())

    @property
    def image_name(self) -> str:
        return f"{self.docx.image_name}_{self.docx.image_count}{self.suffix}"

    @property
    def suffix(self) -> str:
        return self.target.suffix

    @property
    def target(self) -> pathlib.Path:
        rId = self.tag.find("a:blip").get("r:embed")
        target = pathlib.Path(f"word/{self.docx.get_reference(rId)}")
        return target

    def json(self) -> Mapping:
        return {}


class ImageUrlParser(ObjectParser):
    def parse(self, tag) -> Mapping:
        image = ImageHandle(tag, self.docx)

        return {
            "_key": image.key,
            "_type": "imageUrlObject",
            "width": image.width,
            "height": image.height,
            "urlField": image.link,
            "urlTitle": image.image_name,
        }

    def json(self) -> Mapping:
        payload = []
        for tag in self.tag.find_all("w:p"):
            payload.append(self.parse(tag))
        return payload


class Paragraph(ObjectParser):
    def json(self) -> Mapping:
        if self.is_image:
            return ImageParagraph(self.tag, self.docx).json()
        return TextParagraph(self.tag, self.docx).json()

    @cached_property
    def is_image(self):
        return self.tag.find("w:drawing") is not None

    @property
    def pStyle(self) -> str:
        pstyle = self.tag.find("w:pStyle")
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


class ImageParagraph(Paragraph):
    def json(self) -> Mapping:
        if self.docx.imageInFM:
            return ImageUrlParser(self.tag, self.docx).parse(self.tag)
        image = ImageHandle(self.tag, self.docx)
        return {
            "_key": image.key,
            "_type": "block",
            "children": [
                {
                    "_key": image.link_key,
                    "_type": "span",
                    "marks": [image.key2],
                    "text": image.text,
                }
            ],
            "markDefs": [
                {"_key": image.key2, "_type": "imagelink", "href": image.link}
            ],
            "style": self.pStyle,
        }


class TextRun(ObjectParser):
    @property
    def key(self) -> str:
        hashstring = hashlib.sha1(f"{self.docx.title}{self.tag.text}".encode())
        return hashstring.hexdigest()[:12]

    @property
    def marks(self) -> list[str]:
        if hasattr(self, "_marks"):
            return self._marks
        self._marks = []
        return self._marks

    def register_marks(self):
        if self.tag.find("w:u") is not None:
            self.marks.append("u")
        if self.tag.find("w:b") is not None:
            self.marks.append("strong")
        if self.tag.find("w:i") is not None:
            self.marks.append("em")
        if self.tag.parent.name == "hyperlink":
            self.marks.append(self.register_link())

    def register_link(self):
        link = self.docx.get_reference(self.tag.parent.get("r:id"))
        key = hashlib.sha1(f"{link}{self.tag.text}".encode()).hexdigest()[:12]
        self.markDefs.append({"_key": key, "_type": "link", "href": link})
        return key

    @cached_property
    def is_footnote(self):
        if self.tag.find("w:rStyle", {"w:val": "FootnoteReference"}) is not None:
            return True
        return False

    @property
    def markDefs(self) -> list[str]:
        if hasattr(self, "_markDefs"):
            return self._markDefs
        self._markDefs = []
        return self._markDefs

    def json(self) -> Mapping:
        self.register_marks()
        return {
            "_key": self.key,
            "_type": "span",
            "marks": self.marks,
            "text": self.tag.text,
        }

    @property
    def registered(self) -> bool:
        if not hasattr(self, "_registered"):
            return False
        return self._registered

    @registered.setter
    def registered(self, value: bool) -> None:
        self._registered = value


class FootnoteParser(ObjectParser):
    def find_footnote(self) -> Tag:
        fid = self.tag.find("w:footnoteReference").get("w:id")
        footnote = self.docx.footnotes.find_all("w:footnote", {"w:id": fid})
        for f in footnote:
            if f.text != "":
                return f

    def find_link(self, footnote: Tag):

        linktag = footnote.find("w:hyperlink")
        if linktag is not None:
            rid = linktag.get("r:id")
            link = self.docx.get_footnote_reference(rid)
            return link
        return None

    def json(self) -> Mapping:
        footnote = self.find_footnote()
        link = self.find_link(footnote)
        key = hashlib.sha1(f"{footnote.text}{link}".encode()).hexdigest()[:12]
        return {
            "_key": key,
            "_type": "reference_url",
            "title": footnote.text,
            "urlField": link,
        }


class TextParagraph(Paragraph):
    @cached_property
    def key(self) -> str:
        return hashlib.sha1(self.tag.text.encode()).hexdigest()[:12]

    @cached_property
    def runs(self) -> list[TextRun]:
        tag_runs = self.tag.find_all("w:r")
        tag_runs = [self.tag] if len(tag_runs) == 0 else tag_runs
        return [TextRun(r, self.docx) for r in tag_runs]

    @property
    def has_footnotes(self) -> bool:
        if self.tag.find("w:rStyle", {"w:val": "FootnoteReference"}) is not None:
            return True
        return False

    def _register_footnotes(self, ancher: TextRun, footnotes: list[TextRun]):
        references = [FootnoteParser(f.tag, self.docx).json() for f in footnotes]
        key = hashlib.sha1(json.dumps(references).encode()).hexdigest()[:12]
        ancher.marks.append(key)
        ancher.markDefs.append(
            {"_key": key, "_type": "Citelink", "reference": references}
        )

    def register_footnotes(self):
        for i, run in enumerate(self.runs):
            if not run.registered:
                if run.is_footnote:
                    if i == 0:
                        raise RuntimeError(
                            "you can't place the footnote at the beginning of paragraph"
                        )
                    anchor = self.runs[i - 1]
                    run.registered = True
                    footnotes = [run]
                    if i < len(self.runs) - 1:
                        for crun in self.runs[i + 1 :]:
                            if crun.is_footnote:
                                crun.registered = True
                                footnotes.append(crun)
                            else:
                                break
                    self._register_footnotes(anchor, footnotes)

    def json(self) -> Mapping:
        if self.has_footnotes:
            self.register_footnotes()
        children = [child.json() for child in self.runs if not child.is_footnote]
        markDefs = sum([child.markDefs for child in self.runs], [])

        return {
            "_key": self.key,
            "_type": "block",
            "children": children,
            "markDefs": markDefs,
            "style": self.pStyle,
        }


class BodyParser(ObjectParser):
    def json(self) -> Mapping:
        payload = {}
        if self.docx.imageInFM:
            payload.update({"imageUrls": [p.json() for p in self.images]})
            payload.update({"body": [p.json() for p in self.texts]})
        else:
            payload.update({"body": [p.json() for p in self.paragraphs]})

        return payload

    @cached_property
    def paragraphs(self) -> list[Paragraph]:
        return [
            Paragraph(p, self.docx) for p in self.tag.find_all("w:p", recursive=False)
        ]

    @cached_property
    def texts(self) -> list[Paragraph]:
        return [p for p in self.paragraphs if not p.is_image]

    @cached_property
    def images(self) -> list[Paragraph]:
        return [p for p in self.paragraphs if p.is_image]


class DocXParser(metaclass=abc.ABCMeta):
    def __init__(self, title: str, config: DocXConfig, service: Services) -> None:
        self.title = title[-4:] if title.endswith("docx") else title
        self.config = config
        self.service = service
        self.images: list[ImageHandle] = []
        self.image_count = 0

    @abc.abstractproperty
    def imageInFM(self) -> bool:
        pass

    @abc.abstractproperty
    def bodyInFM(self) -> bool:
        pass

    @abc.abstractproperty
    def image_endpoint(self) -> str:
        pass

    @abc.abstractproperty
    def image_name(self) -> str:
        pass

    @property
    def type(self) -> str:
        return self.config.type

    def post_process(self, doc: Mapping) -> Mapping:
        if doc["_id"] == "":
            s = self.hash
            doc["_id"] = f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:32]}"
        if doc["_rev"] == "":
            doc["_rev"] = f"{self.hash[-22:]}"

        local = self.service.local.get_client()
        info = local.get_fileinfo(self.type, self.title)
        doc["_updatedAt"] = info["mtime"]

        return doc

    def read_tag(self, tag_name: str, xlm_sheet: str) -> Tag:
        soup = BeautifulSoup(
            self.service.local.get_client().read(self.type, self.title, xlm_sheet),
            features="lxml-xml",
        )
        tag = soup.find(tag_name)
        if tag is None:
            raise ValueError(f"no tag {tag} is found in {xlm_sheet}")
        return tag

    def read_media(self, target: str) -> bytes:
        return self.service.local.get_client().read(self.type, self.title, target)

    def json(self) -> Mapping:
        payload = self.front_matter.copy()
        if not self.bodyInFM:
            payload.update(BodyParser(self.body, self).json())
        return self.post_process(payload)

    @cached_property
    def hash(self) -> str:
        hash_string = f"{self.config.type}-{self.title}"
        return hashlib.sha1(hash_string.encode("utf8")).hexdigest()

    @cached_property
    def body(self) -> Tag:
        return self.tag.find("body")

    @cached_property
    def table(self) -> Tag:
        return self.body.find("w:tbl")

    @cached_property
    def tag(self) -> Tag:
        return self.read_tag("document", "word/document.xml")

    @cached_property
    def rels(self) -> Tag:
        return self.read_tag("Relationships", "word/_rels/document.xml.rels")

    @cached_property
    def footnote_rels(self) -> Tag:
        try:
            return self.read_tag("Relationships", "word/_rels/footnotes.xml.rels")
        except Exception:
            raise FileNotFoundError("There is no footnote defined in the document")

    @cached_property
    def footnotes(self) -> Tag:
        try:
            return self.read_tag("footnotes", "word/footnotes.xml")
        except Exception:
            raise FileNotFoundError("There is no footnote defined in the document")

    @cached_property
    def literals(self) -> dict[str, str]:
        return dict(json.load(open("literals.json", "r", encoding="utf8"))["literal"])

    @cached_property
    def zhen(self) -> dict[str, str]:
        return {
            v: k for k, v in json.load(open("EnZh.json", "r", encoding="utf8")).items()
        }

    def get_reference(self, rId: str):
        return self.rels.find("Relationship", {"Id": rId}).get("Target")

    def get_footnote_reference(self, rId: str):
        return self.footnote_rels.find("Relationship", {"Id": rId}).get("Target")

    def parse_field(self, tag_name: str, tag: Tag):
        literal = literals[tag_name]
        match literal:
            case "string" | "date" | "time":
                return tag.text
            case "boolean":
                return True if tag.text == "true" else False
            case "number":
                num = tag.text
                return float(num) if "." in num else int(num)
            case "listString":
                return re.split("[,，]", tag.text)
            case "datetime":
                dt = parser.parse(tag.text)
                return dt
            case "slug":
                return {"slug": {"_type": "slug", "current": tag.text}}
            case "listArticleUrl":
                return ArticleUrlParser(tag, self).json()
            case "listImageUrl":
                return ImageUrlParser(tag, self).json()
            case "body":
                return BodyParser(tag, self).json()
            case _:
                raise ValueError(f"unknown literal for {tag_name}")

    @cached_property
    def front_matter(self) -> Mapping:
        fm = {}
        rows = self.table.find_all("w:tr")
        for row in rows:
            cols = row.find_all("w:tc")
            try:
                field_name = zhen[cols[0].text]
            except KeyError:
                raise KeyError(f"{cols[0].text} is not found in zhen dictionary")
            if cols[1].text != "":
                parsed = self.parse_field(field_name, cols[1])
                if isinstance(parsed, dict):
                    for key, item in parsed.items():
                        fm[key] = item
                else:
                    fm[field_name] = parsed
            # fm[field_name] = self.parse_field(field_name, cols[1])
        return fm


class ArticleParser(DocXParser):
    @property
    def imageInFM(self) -> bool:
        return False

    @property
    def bodyInFM(self) -> bool:
        return False

    @property
    def image_name(self) -> str:
        return self.title

    @property
    def image_endpoint(self) -> str:
        return ""


class TabulateParser(ArticleParser):
    @property
    def imageInFM(self) -> bool:
        return True

    @property
    def bodyInFM(self) -> bool:
        return True


if __name__ == "__main__":
    from word2json.parseargs import make_parseargs
    from word2json.service import Services

    config = make_parseargs(["--type", "casefile", "--title", "公审第1回检方陈述"])
    service = Services.parse_file("credential.json")
    sanity = service.sanity.get_client(True)
    docx = ArticleParser(config.title, config, service)

    # jsondoc = sanity.get_document(config.type, config.title)

    # docx = TimelineParser(config.title, config=config, service=service)
    payload = docx.json()
