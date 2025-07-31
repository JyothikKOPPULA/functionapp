import azure.functions as func
import logging
import json
from core.doc_indexer import process_and_index_blob

app = func.FunctionApp()

@app.blob_trigger(arg_name="blob", 
                  path="uploads/{customer_id}/{filename}",
                  connection="AzureWebJobsStorage")
def blob_upload_trigger(blob: func.InputStream, customer_id: str, filename: str):
    logging.info(f"Processing file: {filename} for customer: {customer_id}")
    process_and_index_blob(blob.read(), customer_id, filename)
    logging.info("Indexing completed.")
