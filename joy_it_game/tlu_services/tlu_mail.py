""" module: tlu_mail
** Content **
This module shall send and receive emails

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
from datetime import datetime
import email
import logging

class tlu_mail_msg:
    """Simply hold email-message content    
    """
    
    msg_from = ""
    msg_to = ""
    msg_date = datetime.now()
    msg_subject = ""
    msg_content = ""
    msg_uid = ""
    def __init__(self,subject=""):
        """
        Initialization adds optional subject
        
        :param subject: Optional header of the message
        :type subject: str
        
        """
        self.msg_subject=subject
          
class tlu_mail:
    """Provide sending and receiving emails with html-body via SSL-SMTP 
    """
    
    def send_email(self,to,subject,body, 
                   mail_user='', 
                   mail_server='', 
                   mail_port='', 
                   mail_pw=''):        
        """Sends an email
        
        This method is going to try to send an email using the parameters provided
        
        **Parameters**:
        
        :param to:           The receiver of the email
        :param subject:      The headline
        :param body:         Content in html-notation
        :param mail_user:    login-user to the server, also sender-email
        :param mail_server:  URL of ssl-encoded SMTP-server
        :param mail_port:    ssl-port of SMTP-Server
        :param mail_pw:      Password in cleartype to log into the SMTP-Server
        :type to: str
        :type subject: str
        :type bodx: str
        :type mail_user: str
        :type mail_port: int
        :type mail_pw: str
        :returns: Nothing would be returned, although Exceptions may get raised   
        :rtype: None        
        """
        
        msg = MIMEMultipart()
        msg['From'] = mail_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP_SSL(mail_server, mail_port)
        server.login(mail_user, mail_pw)
        text = msg.as_string()
        server.sendmail(mail_user, to, text)
        server.quit()
     
    def fetch_email(self, mail_subject="", 
                    mail_user='', 
                    mail_server='', 
                    mail_port='', 
                    mail_pw=''):
        """Fetches email. If subject given, searches for the specified email.
        
        @copyright  Contains Info from: https://stackoverflow.com/questions/2230037/how-to-fetch-an-email-body-using-imaplib-in-python"

        :param mail_user: str   login-user to the server, also sender-email
        :param mail_server: str URL of ssl-encoded SMTP-server
        :param mail_port: int   ssl-port of SMTP-Server
        :param mail_pw: str     Password in cleartype to log into the SMTP-Server
        :rtype: [] Returns List of messages found. If empty then there are no messages found          
        """
        
        ret=[]
        mail = imaplib.IMAP4_SSL(mail_server, mail_port)
        mail.login(mail_user, mail_pw)
        mail.list()
        mail.select('Inbox')
        result, data = mail.uid('search',None, "UNSEEN")
        logging.debug('Result of mail search was '+result)
        i = len(data[0].split())
        
        for x in range(i):
            email_uid = data[0].split()[x]
            result, email_data = mail.uid('fetch', email_uid, '(RFC822)')
            raw_email = email_data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            #Now header
            email_subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
            if (len(mail_subject)>0)&(email_subject != mail_subject):
                continue # skip unwanted emails
            date_tuple = email.utils.parsedate_tz(email_message['Date'])
            if date_tuple:
                local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
            email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
            email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))

            # Body details
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                else:
                    continue
            
            found_email = tlu_mail_msg(mail_subject)
            found_email.msg_content=body
            found_email.msg_date=local_message_date
            found_email.msg_from=email_from
            found_email.msg_to=email_to
            found_email.msg_uid=email_uid
            ret += [found_email]
        mail.close()
        mail.logout()
        return ret
    def remove_email(self,mail_msg,
                    mail_user='', 
                    mail_server='', 
                    mail_port='', 
                    mail_pw=''):
        """Removes email specified by msg
        
        @copyright Contains Info from https://stackoverflow.com/questions/3180891/imap-deleting-messages
        
        :param mail_msg: tlu_mail_msg message that should be removed 
        :param mail_user: str   login-user to the server, also sender-email
        :param mail_server: str URL of ssl-encoded SMTP-server
        :param mail_port: int   ssl-port of SMTP-Server
        :param mail_pw: str     Password in cleartype to log into the SMTP-Server

        """
        
        mail = imaplib.IMAP4_SSL(mail_server, mail_port)
        mail.login(mail_user, mail_pw)
        mail.list()
        mail.select('inbox')
        mail.uid('STORE', mail_msg.msg_uid, '+FLAGS','(\\Deleted)')
        mail.expunge()
        mail.close()
        mail.logout()