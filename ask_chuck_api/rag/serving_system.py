from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore

from ask_chuck_api.rag.constants import *
# import os

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "askchuck-0c12865e76ea.json"


# print("creds: ", credentails_path)

engine = AlloyDBEngine.from_instance(
    project_id=PROJECT_ID,
    region=REGION,
    cluster=CLUSTER,
    instance=INSTANCE,
    database=DATABASE,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    iam_account_email="vishal@askchuck.iam.gserviceaccount.com"
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


async def handle_query(query: str) -> str:

    store = await AlloyDBVectorStore.create(
        engine=engine,
        table_name=TABLE_NAME,
        embedding_service=embedding,
    )

    relevant_docs = await store.asimilarity_search(
        query=query
    )

    print(f"\n--- Relevant Documents for ---")
    for i, doc in enumerate(relevant_docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")
        if doc.metadata:
            print(f"Source: {doc.metadata.get('source', 'Unknown')}\n")

    combined_input = (
        "Here are some documents that might help answer the question: "
        + query
        + "\n\nRelevant Documents:\n"
        + "\n\n".join([doc.page_content for doc in relevant_docs])
        + "\n\nPlease provide an answer based only on the provided documents. If the answer is not found in the documents, respond with 'I'm not sure'."
    )

    # Define the messages for the model
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=combined_input),
    ]

    # Invoke the model with the combined input
    result = await model.ainvoke(messages)

    # Display the full result and content only
    print("\n--- Generated Response ---")
    print("Full result:")
    print(result)
    print("Content only:")
    print(result.content)
    print("citations:")
    return result.content
