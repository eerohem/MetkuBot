# inno-slack

Slack App with the following features:
- Reply to messages with text generated with ChatGPT
- Generate images with OpenAI's DALL-E API
- Finds events from Kide.app with given search parameters.

Created as an innovation project for Metropolia UAS Student Union METKA

Made with Slack Bolt

Dependencies:

- Python3.7.1 or above
- Api keys for the following:
  - OpenAI API
  - Slack BOT_TOKEN and SLACK_SIGNING_SECRET
  - DeepL Auth Token
  
Some used libraries may need installation.

To run:

Install ngrok
  - ngrok start [port]

Make a Slack Application
  - Grab SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET from App settings

Set all Api & Auth tokens as environment variables
  
pip install slack_bolt
python app.py