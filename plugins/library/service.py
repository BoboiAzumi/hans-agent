import os
from langchain_core.tools import tool
from pymilvus import MilvusClient, DataType, FunctionType, Function, AnnSearchRequest, WeightedRanker
from langchain_google_genai import GoogleGenerativeAIEmbeddings

EMBEDDING_DIM=768

embedding = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2",
    api_key=os.getenv("GOOGLE_API_KEY"),
    output_dimensionality=EMBEDDING_DIM
)

client = MilvusClient("./storage.db")

if not client.has_collection("hans"):
    schema = MilvusClient.create_schema(
        auto_id=True,
        enable_dynamic_field=True
    )

    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="dense", datatype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM)
    schema.add_field(field_name="sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=5000, enable_analyzer=True)

    bm25_function = Function(
        name="bm25",
        function_type=FunctionType.BM25,
        input_field_names=["text"],
        output_field_names=["sparse"]
    )

    schema.add_function(bm25_function)

    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="dense",
        index_type="AUTOINDEX",
        metric_type="COSINE"
    )

    index_params.add_index(
        field_name="sparse",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="BM25"
    )

    client.create_collection(
        "hans", 
        EMBEDDING_DIM, 
        schema=schema, 
        index_params=index_params,
    )

client.load_collection("hans")

def query_embed(query):
    return embedding.embed_query(query)

def document_embed(document):
    return embedding.embed_documents([document])[0]

def insert(document: str):
    embed = document_embed(document)

    data = [
        {
            "text": document,
            "dense": embed
        }
    ]

    client.insert(
        collection_name="hans",
        data=data
    )

def get(query: str):
    embed = query_embed(query)

    dense = AnnSearchRequest(
        data=[embed],
        anns_field="dense",
        param={
            "metric_type": "COSINE"
        },
        limit=20
    )

    sparse = AnnSearchRequest(
        data=[query],
        anns_field="sparse",
        param={
            "metric_type": "BM25"
        },
        limit=20
    )

    result = client.hybrid_search(
        collection_name="hans",
        reqs=[dense, sparse],
        ranker=WeightedRanker(0.6, 0.4),
        limit=5,
        output_fields=["text"]
    )

    return [
        {"id": hit["entity"]["id"], "text": hit["entity"]["text"]} 
        for hit in result[0]
    ]

def delete_data(ids: list[str]):
    client.delete(
        "hans",
        ids=ids
    )

@tool
def tool_call(mode: str, content: str | list[str]):
    '''
    Menyimpan atau mengambil informasi tertentu, tool ini berkaitan dengan ingatan jangka panjang.
    Gunakan untuk menyimpan informasi penting ataupun mengingat sesuatu.
    Untuk menghapus, lampirkan content adalah ID dari list datanya, pastikan kamu melakukan get data terlebih dahulu.

    Tambahkan di akhir response berupa kalimat (hanya jika save atau delete)
    "\n\n{Content} telah di **{mode}**"
    argumen:
        mode: "save", "load", "delete", save untuk menyimpan, load untuk mengambil informasi, delete untung menghapus
        content: informasi bertipe string, dipakai untuk input ataupun query pencarian, bisa pula berisi daftar id yang akan di delete
    '''
    if mode == "save":
        print(f"Catat =>\n{content}")
        return insert(content)
    if mode == "delete":
        print(f"Hapus => {content}")
        delete_data(content)
    else:
        return get(content)
    