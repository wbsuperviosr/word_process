from functools import cached_property
import json
import os
from typing import Mapping
from bs4 import Tag
from word2json.parser.engine import TabulateParser


zhen = {v: k for k, v in json.load(open("EnZh.json", "r", encoding="utf8")).items()}


class TimelineParser(TabulateParser):
    @property
    def image_endpoint(self) -> str:
        return f"7时光回溯/{self.title}"

    @cached_property
    def tables(self) -> Tag:
        return self.body.find_all("w:tbl")

    def is_title(self, title: bool, table: Tag):
        rows = table.find_all("w:tr")
        for row in rows:
            cols = row.find_all("w:tc")
            if cols[0].text == "标题" and cols[1].text == title:
                return True
        return False

    @property
    def front_matter(self) -> Mapping:
        for table in self.tables:
            if not self.is_title(self.title, table):
                continue
            fm = {}
            rows = table.find_all("w:tr")
            for row in rows:
                cols = row.find_all("w:tc")
                try:
                    field_name = zhen[cols[0].text]
                except KeyError:
                    raise KeyError(f"{cols[0].text} is not found in zhen dictionary")
                fm[field_name] = self.parse_field(field_name, cols[1])
            return fm

    @property
    def filepath(self) -> str:
        return os.path.join(self.config.output_dir, self.type, "时间线.docx")
