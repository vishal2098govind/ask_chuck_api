from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore

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


async def get_vector_store():
    store = await AlloyDBVectorStore.create(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding,
    )
    print("store: ", store)
    return store


def get_retriever():
    db = AlloyDBVectorStore.create_sync(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding,
    )
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    print("db: ", db)
    print("retriever: ", retriever)
    return retriever
