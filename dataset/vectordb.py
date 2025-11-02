from pymilvus import MilvusClient, DataType
import pandas as pd

# Read data
df = pd.read_parquet("dataset/data/embed.parquet")

# Instantiate a local milvus client
client = MilvusClient("dataset/data/milvus.db")

# Drop existing collection, if it exists
if client.has_collection(collection_name="reckonsys"):
    client.drop_collection(collection_name="reckonsys")

# Dataset schema
print("Creating Schema")
schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)

# Add the fields to the schema
schema.add_field(
    field_name="id", datatype=DataType.VARCHAR, max_length=64, is_primary=True
)
schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
schema.add_field(field_name="page_content", datatype=DataType.VARCHAR, max_length=3072)
schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=64)

# Create a new collection
print("Creating Collection")
client.create_collection(collection_name="reckonsys", schema=schema)

# Create index
# Set up the index parameters
print("Creating Index")
index_params = MilvusClient.prepare_index_params()

index_params.add_index(
    field_name="vector",
    metric_type="COSINE",
    index_type="IVF_FLAT",
    index_name="reckonsys",
    params={"nlist": 128},
)

# Create an index file
client.create_index(
    collection_name="reckonsys",
    index_params=index_params,
    sync=True,  # Wait for index creation to complete before returning.
)

# Load the collection
print(f"Loading Collection")

client.load_collection(
    collection_name="reckonsys",
    replica_number=1,  # Number of replicas to create on query nodes.
)

# Create a list of dictionaries
data = df.to_dict('records')

# Insert data
res = client.insert(collection_name="reckonsys", data=data)

# Show results
print(f"Inserted {res['insert_count']} records")
