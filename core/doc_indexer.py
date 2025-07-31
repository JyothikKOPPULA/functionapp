import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType
)
from azure.search.documents import SearchClient

SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_SERVICE_KEY = os.getenv("SEARCH_SERVICE_KEY")
SEARCH_INDEX_NAME = "documents-index"

def chunk_text(text, max_tokens=500):
    sentences = text.split('. ')
    chunks, chunk = [], ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_tokens:
            chunk += sentence + '. '
        else:
            chunks.append(chunk.strip())
            chunk = sentence + '. '
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def create_or_update_index():
    search_credential = AzureKeyCredential(SEARCH_SERVICE_KEY)
    index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=search_credential)
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="customer_id", type=SearchFieldDataType.String, filterable=True, searchable=True),
        SearchField(name="filename", type=SearchFieldDataType.String, filterable=True, searchable=True)
    ]
    index = SearchIndex(name=SEARCH_INDEX_NAME, fields=fields)
    try:
        index_client.get_index(SEARCH_INDEX_NAME)
    except Exception:
        index_client.create_index(index)

def upload_chunks_to_index(chunks, customer_id, filename):
    search_credential = AzureKeyCredential(SEARCH_SERVICE_KEY)
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=SEARCH_INDEX_NAME, credential=search_credential)
    documents = []
    for i, chunk in enumerate(chunks):
        doc = {
            "id": f"{customer_id}_{filename}_{i}",
            "content": chunk,
            "customer_id": customer_id,
            "filename": filename
        }
        documents.append(doc)
    search_client.upload_documents(documents)

def process_and_index_blob(blob_bytes, customer_id, filename):
    text = blob_bytes.decode("utf-8")  # For binary files, use extraction logic
    create_or_update_index()
    chunks = chunk_text(text)
    upload_chunks_to_index(chunks, customer_id, filename)