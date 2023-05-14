import openai

import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

#Recognize env variables
load_dotenv()

#Initial AI Model, can change to "gpt-4" if access is enabled 
modelname = 'gpt-3.5-turbo'
#List of acceptable inputs for changing AI model to GPT-3.5
gpt35names=["!gpt-3.5-turbo", "!gpt-3.5", "!gpt3.5", "!gpt3", "!gpt35", "!gpt-35"]
#List of acceptable inputs for changing AI model to GPT-4
gpt4names=["!gpt-4", "!gpt4"]

#Read the "AIPersona.txt" file to set the AI's persona
with open("AIPersona.txt", 'r', encoding="utf8") as chat:
    persona = chat.read()

#Initiaing the AI's context array, and setting the AI's persona
messages = [{'role': "system", 'content': persona}]

#Retrieving the OpenAI API key from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')

#Setting intents for Discord bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Function that runs once bot is ready
@bot.event
async def on_ready():
    #Output to console that bot is connected to Discord
    print(f'{bot.user} has connected to Discord!')
    #Set Discord channel to interact with OpenAI
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    #Output to Discord channel that bot is ready
    await channel.send('Bot is ready! Type !help at any time for help.')

#Function that runs when message is sent in Discord channel
@bot.event
async def on_message(message):
    #Making variables within function global
    global modelname
    global messages
    global persona
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    #Check if command is used
    if message.content[0] == "!":
        #Check if user wants the !help command and sends help message
        if message.content == "!help":
            await message.channel.send("""```
To show current AI model, type: !model
To change the model to GPT-3.5, type: !gpt-3.5-turbo
To change the model to GPT-4, type: !gpt-4
To clear the message context, type: !clear
To update the AI's persona, type: '!persona' followed by the new persona's description (e.g. '!persona This is the new persona')
To reset the AI's persona, type: !resetpersona```""")
            return
        #Command to clear the message context with the AI
        if message.content.lower().strip() == "!clear":
            messages = [{'role': "system", 'content': persona}]
            return
        #Command to change model to GPT-4
        if any(message.content.lower().strip() == c for c in gpt4names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-4"
            await message.channel.send("Updated model to: " + modelname)
            return
        #Command to change model to GPT-3.5-turbo
        if any(message.content.lower().strip() == c for c in gpt35names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-3.5-turbo"
            await message.channel.send("Updated model to: " + modelname)
            return
        #Command to update persona
        if message.content.startswith('!persona'):
            updated_persona = message.content.split('!persona')[1]
            messages.append({'role': "system", 'content': updated_persona})
            await message.channel.send("Updated persona to: " + updated_persona)
            return
        #Command to reset persona
        if message.content.startswith('!resetpersona'):
            messages.append({'role': "system", 'content': persona})
            await message.channel.send("Persona has been reset!")
            return
        #Command to see current AI model
        if message.content.startswith('!model'):
            await message.channel.send("The current AI model is: " + modelname)
            return
        
    #Writing users message to the AI to 'logs.txt' file
    f = open("logs.txt", "a+")
    f.write(str(datetime.datetime.now()) + " - User: " + message.content + "\n")
    f.close()

    #Adding users message to the 'messages' variable/adding it to the AI's context
    messages.append({'role': "user", 'content': message.content})

    #Attempt to get a response from the OpenAI API, exception cases will run if error occurs
    try:
        #Show bot as typing on Discord while waiting for API respponse
        async with message.channel.typing(): 
            #Giving API input of model and message context
            response = openai.ChatCompletion.create(
        model=modelname,
        messages=messages
        )
        #Get response text from API
        output = response['choices'][0]['message']['content']
        #Adding AI's response to the 'messages' variable/adding it to the AI's context
        messages.append({'role': "assistant", 'content': output})

        #Writing AI's response to the 'logs.txt' file
        f = open("Logs.txt", "a")
        f.write(str(datetime.datetime.now()) + " - Assistant: " + output + "\n")
        f.close()

        #Discord only allows 2000 characters to be output, so splitting the text up may be necessary 
        output_length = len(output)
        num_of_outputs = (output_length // 1900) + 1
        #Loop to split up response every 1900 characters
        for i in range(0,num_of_outputs):
            #Output "Continued" to Discord if text is being continued from previous output
            if i >= 1:
                await message.channel.send("(Continued)")
            #Outputting the i'th iteration of 1900 characters (If more than 1900 characters are present, on first run it'll print out the first 1900 chars, then on the next run it'll print the next 1900 chars, and so on)
            await message.channel.send(output[(1900*(i)):(1900*(i+1))])
        
    #Handle errors recieved during attempt to get response from OpenAI's API
    except Exception as e:
        #Output error to console
        print(e)
        #Output error to Discord
        await message.channel.send(e)
        await message.channel.send("Something went wrong, try asking again.")
        return
    
#Run Discord bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))