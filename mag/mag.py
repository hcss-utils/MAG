# -*- coding: utf-8 -*-
import json
from time import sleep

import pandas as pd
import requests

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
        "AuId": "author_id",
        "DAuN": "author_name",
        "Y": "year_published",
        "D": "isodate_published",
        "DOI": "DOI",
        "J": "journals",
        "JN": "journal_name",
        "PB": "publisher",
        "FId": "field_of_study_id",
        "FN": "field_of_study",
    }

    def __init__(
        self,
        expr: str,
        key: str,
        count: int = 1_000,
        offset: int = 0,
        model: str = "latest",
        attr: str = "DN,Ti,W,AW,IA,AA.AuId,AA.DAuN,Y,D,DOI,J.JN,PB,F.FId,F.FN",
    ):
        self.params = {
            "expr": expr,
            "offset": offset,
            "count": count,
            "attributes": attr,
            "model": model,
            "subscription-key": key,
        }
        self.json_data = None
        self.json_foses = None
        self.table_data = None

    def download_publications(self):
        """Download entities."""
        logger.info(
            f"Calling Microsoft Academic API with the query: {self.params['expr']}"
        )
        records = list(self.yield_records())
        self.json_data = [item["raw"] for item in records]
        self.table_data = (
            pd.DataFrame([item["processed"] for item in records])
            .drop(["prob", "logprob"], axis=1)
            .rename(columns=MAG.ENTITIES)
        )
        logger.info(f"Downloaded {self.table_data.shape[0]} entries in total.")

    def fetch_foses(self, attr="Id,ECC,FL,FN,FC.FId,FC.FN,FP.FId,FP.FN", count=1):
        """Download fields of study attributes."""
        if self.json_data is None:
            raise ValueError("run .download_publications first.")
        if self.json_foses is not None:
            raise ValueError("fields of studies has already been fetched.")
        unique_foses = {f["FId"] for entity in self.json_data for f in entity["F"]}
        logger.info(f"identified {len(unique_foses)} unique fields of study...")

        foses = []
        params = self.params.copy()
        params.update(attributes=attr)
        params.update(count=count)
        for idx, fid in enumerate(unique_foses):
            params.update(expr=f"And(Id={fid}, Ty='6')")
            data = self.fetch(MAG.ENDPOINT, params)
            try:
                foses.append(data["entities"][0])
            except TypeError:
                logger.exception(idx)
            if idx % 100 == 0:
                logger.info(f"fetched {idx} foses.")
        self.json_foses = foses
        logger.info(f"fetched {len(self.json_foses)} foses.")
        return foses

    def save(self, tocsv=None, tojson=None):
        """Write fetched data to files."""
        if tocsv is not None and self.table_data is not None:
            self.table_data.to_csv(tocsv, index=False)
        if tojson is not None and self.json_data is not None:
            with open(tojson, "w", encoding="utf-8") as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
        if tojson is not None and self.json_foses is not None:
            with open(
                tojson.rstrip(".json") + "_foses.json", "w", encoding="utf-8"
            ) as f:
                json.dump(self.json_foses, f, ensure_ascii=False, indent=4)

    @staticmethod
    def fetch(url, params):
        """Make a remote call to Microsoft Academic API."""
        return requests.get(url, params).json()

    @staticmethod
    def restore_abstract(abstract):
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
        """Process entities, including unnesting JSON and restoring
        inverted abstracts to their raw form."""
        for item in entities:
            entity = item.copy()
            if "IA" in entity.keys():
                entity["RA"] = self.restore_abstract(entity["IA"])
                del entity["IA"]
            if "AA" in entity.keys():
                entity["DAuN"] = ";".join(item["DAuN"] for item in entity["AA"])
                entity["AuId"] = ";".join(str(item["AuId"]) for item in entity["AA"])
                del entity["AA"]
            if "F" in entity.keys():
                entity["FN"] = ";".join(item["FN"] for item in entity["F"])
                del entity["F"]
            if "J" in entity.keys():
                if isinstance(entity["J"], dict):
                    entity["JN"] = entity["J"]["JN"]
                elif isinstance(entity["J"], list):
                    entity["JN"] = ";".join(item["JN"] for item in entity["J"])
                else:
                    entity["JN"] = entity["J"]
                del entity["J"]
            yield {"raw": item, "processed": entity}

    def yield_records(self):
        """Fetch all entities for a given query expression."""
        params = self.params.copy()
        downloaded = 0
        while True:
            data = self.fetch(MAG.ENDPOINT, params)
            if data["entities"] == []:
                break
            yield from self.process(data["entities"])
            params["offset"] += params["count"]
            downloaded += len(data["entities"])
            logger.info(f"fetched {downloaded} entries.")
            sleep(3.1)
