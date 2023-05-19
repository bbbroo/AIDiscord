# AIDiscord

This is a small project to integrate usage of the OpenAI API with Discord, in order to chat with GPT-3.5-turbo and GPT-4 models.

* [Things you'll need](#things-youll-need)
* [Usage](#usage)
* [Features](#features)
* [Contributing](#contributing)
* [License](#license)

## Things you'll need

To interact with the OpenAI API you will need an [OpenAI platform account](https://platform.openai.com/overview). Once you have signed up, [create an API key](https://platform.openai.com/account/api-keys) from your account dashboard.

You will also need to create a [Discord Bot](https://discord.com/developers/applications) in order to send and read messages from Discord. After that bot is created, ensure that is has read and write permissions, then add it to your desired server. Also, retrieve the Discord bot token to enter into the env. file later.

Lastly, you will need to have a channel you would like to interact with the bot in. Once you have that channel, retrieve the channel ID in order to enter into the .env file later.

## Usage

Installation and usage is manual right now. To do so you should clone the repo and change into the new directory:

```
git clone https://github.com/bbbroo/AIDiscord.git
cd AIDiscord
```

Then install the requirements:

```
pip install -r requirements.txt
```

Next, copy the `.env.example` to `.env` and enter your OpenAI API key, Discord Channel ID, and Discord Bot Token. 

(Optional) You can update the AI's persona by updating the AIPersona.txt file, and changing it to get the AI to behave as you would like.

Once all of those steps are complete, run the script with the command:

```
python main.py
```

Once the script is up and runnning, you will get a message from the You can chat back and forth with GPT-3.5 on the command line. You can also update 'modelname' in main.py to 'gpt-4' if you have API access to that model.

## Features

✅ Ability to chat with GPT-3.5 & GPT-4 in Discord. </br>
✅ Provide persona for AI, and ability to customize on the fly. </br>
✅ Functionality to recover past conversations. </br>
✅ Ability to create and switch between multiple assistants all with different context and personasm without losing information.  </br>
<!-- ⬜ Mercur -->

## Contributing

1. Fork it ( https://github.com/bbbroo/AIDiscord/fork )
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a new Pull Request


## License

This code is available as open source under the terms of the [MIT License](https://opensource.org/license/mit/).
