import time
import os
import pickle
import base64
from email import message_from_bytes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import groq

# Groq API setup (DO NOT store secrets in code, use env vars instead)
groq_api_key = "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"
client = groq.Groq(api_key=groq_api_key)
def detect_spam(message):
    prompt = f"""
You are a spam detection AI. Read the message and classify it as "Spam" or "Not Spam". Then explain the reason in one or two sentences.

Message: "{message}"

Classification:"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that detects spam and explains its reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100,
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        return f"Error: {e}"

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_655930560806-ab48v1enoevicjm62qus0ng7qlon4sge.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_latest_emails(service, max_results=5):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        msg_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        mime_msg = message_from_bytes(msg_bytes)
        emails.append({
            "subject": mime_msg.get('subject'),
            "from": mime_msg.get('from'),
            "body": get_body_from_email(mime_msg)
        })
    return emails

def get_body_from_email(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors='ignore')
    else:
        return mime_msg.get_payload(decode=True).decode(errors='ignore')
    return ""

def main():
    service = gmail_authenticate()
    print("Gmail spam detection bot started. Type 'exit' to quit at any prompt.\n")
    while True:
        emails = get_latest_emails(service)
        for email in emails:
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print("Spam Check:")
            result = detect_spam(email['body'][:2000])  # limit to 2000 chars
            print(result)
            print("="*60)

        print("Press Enter to check again or type 'exit' to quit: ")
        time.sleep(10)

        # Optionally, add a short delay to avoid rapid API calls (uncomment below)
        # time.sleep(10)  # wait 10 seconds before checking again

main()