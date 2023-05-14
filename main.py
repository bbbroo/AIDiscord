import openai
import time
import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

#Recognize env variables
load_dotenv()

#Initial AI Model, can change to "gpt-4" if access is enabled 
modelname = 'gpt-4' #'gpt-4' #'gpt-3.5-turbo'
#List of acceptable inputs for changing AI model to GPT-3.5
gpt35names=["!gpt-3.5-turbo", "!gpt-3.5", "!gpt3.5", "!gpt3", "!gpt35", "!gpt-35"]
#List of acceptable inputs for changing AI model to GPT-4
gpt4names=["!gpt-4", "!gpt4"]

#Set default persona, in case none is provided
persona = 'You will act as an expert in all subject matters.'

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
    global persona
    global messages

    #Set Discord channel to interact with OpenAI
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    #Read the "AIPersona.txt" file to set the AI's persona: USE FOR STARTING NEW CONTEXT
    try:
        with open("AIPersona.txt", 'r', encoding="utf8") as chat:
            persona = chat.read()
        if persona.strip()=="":
            persona = 'You will act as an expert in all subject matters.'
            await channel.send("""```ansi
\u001b[1;33mWARNING! The"AIPersona.txt" file is empty! Please add your AI\'s persona to the text file, otherwise we can continue utilizing the default persona: """ + persona + "\n```")
    except FileNotFoundError:
        await channel.send("""```ansi
\u001b[1;33mWARNING! "AIPersona.txt" file not found! Please add an "AIPersona.txt" file to the main directory with your desired AI persona included, otherwise we can continue utilizing the default persona: """ + persona + "\n```")

    #Read the "pastconversation.txt" file to pick up previous conversation: USE FOR PICKING UP PAST CONVERSATION
    # with open("pastconversation.txt", 'r', encoding="utf8") as chat:
    #     persona = chat.read()

    #Initiaing the AI's context array, and setting the AI's persona: USE FOR STARTING NEW CONTEXT
    messages = [{'role': "system", 'content': persona}]

    #Picking up the past AI's context array: USE FOR PICKING UP PAST CONVERSATION
    #messages = list(eval(persona))
    #Output to console that bot is connected to Discord
    print(f'{bot.user} has connected to Discord!')
    #Output to Discord channel that bot is ready
    await channel.send('Bot is ready! Type !help at any time for help.')

#Function that runs when message is sent in Discord channel
@bot.event
async def on_message(message):
    #Making variables within function global
    global modelname
    global messages
    global persona
    global output
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    #Check if command is used
    if message.content[0] == "!":
        #Strip input of whitespace and make lowercase
        cleaned_message = message.content.lower().strip()
        #Check if user wants the !help command and sends help message
        if cleaned_message.startswith('!help'):
            await message.channel.send("""```
To show current AI model, type: !model
To change the model to GPT-3.5, type: !gpt-3.5-turbo
To change the model to GPT-4, type: !gpt-4
To clear the message context, type: !clear
To get the AI's current persona, type: !persona
To update the AI's persona, type: '!updatepersona' followed by the new persona's description (e.g. '!updatepersona This is the new persona')
To reset the AI's persona, type: !resetpersona```""")
            return
        
        #Command to clear the message context with the AI
        if cleaned_message.startswith('!clear'):
            messages = [{'role': "system", 'content': persona}]
            await message.channel.send("Cleared message context.")
            return
        #Command to get persona
        if cleaned_message.startswith('!persona'):
            await message.channel.send("The current persona is: ")
            await output_text(persona, message)
            return
        #Command to update persona
        if cleaned_message.startswith('!updatepersona'):
            updated_persona = message.content.strip()[14:]
            if updated_persona != "":
                messages.append({'role': "system", 'content': updated_persona})
                await message.channel.send("Updated persona to: ")
                await output_text(updated_persona, message)
            else:
                await message.channel.send("""```ansi
\u001b[1;33mWARNING! Updated persona cannot be empty. Please add try the command again with text directly after the !updateprompt command, otherwise we can continue utilizing the current persona: """ + persona + "\n```")
            return
        #Command to reset persona
        if cleaned_message.startswith('!resetpersona'):
            messages.append({'role': "system", 'content': persona})
            await message.channel.send("Persona has been reset to:")
            await output_text(persona, message)
            return
        #Command to see current AI model
        if cleaned_message.startswith('!model'):
            await message.channel.send("The current AI model is: " + modelname)
            return
        #Command to change model to GPT-4
        if any(cleaned_message.startswith(c) for c in gpt4names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-4"
            await message.channel.send("Updated model to: " + modelname)
            return
        #Command to change model to GPT-3.5-turbo
        if any(cleaned_message.startswith(c) for c in gpt35names): 
            #messages = [{'role': "system", 'content': persona}]
            modelname = "gpt-3.5-turbo"
            await message.channel.send("Updated model to: " + modelname)
            return
        #This will only be reached if none of the !commands above were used
        await message.channel.send("The command was not recognized, please try again. Type !help for a list of the possible commands.")
        return
        
    #Writing users message to the AI to 'logs.txt' file
    f = open("logs.txt", "a+")
    f.write(str(datetime.datetime.now()) + " - User: " + message.content + "\n")
    f.close()

    #Adding users message to the 'messages' variable/adding it to the AI's context
    messages.append({'role': "user", 'content': message.content})

    #Attempt to get a response from the OpenAI API, exception cases will run if error occurs
    try:

        #response = await retry_api(query_openai_api)  #TEST FUNCTIONS

        #Show bot as typing on Discord while waiting for API response: ACTUAL FUNCTION
        async with message.channel.typing():
        #Giving API input of model and message context
            for retry in range(3):  # Set the number of retries here (3 in this example)
                try:
                    response = openai.ChatCompletion.create(
                        model=modelname,
                        messages=messages
                    )
                    break  # If successful, break the loop and continue processing the response
                except Exception as e:
                    if "Connection aborted" in str(e):  # Check if the error is due to connection abort
                        print(e)
                        if retry < 2:  # Only retry if the retry count is less than the limit (2 in this example)
                            time.sleep(5)  # Wait for 5 seconds before retrying
                            continue  # Retry the request
                    else:
                        raise  # Raise the error if it is not related to the connection
            else:  # If the loop finishes without a successful request
                raise Exception("Exceeded the number of retries. Failed to obtain response from the API.")
        
        #Get response text from API
        output = response['choices'][0]['message']['content']
        #Adding AI's response to the 'messages' variable/adding it to the AI's context
        messages.append({'role': "assistant", 'content': output})

        #Writing AI's response to the 'logs.txt' file
        f = open("logs.txt", "a")
        f.write(str(datetime.datetime.now()) + " - Assistant: " + output + "\n")
        f.close()

        #Writing message context to file. It is less readable but useful when attempting to pick up previous conversations
        g = open("contextlogs.txt", "a+")
        g.write(str(messages))
        g.close()

        #Call output function
        await output_text(output, message)
        
    #Handle errors recieved during attempt to get response from OpenAI's API
    except Exception as e:
        #Output error to console
        print(e)
        #Output error to Discord
        await message.channel.send(e)
        await message.channel.send("Something went wrong, try asking again.")
        return
    

'''
#Function to query the OpenAI API
async def query_openai_api():
    async with message.channel.typing():
        response = openai.ChatCompletion.create(
            model=modelname,
            messages=messages
        )
    return response


#Function to retry querying the OpenAI API 5 seconds after receiving 'Connection error'
async def retry_api(query_func, retry_delay=5):
    while True:
        try:
            result = await query_func()
            return result
        except RemoteDisconnected as e:
            print("Connection error. Retrying in", retry_delay, "seconds...")
            await asyncio.sleep(retry_delay)
'''

#Function to split up responses to less than 1900 characters, if needed, since Discord messages are limited to 2000 words
async def output_text(output, message):
    output_length = len(output)
    num_of_outputs = (output_length // 1900) + 1
    #Loop to split up response every 1900 characters
    for i in range(0,num_of_outputs):
        #Output "Continued" to Discord if text is being continued from previous output
        if i >= 1:
            await message.channel.send("(Continued)")
        #Outputting the i'th iteration of 1900 characters (If more than 1900 characters are present, on first run it'll print out the first 1900 chars, then on the next run it'll print the next 1900 chars, and so on)
        await message.channel.send(output[(1900*(i)):(1900*(i+1))])

    
#Run Discord bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))