from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_alloydb_pg import AlloyDBVectorStore

from ask_chuck_api.rag.constants import TABLE_NAME
from ask_chuck_api.rag.serving_system import get_vector_store, model


async def handle_query(query: str):

    store = await get_vector_store()

    relevant_docs = await store.asimilarity_search(
        query=query
    )

    citations = []

    print(f"\n--- Relevant Documents for ---")
    for i, doc in enumerate(relevant_docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")
        if doc.metadata:
            citations.append({
                "source": doc.metadata.get('source', 'Unknown')
            })
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

    return {
        "response": result.content,
        "citations": citations,
    }
