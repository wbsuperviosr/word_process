import json
from typing import TYPE_CHECKING, Callable, Mapping
from word2json.utils import genKey
from datetime import datetime

if TYPE_CHECKING:
    from word2json.parser.engine import DocX


class DocTracker(object):
    def __init__(
        self,
        identifier_getter: Callable[[Mapping], str] = lambda x: x.get("title", None),
        database: str = "database.json",
    ) -> None:

        self.database = database
        self.data = json.load(open(database, "r", encoding="utf-8"))
        self.identifier_getter = identifier_getter

    def get_meta(self, docx: "DocX"):
        identity = self.identifier_getter(docx.front_matter)
        if identity is None:
            raise RuntimeError(
                "you identifier function return None, please check your identifier function"
            )
        else:
            identity = f"{docx.doctype.value}-{identity}"
        if identity in self.data.keys():
            meta = self.data[identity]
            meta.update({"_updatedAt": datetime.now().isoformat()[:-3] + "Z"})

        else:
            meta = {
                "_createdAt": datetime.now().isoformat()[:-3] + "Z",
                "_updatedAt": datetime.now().isoformat()[:-3] + "Z",
                "_type": docx.doctype.value,
                "_id": f"{genKey(8)}-{genKey(4)}-{genKey(4)}-{genKey(4)}-{genKey(12)}",
                "_rev": genKey(22),
            }
            self.data[identity] = meta
        self.save()
        return meta

    def save(self) -> None:
        json.dump(self.data, open(self.database, "w"), ensure_ascii=False)
