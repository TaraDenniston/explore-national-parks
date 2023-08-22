import urllib.request
from app import BASE_URL, NPS_API_KEY
from models import db, Park


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

def populate_parks_table():
    """Request parks data from the NPS API and use it to populate
        the parks table in the database"""
    
    # Delete any records currently in the table
    Park.query.delete()
    
    parks = []

    # Make request to API
    url = f'{BASE_URL}/parks?limit=500&api_key={NPS_API_KEY}'
    response = urllib.request.urlopen(url)

    res_body = response.read()
    data = json.loads(res_body.decode("utf-8"))

    parks_list = data['data']

    # From the data, create new Park objects and append to list
    for item in parks_list:
        if item['images']:
            img_url=item['images'][0]['url']
            img_alt=item['images'][0]['altText']
        else:
            img_url='https://placehold.co/400x300?text=No+Image'
            img_alt='no default image'

        park = Park(park_code=item['parkCode'], full_name=item['fullName'], \
                    description=item['description'], image_url=img_url, image_alt=img_alt)
        parks.append(park)

    # Add list of parks to the db
    db.session.add_all(parks)
    db.session.commit()