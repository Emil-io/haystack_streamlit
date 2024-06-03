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

            if os.path.exists(path):
                with open(path, 'r') as file:
                    meta_data = json.load(file)
                doc.meta.update(meta_data)

        return {"documents": documents}
