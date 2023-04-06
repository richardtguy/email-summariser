import os
import argparse
from email import message_from_string

from bs4 import BeautifulSoup
from mailparser_reply import EmailReplyParser
import openai

class EmailSummary():
    def __init__(self, email_str):
        # parse email message from string
        self.msg = message_from_string(email_str)
        for k, v in self.msg.items():
            setattr(self, k.lower(), v)
        self._summarise_latest_reply()

    def _summarise_latest_reply(self):
        # extract plain text body
        if self.msg.is_multipart():
            for part in self.msg.walk():
                if 'text/plain' in part.get_content_type():
                    body = part.get_payload(decode=True)
        else:
            body = self.msg.get_payload(decode=True)

        # remove any formatting tags
        soup = BeautifulSoup(body, features="html.parser")
        mail_body = soup.get_text()
        
        # extract latest reply
        rp = EmailReplyParser()
        m = rp.read(mail_body)
        latest_reply = m.replies[0].body

        # summarise latest reply using OpenAI
        prompt = f"Summarise this email in one sentence: {latest_reply}"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        self.summary = response['choices'][0]['message']['content']
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    
    with open(args.filename, "r") as f:
        raw_email = f.read()
    print(EmailSummary(raw_email).summary)