from word2json.parser.engine import TabulateParser


class MediaParser(TabulateParser):
    @property
    def image_endpoint(self) -> str:
        return f"影音资料/{self.title}"
