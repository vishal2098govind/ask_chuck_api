import os
import time
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from ask_chuck_api.rag.constants import *

engine = AlloyDBEngine.from_instance(
    project_id=PROJECT_ID,
    region=REGION,
    cluster=CLUSTER,
    instance=INSTANCE,
    database=DATABASE,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
)

embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=PROJECT_ID,
)

model = ChatVertexAI(
    model="gemini-1.5-flash-001",
    temperature=0,
    max_tokens=None,
    max_retries=6,
    stop=None,
)


def get_alloydb_vector_store():
    store = AlloyDBVectorStore.create_sync(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding,
    )
    print("store: ", store)
    return store


def get_pincone_vector_store():
    if not os.getenv("PINECONE_API_KEY"):
        os.environ["PINECONE_API_KEY"] = "405d48bc-0764-4a04-a2a5-32b59635e09e"

    pinecone_api_key = os.environ.get("PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "langchain-ask-chuck-pinecone-index"

    index = pc.Index(index_name)

    store = PineconeVectorStore(
        index=index,
        embedding=embedding,
    )
    print("store: ", store)
    return store


def get_retriever():
    db = get_pincone_vector_store()
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3, },
    )
    print("db: ", db)
    print("retriever: ", retriever)
    return retriever
