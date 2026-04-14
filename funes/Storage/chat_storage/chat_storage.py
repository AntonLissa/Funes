from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid


class ChatStorage:

    def __init__(self, uri="mongodb://localhost:27017", db="llm_chats"):

        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db]

        self.chats = self.db.chats
        self.messages = self.db.messages

    async def create_chat(self, user_id, agent):

        chat_id = str(uuid.uuid4())

        chat = {
            "_id": chat_id,
            "user_id": user_id,
            "agent": agent,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0,
            "token_count": 0
        }

        await self.chats.insert_one(chat)

        return chat_id

    async def save_message(
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

        await self.messages.insert_one(message)

        await self.chats.update_one(
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

    async def get_messages(self, chat_id, limit=100):

        cursor = (
            self.messages
            .find({"chat_id": chat_id})
            .sort("created_at", 1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def list_user_chats(self, user_id):

        cursor = (
            self.chats
            .find({"user_id": user_id})
            .sort("updated_at", -1)
        )

        return await cursor.to_list(length=100)

