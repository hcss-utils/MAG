# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
from time import sleep
from .logger import logger


class MAG:
    """Papers retrieved from Microsoft Academic API.


    Attributes
    ----------
    expr: str
        query expression [1]
    key: str
        subscription key [2]
    count: int, defaults to 1000
        number of entities retrivied with each request
    offset: int, defaults to 0
        retrieve a subset of entities starting with the offset value
    model: str, defaults to latest
        API's internal model
    attr: str, defaults to "DN,Ti,W,AW,IA,AA.AuId,AA.DAuN,Y,D,DOI,J.JN,PB,ECC,F.DFN,F.FN"
        entity attributes to retrieve [3]


    Usage
    -----
    >>> from mag import MAG
    >>> pubs = MAG(
            expr="And(And(AW='organized', AW='crime', Y=[2000, 2020]), Composite(F.FN='political science'))",
            key="2q3b955bfa210f9aa1a4eq35fa63378c"
        )
    >>> pubs.download_publications()
    >>> pubs.save(tocsv="../data/data.csv")
    >>> pubs.save(tojson="../data/data.json")


    References
    ----------
    [1] Query expression syntax, https://docs.microsoft.com/en-us/academic-services/project-academic-knowledge/reference-query-expression-syntax
    [2] Accessing Subscription key, https://msr-apis.portal.azure-api.net/
    [3] Entity Attributes, https://docs.microsoft.com/en-us/academic-services/project-academic-knowledge/reference-paper-entity-attributes
    """

    ENDPOINT = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate"
    ENTITIES = {
        "Id": "mag_ID",
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
        model: str = "latest",
        attr: str = "DN,Ti,W,AW,IA,AA.AuId,AA.DAuN,Y,D,DOI,J.JN,PB,ECC,F.DFN,F.FN",
    ):
        self.expr = expr
        self.key = key
        self.count = count
        self.offset = offset
        self.model = model
        self.attr = attr

        self.json_data = None
        self.table_data = None

    def download_publications(self):
        """Download entities."""
        logger.info(f"Calling Microsoft Academic API with the query: {self.expr}")
        records = list(self.yield_records())
        self.json_data = records
        self.table_data = (
            pd.DataFrame(records)
            .drop(["prob", "logprob"], axis=1)
            .rename(columns=MAG.ENTITIES)
        )
        logger.info(f"Downloaded {self.table_data.shape[0]} entries in total.")

    def save(self, tocsv=None, tojson=None):
        """Write fetched data to files."""
        if tocsv is not None and self.table_data is not None:
            self.table_data.to_csv(tocsv, index=False)
        if tojson is not None and self.json_data is not None:
            with open(tojson, "w", encoding="utf-8") as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)

    def fetch(self, url, params):
        """Make a remote call to Microsoft Academic API."""
        return requests.get(url, params).json()

    def restore_abstract(self, abstract):
        """Restore inverted abstract to its original form."""
        words = abstract["InvertedIndex"]
        total_words = abstract["IndexLength"]

        text = []
        for position in range(0, total_words):
            for word, positions in words.items():
                if position in positions:
                    text.append(word)
        return " ".join(text)

    def process(self, entities):
        """Process entities: restore inverted abstracts to their raw form."""
        for entity in entities:
            entity["RA"] = self.restore_abstract(entity["IA"])
            yield entity

    def yield_records(self):
        """Fetch all entities for a given query expression."""
        params = {
            "expr": self.expr,
            "offset": self.offset,
            "count": self.count,
            "attributes": self.attr,
            "model": self.model,
            "subscription-key": self.key,
        }
        downloaded = 0
        while True:
            data = self.fetch(MAG.ENDPOINT, params)
            if data["entities"] == []:
                break
            yield from self.process(data["entities"])
            params["offset"] += self.count
            downloaded += len(data["entities"])
            logger.info(f"fetched {downloaded} entries.")
            sleep(3.1)
