#!/usr/bin/env python3
# ^ Used if you want to run the app as a bash script

__author__      = "Eero Hemminki"
__copyright__   = "Copyright 2023"
__credits__     = ["Eero Hemminki, Metropolia UAS Student Union METKA"]
__license__     = "GPL"
__version__     = "1.0.1"
__maintainer__  = "Eero Hemminki"
__email__       = "eero.hemminki@metkaweb.fi"

import logging
import os
import openai
import requests
import CustomFunctions
import json
import re
import deepl

import logging
import os
import openai

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from PIL import Image
from CustomFunctions import findEventsByName
from CustomFunctions import getChannelId

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

app = App(
    # These should be set as environment variables on the machine you are running this on.
    # Just add export SLACK_BOT_TOKEN=somethingsomething to ~/.bashrc or similar
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

# Add functionality here
conversation_history = []
DEEPL_API_URL = "api-free.deepl.com/v2/translate"
translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))

# Add functionality here
conversation_history = []

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)
    
@app.command("/find")
def replyWithFoundEvent(ack, payload):
    ack()
    try:
        #TODO: Find a way to parse events found in function to a string or other format that the parameter 'text' accepts
        message = "<@" + payload.get('user_id') + "> " + "Events from Kide.app matching '" + payload.get('text') + "'\n" + "\n".join(findEventsByName(payload.get('text')))
        str(message)
        result = client.chat_postMessage(
        channel=payload.get('channel_id'),
        text=message
        )
    except SlackApiError as e:
        print(f"Error: {e}")
        
@app.command("/prompt")
def replyToSlashCommand(ack, payload):
    ack()
    payload.get('text')
    try:
        # For information about the different models, see OpenAI API documentation.
        # temperature determines the "creativity" of the created response
        # max_tokens determines the maximum length of the response. API limit is 4000 at the time of writing this comment.
        response = openai.Completion.create(model="gpt-4", prompt=payload.get('text'), temperature=0.6, max_tokens=8192)
        parsedResponse = response["choices"][0]["text"]
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=payload.get('channel_id'),
            text="<@" + payload.get('user_id') + "> " + payload.get('text') + "\n" + parsedResponse
        )

    except SlackApiError as e:
        print(f"Error: {e}")

@app.command("/image")
def replyWithGeneratedImage(ack, payload):
    ack()
    payload.get('text')
    try:
        # DALL-E API, free version.
        # n is the amount of images you want to generate simultaneously.
        # size is, ...well, size :D (pixels)
        response = openai.Image.create(
            prompt=payload.get('text'),
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        # The following scrapes the image so it will send as an image (not URL) to Slack.
        # If not scraped, the URL is valid for only 2-3 hours.
        responseImage = requests.get(image_url).content
        result = client.files_upload(
            channels=payload.get('channel_id'),
            file=responseImage,
            initial_comment="<@" + payload.get('user_id') + ">\n",
            title=payload.get('text')
        )
    except SlackApiError as e:
        print(f"Error: {e}")

@app.command("/translate")
def replyWithTranslatedText(ack, payload):
    ack()
    textToTranslate = payload.get('text')
    # Theoretically, you could make just one function and pass a language parameter with the slash commands
    # However, I did not find a reliable way to do this without regex or some other hack
    translatedText = translator.translate_text(textToTranslate, target_lang="EN-GB")
    try:
        result = client.chat_postMessage(
            channel=payload.get('channel_id'),
            text="<@" + payload.get('user_id') + "> \n" + translatedText.text
        )
    except SlackApiError as e:
        print(f"Error: {e}")

@app.command("/suomeksi")
def replyWithTranslatedText(ack, payload):
    ack()
    textToTranslate = payload.get('text')
    translatedText = translator.translate_text(textToTranslate, target_lang="FI")
    try:
        result = client.chat_postMessage(
            channel=payload.get('channel_id'),
            text="<@" + payload.get('user_id') + "> \n" + translatedText.text
        )
    except SlackApiError as e:
        print(f"Error: {e}")

@app.command("/svenska")
def replyWithTranslatedText(ack, payload):
    ack()
    textToTranslate = payload.get('text')
    translatedText = translator.translate_text(textToTranslate, target_lang="SV")
    try:
        result = client.chat_postMessage(
            channel=payload.get('channel_id'),
            text="<@" + payload.get('user_id') + "> \n" + translatedText.text
        )
    except SlackApiError as e:
        print(f"Error: {e}")
    
# @app.event("app_home_opened") etc
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
		{
			"type": "image",
			"title": {
				"type": "plain_text",
				"text": "#innovaatio",
			},
			"image_url": "https://metkaweb.fi/wp-content/uploads/2017/10/Metka_Simple_RGB_Full_color-300x66.jpg",
			"alt_text": "METKA logo"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Alun perin kehitetty METKAn slackiin. Made with love by Faija.\r\n\r\nPerus ominaisuuksia:\r\n- Generoi vastauksia ChatGPT:llä\r\n- Generoi kuvia DALL-E:lla\r\n- Voi kääntää tekstiä englanniksi, suomeksi tai ruotsiksi (mistä tahansa kielestä)\r\n- Voi hakea ja palauttaa Kide.app tapahtumia ja niiden aikatauluja\r\n- Works best if used in english\n\n"
			}
		},
        {
            "type": "divider"
        },
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Known issues"
			}
		},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "31.3.\n\n- If the prompt is too long, bot does not respond (API has a token limit of 4000)\n- If multiple messages are sent at the same time, bot might skip the first message and replace the prompt with the latest message."
            }
        },
        {
            "type": "divider"
        },
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Changelog"
			}
		}
	    ]
      }
    )
  
  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))