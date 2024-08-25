import logging
from datetime import datetime
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from google.cloud.firestore import Client, DocumentReference, CollectionReference, DocumentSnapshot
from langchain_core.messages import (
    BaseMessage,
    messages_from_dict,
    message_to_dict
)

logger = logging.getLogger(__name__)


def _get_firestore_client() -> Client:
    try:
        import firebase_admin
        from firebase_admin import firestore
    except ImportError:
        raise ImportError(
            "Could not import firebase-admin python package. "
            "Please install it with `pip install firebase-admin`."
        )

    # For multiple instances, only initialize the app once.
    try:
        firebase_admin.get_app()
    except ValueError as e:
        logger.debug("Initializing Firebase app: %s", e)
        firebase_admin.initialize_app()

    return firestore.client()


class RagChatMessageHistory(BaseChatMessageHistory):
    def __init__(
        self,
        session_id: str,
        user_id: str,
        firestore_client: Optional[Client] = None,
    ):
        """
        Initialize a new instance of the FirestoreChatMessageHistory class.

        :param collection_name: The name of the collection to use.
        :param session_id: The session ID for the chat..
        :param user_id: The user ID for the chat.
        """
        self.collection_name = "conversations"
        self.conversation_messages_collection_name = "messages"
        self.session_id = session_id
        self.user_id = user_id
        self._document: Optional[DocumentReference] = None
        self.conversation_messages: Optional[CollectionReference] = None
        self.messages: List[BaseMessage] = []
        self.firestore_client = firestore_client or _get_firestore_client()
        self.prepare_firestore()

    def prepare_firestore(self) -> None:
        """Prepare the Firestore client.

        Use this function to make sure your database is ready.
        """
        self._document = self.firestore_client.collection(
            self.collection_name
        ).document(self.session_id)
        self.conversation_messages = self._document.collection(
            self.conversation_messages_collection_name
        )
        self.load_messages()

    async def aget_messages(self) -> List[BaseMessage]:
        self.load_messages()
        print("loaded messages")
        return self.messages

    def load_messages(self) -> None:
        """Retrieve the messages from Firestore"""
        if not self._document:
            raise ValueError("Document not initialized")
        if not self.conversation_messages:
            raise ValueError("Messages collection not initialized")

        history: List[DocumentSnapshot] = self.conversation_messages.get()
        history.sort(key=lambda x: x.get('created_at'))

        if len(history) > 0:
            self.messages = messages_from_dict(
                [m.get('message') for m in history])

    def add_message(self, message: BaseMessage) -> None:
        self.upsert_messages(message)

    def upsert_messages(self, new_message: Optional[BaseMessage] = None) -> None:
        """Update the Firestore document."""
        if not self._document:
            raise ValueError("Document not initialized")

        self._document.set({
            "id": self.session_id,
            "user_id": self.user_id
        })
        print("message content:", new_message.content)

        self.conversation_messages.add(
            {
                "message": message_to_dict(new_message),
                "created_at": datetime.now(),
            }
        )

    def clear(self) -> None:
        """Clear session memory from this memory and Firestore."""
        self.messages = []
        if self._document:
            self._document.delete()
