from typing import TypedDict, List

class State(TypedDict):
    # default field
    upload_file: str
    # save file fields
    file_path: str
    original_filename: str
    file_save_status: str
    # extraction fields
    doc_text: str
    extraction_method: str
    extraction_status: str
    # chunking fields
    doc_chunks: List[str]
    chunking_status: str
    # embedding fields
    doc_embeddings: List[List[float]]
    embedding_status: str
    # analysis fields
    storage_status: str
    # category prediction fields
    predicted_category: str
    category_prediction_status: str