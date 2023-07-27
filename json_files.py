import urllib.request
from keys import NPS_API_KEY
from models import BASE_URL


def create_activities_json_file():
    """Create JSON file with activities data collected from the NPS API"""

    # Make request to API
    url = f'{BASE_URL}/activities?api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(url)

    # Decode the response
    data = response.read().decode("UTF-8")

    # Create JSON file
    with open('static/json/activities.json', 'w') as outfile:
        outfile.write(data)

    return

def create_topics_json_file():
    """Create JSON file with topics data collected from the NPS API"""

    # Make request to API
    url = f'{BASE_URL}/topics?limit=100&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(url)

    # Decode the response
    data = response.read().decode("UTF-8")

    # Create JSON file
    with open('static/json/topics.json', 'w') as outfile:
        outfile.write(data)

    return