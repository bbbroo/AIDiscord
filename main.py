import openai
import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

modelname = 'gpt-3.5'
gpt35names=["!gpt-3.5-turbo","!gpt-3.5","!GPT-3.5","!GPT-3.5-turbo", "!gpt3.5"]
gpt4names=["!gpt-4","!GPT-4", "!gpt4"]

with open("AIPersona.txt", 'r', encoding="utf8") as chat:
    persona = chat.read()

messages = [{'role': "system", 'content': persona}]

openai.api_key = os.getenv('OPENAI_API_KEY')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    await channel.send('Bot is ready! Type !help at any time for help.')

@bot.event
async def on_message(message):
    global modelname
    global messages
    global persona
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    if message.content[0] == "!":
        if message.content == "!help":
            await message.channel.send("""```
To change the model to GPT-3.5, type: !gpt-3.5-turbo
To change the model to GPT-4, type: !gpt-4
To clear the message context, type: !clear
To update the AI's persona, type: '!persona' followed by the new persona's description (e.g. '!persona This is the new persona')
To reset the AI's persona, type: !resetpersona```""")
            return
        if message.content == "!clear":
            messages = [{'role': "system", 'content': persona}]
        if any(message.content == c for c in gpt4names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-4"
            await message.channel.send("Updated model to: " + modelname)
            return
        if any(message.content == c for c in gpt35names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-3.5-turbo"
            await message.channel.send("Updated model to: " + modelname)
            return
        if message.content.startswith('!persona'):
            updated_persona = message.content.split('!persona')[1]
            messages = [{'role': "system", 'content': updated_persona}]
            await message.channel.send("Updated persona to: " + updated_persona)
            return
        if message.content.startswith('!resetpersona'):
            messages = [{'role': "system", 'content': persona}]
            await message.channel.send("Persona has been reset!")
            return
    f = open("logs.txt", "a+")
    f.write(str(datetime.datetime.now()) + " - User: " + message.content + "\n")
    f.close()
    messages.append({'role': "user", 'content': message.content})
    try:
        async with message.channel.typing(): 
            response = openai.ChatCompletion.create(
        model=modelname,
        messages=messages
        )
        output = response['choices'][0]['message']['content']
        messages.append({'role': "assistant", 'content': output})
        f = open("Logs.txt", "a")
        f.write(str(datetime.datetime.now()) + " - Assistant: " + output + "\n")
        f.close()
        output_length = len(output)
        num_of_outputs = (output_length // 1900) + 1
        #await message.channel.send(modelname+ ": " +output[:1900])
        for i in range(0,num_of_outputs):
            await message.channel.send(modelname+ ": " +output[(1900*(i)):(1900*(i+1))])
        
    except Exception as e:
        print(e)
        await message.channel.send("Something went wrong, try asking again.")
        return
    
bot.run(os.getenv('DISCORD_BOT_TOKEN'))