import os
from glob import glob
from uuid import uuid4

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datasets import Dataset

# Gather all the text files
folder = "dataset/data/scraped"
txt_files = glob(f"{folder}/*.txt")

# File name of the text dataset
dataset_file_name = "dataset/data/dataset.parquet"

# Empty list to hold Langchain Documents
documents = []

# Iterate over files
for txt_file in txt_files:
    # Extract filename
    file_name = os.path.basename(txt_file)

    # Read
    with open(txt_file, "r") as file:
        text = file.read()

    # Add instance of Document to list
    documents.append(Document(metadata={"source": file_name}, page_content=text))


# Instantiate the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)

# Split all the documents
all_splits = text_splitter.split_documents(documents)

# Create a list of dictionaries to read into dataset
data = [dict(split) for split in all_splits]

# Create a HF dataset
dataset = Dataset.from_list(data)

# Flatten the nested dicts
dataset = dataset.flatten()

# Add unique identifiers
dataset = dataset.map(
    lambda example: {"id": str(uuid4()), "source": example["metadata.source"]},
    remove_columns=["metadata.start_index", "type", "metadata.source"],
)

print(dataset[0])

# Save to file
dataset.to_parquet(dataset_file_name)
