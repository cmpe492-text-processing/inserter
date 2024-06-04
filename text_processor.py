import nltk

from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
import re


class TextProcessor:
    def __init__(self):
        self._nltk = nltk
        self._nlp = spacy.load("en_core_web_sm")
        self._link_pattern = r"http\S+"
        self._markdown_link_pattern = r"\[([^\]]+)\]\((http\S+)\)"

    @property
    def nlp(self):
        return self._nlp

    def clean_text(self, txt: str) -> str:
        txt = txt.lower()
        txt = self.replace_links(txt)
        txt = self.remove_punctuation(txt)
        txt = txt.replace("\\", " ").replace("[", " ").replace("]", " ")
        txt = txt.strip()
        return txt

    @staticmethod
    def get_sentiment_scores(sentence: str) -> (float, float, float, float):
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(sentence)
        return scores["compound"], scores["pos"], scores["neg"], scores["neu"]

    @staticmethod
    def remove_punctuation(txt: str) -> str:
        return re.sub(r"[^\w\s\-\'\.,]", "", txt)

    def replace_links(self, txt: str) -> str:
        def replace_plain_links(match):
            if re.match(self._markdown_link_pattern, match.group(0)):
                return match.group(0)
            return "<link>"

        def replace_markdown_link(match):
            return match.group(1)

        txt = re.sub(self._markdown_link_pattern, replace_markdown_link, txt)
        txt = re.sub(
            r"(\[([^\]]+)\]\((http\S+)\))|" + self._link_pattern,
            replace_plain_links,
            txt,
        )
        return txt
