import discord
import json
import random
import asyncio
import os

def get_user_input(existing_settings):
    settings = existing_settings.copy()

    if "tokens" not in settings:
        settings["tokens"] = input("Enter Discord tokens (separated by comma for multiple accounts): ").split(",")

    if "channel_ids" not in settings:
        channel_ids = input("Enter channel IDs (separated by comma for multiple channels): ").split(",")
        settings["channel_ids"] = [int(id) for id in channel_ids]

    if "cooldown" not in settings:
        settings["cooldown"] = int(input("Enter spam time: "))

    if "random_delay" not in settings:
        settings["random_delay"] = int(input("Enter max random delay time after cooldown: "))

    with open("settings.json", "w") as file:
        json.dump(settings, file)
    
    return settings


settings = {}
if os.path.exists("settings.json"):
    with open("settings.json", "r") as file:
        settings = json.load(file)

settings = get_user_input(settings)


with open("message.txt", "r") as file:
    message_content = file.read()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await self.send_messages_to_all_channels()

    async def send_messages_to_all_channels(self):
        while True:
            for channel_id in settings["channel_ids"]:
                channel = self.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(message_content)
                        random_delay = random.randint(1, settings["random_delay"])
                        await asyncio.sleep(settings["cooldown"] + random_delay)
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.response.headers.get('Retry-After')
                            if retry_after:
                                await asyncio.sleep(float(retry_after))
                                await channel.send(message_content)
                        else:
                            print(f"Error sending message: {e}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

async def run_client(token):
    client = MyClient()
    try:
        await client.start(token)
    except discord.LoginFailure:
        print(f"Login failed for token: {token}. Check if the token is valid.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    await asyncio.gather(*(run_client(token) for token in settings["tokens"]))

if __name__ == "__main__":
    asyncio.run(main())