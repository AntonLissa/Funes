import asyncio
from chat_storage import ChatStorage


async def main():

    storage = ChatStorage()

    user_id = "user_1"
    agent_id = 'test'

    print("\n--- CHAT DELL'UTENTE ---\n")

    chats = await storage.list_user_chats(user_id)

    if not chats:
        print("Nessuna chat trovata")

    for c in chats:
        print(
            f"id: {c['_id']} | "
            f"messages: {c.get('message_count',0)} | "
            f"updated: {c.get('updated_at')}"
        )

    print("\nCreazione nuova chat...\n")

    chat_id = await storage.create_chat(user_id, agent_id)

    print("Nuova chat:", chat_id)
    print("\nScrivi 'exit' per terminare\n")

    while True:

        user_msg = input("USER: ")

        if user_msg == "exit":
            break

        await storage.save_message(
            chat_id,
            user_id,
            "user",
            user_msg
        )

        llm_msg = input("LLM: ")

        if llm_msg == "exit":
            break

        await storage.save_message(
            chat_id,
            user_id,
            "assistant",
            llm_msg
        )

    print("\n--- MESSAGGI SALVATI ---\n")

    messages = await storage.get_messages(chat_id)

    for m in messages:
        print(f"{m['role']}: {m['content']}")


if __name__ == "__main__":
    asyncio.run(main())
