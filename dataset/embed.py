import pandas as pd
from sentence_transformers import SentenceTransformer
import torch

# Read dataset
df = pd.read_parquet("dataset/data/dataset.parquet")

# Model to use for embedding
model_name = "mixedbread-ai/mxbai-embed-large-v1"

# Instantiate the model to gpu, if possible
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(model_name, device=device)

# Batch encode the page content
df["vector"] = model.encode(
    df["page_content"].tolist(),
    batch_size=120,
    show_progress_bar=True,
    convert_to_numpy=True,
    precision="float32",
).tolist()

# Save to file
df.to_parquet("dataset/data/embed.parquet", index=False)
