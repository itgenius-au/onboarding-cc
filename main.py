# Import required modules
import os
import sys
import json
import base64
import requests
import asana as Asana
from flask import Flask

# Flask
app = Flask(__name__)
@app.route('/')

# Generate Asana API client
def asana_client():
    return Asana.Client.access_token(os.environ['ASANA_TOKEN'])
# Create new Asana project
def copy_task(src):

    # Instantiate Asana Client
    asana = asana_client()

    # Get Template Data
    product = src['product']
    domain = src['domain']
    fullname = src['fullname']
    project = src['project']
    workspace = src['workspace']
    task = src['task']
    section = src['section']
    team = src['team']

    # Get original subtask list
    subtasks = asana.tasks.subtasks(task)
    subtask_list = []

    # Parse iterable to array
    for subtask in subtasks:
        subtask_list.append(subtask["name"])

    # Reverse order for Asana API
    subtask_list = reversed(subtask_list)

    if "Basic" in product:
        name = "Basic - " + domain + " : " + fullname
    elif "Business" in product:
        name = "Business - " + domain + " : " + fullname

    # Create new task
    new_task = asana.tasks.create({
        "workspace": workspace,
        "projects": project,
        "section": section,
        "team": team,
        "name": name
    })

    print("Created task : {0}" .format(new_task))

    # Add subtasks
    for subtask_item in subtask_list:
        asana.tasks.add_subtask(new_task['id'], {"name": subtask_item})

    return new_task['id']


# The start of the function.
def onboard_cc(message, context):
    if 'data' in message:
        data = base64.b64decode(message['data']).decode('utf-8')
        order = json.loads(data)
        print(order)

        if "Concierge" in order['product']:
            task = copy_task({
                "product" : order['product'],
                "domain": order['domain'],
                "fullname": order['fullname'],
                "workspace" : os.environ['WORKSPACE_ID'],
                "project": os.environ['CC_PROJECT_ID'],
                "task": os.environ['CC_TASK'],
                "section" : os.environ['CC_SECTION'],
                "team" : os.environ['CC_TEAM']
            })
            order['task'] = task
            response = requests.post(url=os.environ['CC_HOOK'], data=order)
    else:
        print('No data found from Pub/Sub message.')