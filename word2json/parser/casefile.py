# %%
from word2json.parser.engine import ArticleParser


class CasefileParser(ArticleParser):
    @property
    def image_endpoint(self) -> str:
        return f"6部分卷宗/{self.title}"

    @property
    def imageInFM(self) -> bool:
        return True


if __name__ == "__main__":
    from word2json.parseargs import make_parseargs
    from word2json.service import Services

    config = make_parseargs(["--type", "casefile", "--title", "公审第1回检方陈述"])
    service = Services.parse_file("credential.json")
    sanity = service.sanity.get_client(True)
    jsondoc = sanity.get_document(config.type, config.title)

    docx = CasefileParser(config.title, config=config, service=service)
    payload = docx.json()
