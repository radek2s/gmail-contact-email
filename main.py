# -*- coding: utf-8 -*-
from __future__ import print_function
import pickle
import random
import os
import os.path
import base64
import mimetypes
from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SENDER = "radek235s@gmail.com"
TOPIC = "Komorka 8 - Lotek"

class Contact:
    """
    Contact class 
    Manage person id, name and email to send an special email
    """

    def __init__ (self, id, imie, email):
        self.id = id
        self.name = imie
        self.email = email
        self.other_id = 0

    def randomOtherIdFromTab(self, tab):
        """Generate random other person id from input tab"""

        x = random.randint(0,len(tab)-1)
        while tab[x] == self.id:
            x = random.randint(0,len(tab)-1)

        self.other_id = tab[x]
        tab.pop(x)
                

PERSON_LIST = []
RANDOM_LIST = []


def initPerson():

    person_id = 0
    f = open("contacts.txt", "r")
    
    for x in f:
        data = x.split("|")
        PERSON_LIST.append(Contact(person_id, data[0], data[1]))
        person_id = person_id + 1

    for x in PERSON_LIST:
        RANDOM_LIST.append(x.id)

    ## Rand other person ID for each person (without repetition)
    for x in PERSON_LIST:
        x.randomOtherIdFromTab(RANDOM_LIST)

def message_body(recipient, subject):

    f = False
    if subject[-1:] == 'a':
        f = True
        
    message_extra = '''\
Niech ten czas pierwszych dni Wielkiego Postu będzie dla Ciebie czasem podejmowania walki o wytrwałość w postanowieniach. Zatrzymaniem się nad uczynkami miłosierdzia względem drugiego człowieka
        \
        '''

    if f:
        message = '''\
Cześć {p1}! 

{p2} została wylosowana dla Ciebie w dzisiejszym lotku aby otoczyć ją modlitwą w tym tygodniu. {text}
        
Pozdrawiam,
Radek\
'''.format(p1=recipient, p2=subject, text=message_extra)
    else:
        message = '''\
Cześć {p1}! 

{p2} został wylosowany dla Ciebie w dzisiejszym lotku aby otoczyć go modlitwą w tym tygodniu. {text}
        
Pozdrawiam,
Radek\
'''.format(p1=recipient, p2=subject, text=message_extra)
    
    return message


def create_message(sender, to, subject, message_text):
    """Create message for gmail function"""

    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
    """Send message via Gmail API"""
    
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
            .execute())
        print ('Message Id: ' + message['id'])
        return message
    except errors.HttpError, error:
        print (error)

def main():
    
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    for person in PERSON_LIST:
        send_message(service, 'me', create_message(SENDER, person.email, TOPIC, message_body(person.name, PERSON_LIST[person.other_id].name)))

    print ("Wysłano!")

if __name__ == '__main__':
    initPerson()
    main()