
from ask_chuck_api.rag.rag_chain import get_rag_chain
from langchain_core.messages import HumanMessage, SystemMessage

chat_history = []  # Collect chat history here (a sequence of messages)


async def handle_conversation(query: str):
    rag_chain = await get_rag_chain()
    while True:
        # Process the user's query through the retrieval chain
        result = rag_chain.invoke(
            {"input": query, "chat_history": chat_history})
        # Display the AI's response
        print(f"AI: {result['answer']}")
        # Update the chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(SystemMessage(content=result["answer"]))
