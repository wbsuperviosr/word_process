import sys
import os

sys.path.append(os.getcwd())
from word2json.parser.engine import TabulateParser


class AboutParser(TabulateParser):
    @property
    def image_endpoint(self) -> str:
        return f"4关于本站/{self.title}"


if __name__ == "__main__":
    from word2json.parseargs import make_parseargs
    from word2json.service import Services
    from pprint import pprint

    config = make_parseargs(["--type", "about", "--title", "测试文档"])
    service = Services.parse_file("credential.json")
    sanity = service.sanity.get_client(True)
    docx = AboutParser(config.title, config, service)

    # jsondoc = sanity.get_document(config.type, config.title)

    # docx = TimelineParser(config.title, config=config, service=service)
    payload = docx.json()
    pprint(payload["body"])
