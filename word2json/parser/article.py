from word2json.parser.engine import ArticleParser


class PostParser(ArticleParser):
    @property
    def image_endpoint(self) -> str:
        return f"2暖曦话语/{self.title}"


class VoiceParser(ArticleParser):
    @property
    def image_endpoint(self) -> str:
        return f"3观者评说/{self.title}"
