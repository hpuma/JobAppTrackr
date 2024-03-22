import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


# Define the scopes required for accessing Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def search_messages(service, query):
    messages = []
    page_token = None
    while True:
        result = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        messages.extend(result.get('messages', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    return messages

def get_message(service, message_id):
    return service.users().messages().get(userId='me', id=message_id).execute()

def get_message_data(message):
    return {
      "subject": message["snippet"],
      "headers": message["payload"]["headers"],
    }

def main():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # Example query to find emails from "jobs-noreply@linkedin.com" as sender
    query = "from:jobs-noreply@linkedin.com"
    messages = search_messages(service, query)

    if not messages:
        print("No messages found.")
    else:
        for message in messages:
            msg = get_message(service, message['id'])
            body = get_message_data(msg)     
            print("Subject:", body['subject'])
            print('Headers:', len(body['headers']))   
            break
        print(len(messages), "messages found")

if __name__ == '__main__':
    main()
    print("Done")
