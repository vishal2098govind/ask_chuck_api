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
        conversation_id: str,
        user_id: str,
        firestore_client: Optional[Client] = None,
    ):
        """
        Initialize a new instance of the FirestoreChatMessageHistory class.

        :param collection_name: The name of the collection to use.
        :param session_id: The session ID for the chat..
        :param user_id: The user ID for the chat.
        """
        self.sessions_collection_name = "ask_chuck_sessions"
        self.conversations_collection_name = "conversations"
        self.session_id = session_id
        self.conversation_id = conversation_id
        self.user_id = user_id
        self._session_document: Optional[DocumentReference] = None
        self._conversations_collection: Optional[CollectionReference] = None
        self.messages: List[BaseMessage] = []
        self.firestore_client = firestore_client or _get_firestore_client()
        self.prepare_firestore()

    def prepare_firestore(self) -> None:
        """Prepare the Firestore client.

        Use this function to make sure your database is ready.
        """
        self._session_document = self.firestore_client.collection(
            self.sessions_collection_name
        ).document(self.session_id)

        self._conversations_collection = self._session_document.collection(
            self.conversations_collection_name
        )
        self.load_messages()

    async def aget_messages(self) -> List[BaseMessage]:
        self.load_messages()
        print("loaded messages")
        return self.messages

    def load_messages(self) -> None:
        """Retrieve the messages from Firestore"""
        if not self._session_document:
            raise ValueError("Session document not initialized")
        if not self._conversations_collection:
            raise ValueError("Conversations collection not initialized")

        history: List[DocumentSnapshot] = self._conversations_collection.get()
        history.sort(key=lambda x: x.get('updated_at'))

        history_messages = []
        for h in history:
            human_message = h.get("human_message")
            history_messages.append(human_message)

            ai_message = h.get("ai_message")
            history_messages.append(ai_message)

        if len(history) > 0:
            self.messages = messages_from_dict(history_messages)

    def add_message(self, message: BaseMessage) -> None:
        self.upsert_messages(message)

    def upsert_messages(self, new_message: Optional[BaseMessage] = None) -> None:
        """Update the Firestore document."""
        if not self._session_document:
            raise ValueError("Document not initialized")

        doc = self._conversations_collection.document(
            self.conversation_id).get()

        session_doc = {
            "id": self.session_id,
            "user_id": self.user_id,
        }

        session_doc_snap = self._session_document.get()
        if not session_doc_snap.exists:
            session_doc["created_at"] = datetime.now()
            session_doc["session_name"] = new_message.content

        self._session_document.set(session_doc, merge=True)
        print("message content:", new_message.content)
        print("message:", new_message)

        conv_doc = {
            "{type}_message".format(type=new_message.type): message_to_dict(new_message),
            "updated_at": datetime.now(),
        }

        if not doc.exists:
            conv_doc["created_at"] = datetime.now()

        self._conversations_collection.document(self.conversation_id).set(
            document_data=conv_doc,
            merge=True
        )

    def add_context(self, context):
        self._conversations_collection.document(self.conversation_id).set(
            document_data={"context": context},
            merge=True
        )

    def clear(self) -> None:
        """Clear session memory from this memory and Firestore."""
        self.messages = []
        if self._session_document:
            self._session_document.delete()
