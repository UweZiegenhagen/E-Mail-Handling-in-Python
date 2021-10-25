# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:29:23 2021

@author: Uwe
"""

import imaplib
import email
import traceback 
import toml

settings = toml.load('settings.toml')

FROM_EMAIL = settings['myemail'] 
FROM_PWD = settings['password']
SMTP_SERVER = "imap.gmail.com" 
SMTP_PORT = 993


def parse_mail(text):
    zeilen = text.split('\n')
    daten = {}

    for zeile in zeilen:
        splits = zeile.split(':')
        if len(splits) == 2:
            daten[splits[0].strip()] = splits[1].strip()
            
    return daten

def read_email_from_gmail():
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()   
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id,first_email_id, -1):
            data = mail.fetch(str(i), '(RFC822)' )
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    body = ''
                    msg = email.message_from_string(str(arr[1],'ansi'))
                    
                    if msg.is_multipart():
                        # https://stackoverflow.com/questions/17874360/python-how-to-parse-the-body-from-a-raw-email-given-that-raw-email-does-not
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))

                            # skip any text/plain (txt) attachments
                            if ctype == 'text/plain' and 'attachment' not in cdispo:
                                body = part.get_payload(decode=True)  # decode
                                break
                    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
                    else:
                        body = msg.get_payload(decode=False)                    
                    
                    email_subject = msg['subject']
                    email_from = msg['from']
                    if 'WWW-Formular:' in email_subject:
                        #print('>>>\n',body,'\n>>>>')
                        struct_data = parse_mail(body)
                        print(struct_data,'\n')
                        antraege.append(struct_data.copy())
                        

    except Exception as e:
        traceback.print_exc() 
        print(str(e))

antraege = []
read_email_from_gmail()
print(len(antraege), 'Anträge wurden in den E-Mails gefunden')
