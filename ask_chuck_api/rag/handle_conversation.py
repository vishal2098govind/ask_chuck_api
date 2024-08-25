
from ask_chuck_api.rag.rag_chain import get_rag_chain


async def handle_conversation(query: str):
    rag_chain = get_rag_chain()

    rag_chain.invoke(
        {"input": query},
        config={
            "configurable": {
                "session_id": "new_session_1_@_123griwg31145"
            },
        }
    )
