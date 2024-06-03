import os
from dotenv import load_dotenv
import tagme
import requests
from tagme import Annotation


class TagmeManager:
    def __init__(self, rho):
        load_dotenv()
        self.api_key = os.getenv("TAGME_API_KEY")
        tagme.GCUBE_TOKEN = self.api_key
        self.rho = rho

    def tag_text(self, txt: str) -> list[Annotation]:
        try:
            return tagme.annotate(txt).get_annotations(self.rho)
        except Exception as e:
            print(f"Error tagging text, skipping")
            return []

    @staticmethod
    def get_annotation_info(annotation):
        curid = annotation.entity_id
        params = {
            "action": "query",
            "prop": "pageprops",
            "pageids": curid,
            "format": "json",
        }
        wikipedia_api_url = "https://en.wikipedia.org/w/api.php"

        response = requests.get(wikipedia_api_url, params=params)
        data = response.json()
        try:
            wikidata_item_id = data["query"]["pages"][str(curid)]["pageprops"][
                "wikibase_item"
            ]
            return wikidata_item_id
        except KeyError as e:
            print(f"Error {e} fetching Wikidata URL from cur-id {curid}.")
            return None
