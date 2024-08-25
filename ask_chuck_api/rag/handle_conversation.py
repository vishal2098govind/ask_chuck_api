
from ask_chuck_api.rag.rag_chain import get_rag_chain


async def handle_conversation(query: str, session_id: str):
    rag_chain = get_rag_chain()

    result = rag_chain.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )

    print('Context: ')
    print(result['context'])
    return result
