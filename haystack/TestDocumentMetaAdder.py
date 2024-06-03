import unittest
from unittest.mock import patch, mock_open, MagicMock
from haystack import Document
from DocumentMetaAdder import DocumentMetaAdder  # Adjust the import according to your module's name
import pandas as pd


class TestDocumentMetaAdder(unittest.TestCase):

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"author": "John Doe", "length": 10}')
    def test_run_with_existing_meta_file(self, mock_file, mock_exists):
        # Set up the mock to return True, as if the file exists
        mock_exists.return_value = True

        # Create a list of Document objects with meta information
        documents = [Document(content="Test content", meta={"file_path": "test_document"})]

        # Instantiate the DocumentMetaAdder component
        component = DocumentMetaAdder()

        # Run the component
        result = component.run(documents)

        # Verify the meta data was updated correctly
        expected_meta = {"file_path": "test_document", "author": "John Doe", "length": 10}
        self.assertEqual(result["documents"][0].meta, expected_meta)

    @patch('os.path.exists')
    def test_run_with_non_existing_meta_file(self, mock_exists):
        # Set up the mock to return False, as if the file does not exist
        mock_exists.return_value = False

        # Create a list of Document objects with meta information
        documents = [Document(content="Test content", meta={"file_path": "test_document"})]

        # Instantiate the DocumentMetaAdder component
        component = DocumentMetaAdder()

        # Run the component
        result = component.run(documents)

        # Verify the meta data remains unchanged
        expected_meta = {"file_path": "test_document"}
        self.assertEqual(result["documents"][0].meta, expected_meta)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"author": "John Doe", "length": 10}')
    def test_run_preserves_all_other_attributes(self, mock_file, mock_exists):
        # Set up the mock to return True, as if the file exists
        mock_exists.return_value = True

        # Create a mock dataframe
        mock_dataframe = pd.DataFrame({"column1": [1, 2], "column2": ["a", "b"]})

        # Create a list of Document objects with various attributes
        documents = [
            Document(
                id="123",
                content="Test content",
                meta={"file_path": "test_document", "existing_meta": "value"},
                score=0.85,
                embedding=[0.1, 0.2, 0.3],
                sparse_embedding=None
            )
        ]

        # Extract the original attributes for comparison later
        original_attributes = {
            attr: getattr(documents[0], attr)
            for attr in dir(documents[0])
            if not attr.startswith('__') and not callable(getattr(documents[0], attr))
        }

        # Instantiate the DocumentMetaAdder component
        component = DocumentMetaAdder()

        # Run the component
        result = component.run(documents)

        # Verify that only the meta attribute was updated
        for attr, original_value in original_attributes.items():
            if attr == 'meta':
                expected_meta = {"file_path": "test_document", "existing_meta": "value", "author": "John Doe",
                                 "length": 10}
                self.assertEqual(result["documents"][0].meta, expected_meta)
            else:
                self.assertEqual(getattr(result["documents"][0], attr), original_value)


if __name__ == '__main__':
    unittest.main()
