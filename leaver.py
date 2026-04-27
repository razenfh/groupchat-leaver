import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest
from tqdm import tqdm

# Paste your API credentials here from https://my.telegram.org
api_id = #
api_hash = "#"

client = TelegramClient("session", api_id, api_hash)

target_user = input("Enter username or ID: ").replace("@", "").strip()


async def get_groups():
    groups = []

    async for dialog in client.iter_dialogs():
        # Skip channels that are not groups
        if dialog.is_channel and not dialog.is_group:
            continue

        if dialog.is_group:
            groups.append(dialog)

    return groups


async def find_chats(groups, user):
    matched = []

    print("\n🔍 Searching through messages...\n")

    for group in tqdm(groups, desc="Searching", unit="chat"):
        try:
            found = False
            # Check last 50 messages for specific user activity
            async for message in client.iter_messages(group, from_user=user, limit=50):
                if message:
                    found = True
                    break

            if found:
                print(f"\n[+] Found user in: {group.name}")
                matched.append(group)

        except Exception:
            pass

    return matched


def choose_chats(chats):
    print("\n📋 Found Chats:\n")

    for i, chat in enumerate(chats, 1):
        print(f"{i}. {chat.name}")

    print("\n1 - Leave all found chats")
    print("2 - Choose manually")

    choice = input("\n👉 Choice: ").strip()

    if choice == "1":
        return chats

    elif choice == "2":
        raw = input("Enter numbers separated by commas: ")
        selected = []
        for x in raw.split(","):
            x = x.strip()
            if x.isdigit():
                idx = int(x) - 1
                if 0 <= idx < len(chats):
                    selected.append(chats[idx])
        return selected

    return []


async def leave_chats(chats):
    print("\n🚪 Leaving groups...\n")

    me = await client.get_me()

    for chat in tqdm(chats, desc="Leaving", unit="chat"):
        try:
            print(f"➡️ Leaving: {chat.name}")

            # =========================
            # SUPERGROUPS / MEGAGROUPS
            # =========================
            if chat.is_channel:
                await client(LeaveChannelRequest(chat.entity))

            # =========================
            # BASIC GROUPS
            # =========================
            else:
                await client(DeleteChatUserRequest(
                    chat_id=chat.id,
                    user_id=me.id
                ))

        except Exception:
            # Fallback method
            try:
                await client.delete_dialog(chat)
            except Exception as e:
                print(f"❌ Error leaving {chat.name}: {e}")


async def main():
    await client.start()

    user = await client.get_entity(target_user)
    groups = await get_groups()
    chats = await find_chats(groups, user)

    print("\n========== RESULTS ==========")

    if not chats:
        print("No matches found.")
        return

    selected = choose_chats(chats)

    if not selected:
        print("Cancelled.")
        return

    await client.get_dialogs() # Refresh cache
    await leave_chats(selected)

    print("\n✅ Done.")


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())