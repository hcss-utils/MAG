import requests
import pandas as pd
from time import sleep


class MAG:
    ENDPOINT = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate"
    ENTITIES = {
        "DN": "original_paper_title",
        "Ti": "normalized_title",
        "W": "normalized_words_in_title",
        "AW": "normalized_words_in_abstract",
        "RA": "restored_abstract",
        "IA": "inverted_abstract",
        "AA": "authors",
        "AA.AuId": "author_id",
        "AA.DAuN": "author_name",
        "Y": "year_published",
        "D": "isodate_published",
        "DOI": "DOI",
        "J": "journals",
        "J.JN": "journal_name",
        "PB": "publisher",
        "ECC": "estimated_citation_count",
        "F": "fields",
        "F.DFN": "field_of_study",
        "F.FN": "normalized_field_of_study",
    }

    def __init__(
        self,
        expr: str,
        key: str,
        count: int = 1_000,
        offset: int = 0,
        max_results: int = 5_000,
        model: str = "latest",
        attr: str = "DN,Ti,W,AW,IA,AA.AuId,AA.DAuN,Y,D,DOI,J.JN,PB,ECC,F.DFN,F.FN",
    ):
        self.expr = expr
        self.key = key
        self.count = count
        self.offset = offset
        self.max_results = max_results
        self.model = model
        self.attr = attr

        self.json_data = None
        self.table_data = None

    def download_publications(self):
        """Download entities."""
        records = list(self.yield_records())
        self.json_data = records
        self.table_data = (
            pd.DataFrame(records)
            .drop(["prob", "logprob"], axis=1)
            .rename(columns=MAG.ENTITIES)
        )

    def fetch(self, url, params):
        """Make a remote call to API."""
        return requests.get(url, params).json()

    def restore_abstract(self, abstract):
        """Restores inverted abstract to its original form."""
        words = abstract["InvertedIndex"]
        total_words = abstract["IndexLength"]

        text = []
        for position in range(0, total_words):
            for word, positions in words.items():
                if position in positions:
                    text.append(word)
        return " ".join(text)

    def process(self, entities):
        """ """
        for entity in entities:
            entity["RA"] = self.restore_abstract(entity["IA"])
            yield entity

    def yield_records(self):
        """ """
        params = {
            "expr": self.expr,
            "offset": self.offset,
            "count": self.count,
            "attributes": self.attr,
            "model": self.model,
            "subscription-key": self.key,
        }
        toreturn = self.max_results
        while toreturn >= 0:
            data = self.fetch(MAG.ENDPOINT, params)
            yield from self.process(data["entities"])
            toreturn -= self.count
            params["offset"] += self.count
            sleep(3.1)
