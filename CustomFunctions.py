__author__      = "Eero Hemminki"
__copyright__   = "Copyright 2023"
__credits__     = ["Eero Hemminki, Metropolia UAS Student Union METKA"]
__license__     = "GPL"
__version__     = "1.0.1"
__maintainer__  = "Eero Hemminki"
__email__       = "eero.hemminki@metkaweb.fi"

import requests
import os

from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App

KIDE_URL = "https://kide.app/events/products"
KIDE_JSON_URL = "https://api.kide.app/api/products?city=&productType=1&categoryId=&companyId=&pageSize=&searchText="

# Needed for getChannelId() to work
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

def getChannelId(channel_name):         # Using this function is possible to retrieve channel ID's on the fly, but it is pretty slow.
    conversation_id = None              # Suggest using it once to find the ID and then just use the ID everywhere.
    try:
    # Call the conversations.list method using the WebClient
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    #Print result
                    print(f"Found conversation ID: {conversation_id}")
                    break
        return conversation_id
    except SlackApiError as e:
        print(f"Error: {e}")

def findEventsByName(eventName):
    kideEvents = requests.get(KIDE_JSON_URL)
    data = kideEvents.json()
    model = data.get("model")
    events = [] #all events with all parameters
    matchingEvents = []
    for i in model:
        events.append(i)
    i = 0
    for model in events:
        if eventName in ((events[i]["name"]).lower()):
            startTime = events[i]["time"] + events[i]["timeUntilActual"] + 3    # +3 just to make the event start time more exact as the scraping might take a moment (arbitrarily chosen)
            int(startTime)
            # The following is just to parse the information in a readable format to send to Slack
            print('{} - {}'.format(events[i]["name"], events[i]["dateActualFrom"] + "\n" + 'link to event: https://kide.app/events/{}'.format(events[i]["id"])))
            parsedStartTime = datetime.fromtimestamp(startTime, tz=None).strftime("%A, %B, %d, %Y %I:%M")
            #parsedStartTime.strftime("%A, %B, %d, %Y %I:%M:%S") <-- A longer version if you want to time to actual seconds
            matchingEvents.append('{} - {}'.format(events[i]["name"], parsedStartTime + "\n" + 'link to event: https://kide.app/events/{}'.format(events[i]["id"])))
            i+=1
        else:
            i+=1
    return matchingEvents

# The following functions are WIP

def findTicketVariants(eventName):
    foundVariantsFromEvent = []
    foundVariantsFromEvent.append(findEventsByName(eventName))
    
def setAlarmForSales(eventName):
    reminderMessage = "Sales for {} starts in 5 minutes!"
    return reminderMessage