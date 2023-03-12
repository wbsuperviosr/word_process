from word2json.parser.engine import TabulateParser


class RumorParser(TabulateParser):
    @property
    def image_endpoint(self) -> str:
        return f"5谣言澄清/{self.title}"
