import os
import json

from typing import List
from haystack import Document, component, logging


@component
class DocumentMetaAdder:
    """
    TODO: Description
    """

    def __init__(
        self
    ):
        """
        TODO: Description
        """
        pass

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        """
        TODO: Description
        """

        for doc in documents:
            path = doc.meta["file_path"] + ".meta.json"

            print("In the component loop")

            if os.path.exists(path):
                print("Path exists")
                with open(path, 'r') as file:
                    meta_data = json.load(file)
                    print("Json opened")
                    doc.meta.update(meta_data)

        return {"documents": documents}
