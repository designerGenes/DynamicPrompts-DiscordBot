import discord
import random
import os
import asyncio
import argparse

intents = discord.Intents.default()
intents.message_content = True
token = "MTE1MDgwMjk1Njc1MzU3NjEyOA.GuEfNl.x_g0Y2JH3bXYUpYqXTmuxn-tQlUnTCrbCeW7D4"
async def read_file(filename):
    try:
        with open(os.path.join('wildcards', f'{filename}.txt'), 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        try:
            with open(os.path.join('wildcards', filename), 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return None
    
    return [line.strip() for line in lines]

async def replace_wildcards(text):
    start = text.find('[')
    end = text.find(']')
    
    while start != -1 and end != -1:
        wildcard = text[start+1:end]
        file_content = await read_file(wildcard)
        
        if file_content:
            replacement = random.choice(file_content)
            text = text[:start] + replacement + text[end+1:]
        
        start = text.find('[', end)
        end = text.find(']', start)
    
    return text

async def list_wildcard_values(wildcard):
    file_content = await read_file(wildcard)
    if file_content:
        return "\n".join(file_content)
    else:
        return "No wildcards found."

async def test_bot():
    test_strings = [
        "A photograph of [actress].",
        "Summer day, awards ceremony outdoors [actress] accepting Oscar statue.",
        "In the movie, [actor] worked with [actress]."
    ]
    
    for test_str in test_strings:
        result = await replace_wildcards(test_str)
        print(f"Original: {test_str}\nUpdated: {result}\n")

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!wildcard '):
            args = message.content.split(" ")
            
            # Check for the -l flag
            if '-l' in args:
                index = args.index('-l')
                try:
                    wildcard_to_list = args[index + 1][1:-1]  # remove square brackets
                    list_values = await list_wildcard_values(wildcard_to_list)

                    # Break list_values into chunks of 2000 characters each
                    for i in range(0, len(list_values), 2000):
                        await message.channel.send(list_values[i:i+2000])

                    return
                except IndexError:
                    await message.channel.send("Please specify a wildcard after the -l flag.")
                    return
                
            formatted_string = message.content[10:]
            new_string = await replace_wildcards(formatted_string)
            await message.channel.send(new_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the DynamicPrompts bot")
    parser.add_argument("--test", help="Run tests instead of the bot", action="store_true")

    args = parser.parse_args()

    if args.test:
        asyncio.run(test_bot())
    else:
        client = MyClient(intents=intents)
        client.run(token)
