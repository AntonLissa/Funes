from pymongo import MongoClient
from datetime import datetime
import uuid


class ChatStorage:

    def __init__(self, uri="mongodb://localhost:27017", db="llm_chats"):

        self.client = MongoClient(uri)
        self.db = self.client[db]

        self.chats = self.db.chats
        self.messages = self.db.messages
        self.ensure_indexes()
        
        
    def ensure_indexes(self):

        self.messages.create_index("chat_id")
        self.messages.create_index([("chat_id", 1), ("created_at", 1)])
        self.chats.create_index("user_id")


    def create_chat(self, chat_id, user_id, agent):

        chat = {
            "_id": chat_id,
            "user_id": user_id,
            "agent": agent,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "token_count": 0
        }

        self.chats.insert_one(chat)

    def save_message_user(self, chat_id, user_id, content):
        return self.save_message(
            chat_id=chat_id,
            user_id=user_id,
            role="user",
            content=content
        )

    def save_message_assistant(self, chat_id, user_id, content):
        return self.save_message(
            chat_id=chat_id,
            user_id=user_id,
            role="assistant",
            content=content
        )

    def save_message(
        self,
        chat_id,
        user_id,
        role,
        content,
        model=None,
        tokens_prompt=0,
        tokens_completion=0,
        latency_ms=None,
        metadata=None
    ):

        message = {
            "_id": str(uuid.uuid4()),
            "chat_id": chat_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "model": model,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "latency_ms": latency_ms,
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }

        self.messages.insert_one(message)

        self.chats.update_one(
            {"_id": chat_id},
            {
                "$inc": {
                    "message_count": 1,
                    "token_count": tokens_prompt + tokens_completion
                },
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "last_model": model
                }
            }
        )

        return message["_id"]

    def get_messages(self, chat_id, limit=100):

        cursor = (
            self.messages
            .find({"chat_id": chat_id})
            .sort("created_at", 1)
            .limit(limit)
        )

        return list(cursor)

    def list_user_chats(self, user_id):

        cursor = (
            self.chats
            .find({"user_id": user_id})
            .sort("updated_at", -1)
            .limit(100)
        )

        return list(cursor)
