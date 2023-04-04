import os
import argparse
from email.parser import Parser

from bs4 import BeautifulSoup
from mailparser_reply import EmailReplyParser
import openai

def summarise_email(raw_email: str) -> str:
    # parse plain text body from raw email
    p = Parser()    
    msg = p.parsestr(raw_email)
    body=""
    if msg.is_multipart():
        for part in msg.walk():
            if 'text/plain' in part.get_content_type():
               body += part.get_payload(decode=True).decode('utf-8')
    else:
        body = msg.get_payload(decode=True).decode('utf-8')

    # remove any formatting tags
    soup = BeautifulSoup(body, features="html.parser")
    mail_body = soup.get_text()
    
    # extract latest reply
    rp = EmailReplyParser()
    msg = rp.read(mail_body)
    latest_reply = msg.replies[0].body

    # summarise latest reply using OpenAI
    prompt = f"Summarise this email in one sentence: {latest_reply}"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return(response['choices'][0]['message']['content'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    
    with open(args.filename, "r") as f:
        raw_email = f.read()
    text = summarise_email(raw_email)
    print(text)