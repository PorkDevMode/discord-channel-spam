import discord
import json
import random
import asyncio
import os
import datetime
from colorama import init, Fore


def get_user_input(existing_settings):
    
    if not isinstance(existing_settings, dict):
        settings = {}
    else:
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

init(autoreset=True)

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
                        
                        with open("message.txt", "r") as file:
                            message_content = file.read()
                        
                        await channel.send(message_content)
                        now = datetime.datetime.now()
                        
                        print(f"{Fore.GREEN}[{now.strftime('%Y-%m-%d %H:%M:%S')}] {Fore.BLUE}Message sent to channel {channel_id}:\n{message_content}\n")
                        
                    except discord.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.response.headers.get('Retry-After')
                            if retry_after:
                                print(f"{Fore.RED}Cooldown! Retrying in: {retry_after}")
                                await asyncio.sleep(float(retry_after))
                                await channel.send(message_content)
                        else:
                            print(f"{Fore.RED}Error sending message: {e}")
                    except Exception as e:
                        print(f"{Fore.RED}An error occurred: {e}")

            
            random_delay = random.randint(1, settings["random_delay"])
            print(f"{Fore.LIGHTYELLOW_EX}Next message in: {settings['cooldown']} seconds")
            await asyncio.sleep(settings["cooldown"] + random_delay)

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
