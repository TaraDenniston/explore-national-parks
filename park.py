from keys import NPS_API_KEY
from models import BASE_URL


class Park:
    """National Park"""

    def __init__(self, data):
        "Create park from data"
        self.id = data['id']
        self.url = data['url']
        self.fullName = data['fullName']
        self.parkCode = data['parkCode']
        self.description = data['description']
        self.states = data['states']
        self.images = data['images']
        self.focusImage = self.images[0]['url']
        self.focusImageAlt = self.images[0]['altText']
        self.designation = data['designation']



