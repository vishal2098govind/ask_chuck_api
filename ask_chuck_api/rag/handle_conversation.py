from uuid import uuid4
from langchain_core.output_parsers import JsonOutputParser
from ask_chuck_api.rag.rag_chain import get_rag_chain
from google.cloud.firestore import Client
from langchain_core.documents import (Document)

from ask_chuck_api.rag.rag_chat_history import RagChatMessageHistory


async def handle_conversation(query: str, session_id: str, user_id: str):

    conversation_id = str(uuid4())

    rag_chat_history = RagChatMessageHistory(
        conversation_id=conversation_id,
        firestore_client=Client(project="askchuck"),
        session_id=session_id,
        user_id=user_id,
    )

    rag_chain = get_rag_chain(rag_chat_history)

    result = rag_chain.invoke(
        {"input": query},
        config={"configurable": {"session_id": session_id}}
    )

    context = []
    for c in result['context']:
        if isinstance(c, Document):
            context.append(c.dict())

    print('Context: ')
    # print(result['context'])
    print(context)

    rag_chat_history.add_context(context)

    return result
