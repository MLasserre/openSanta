# coding: utf-8

import numpy as np
import random
import pandas as pd

import unidecode
from string import Template
import getpass

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mail_formatting(string):
    string = unidecode.unidecode(string)
    string = string.lower()
    return string


def load_mail_template(language):
    file_name = language + '_mail_template.txt'
    with open(file_name, mode='r', encoding='utf-8') as file:
        mail = Template(file.read())
    return mail 


def random_derangement(n):
    while True:
        v = np.arange(n)
        for j in range(n - 1, -1, -1):
            p = random.randint(0, j)
            if v[p] == j:
                break
            else:
                v[j], v[p] = v[p], v[j]
        else:
            if v[0] != 0:
                return v

def connect_smtp_server(user, password, smtp="smtp.gmail.com", port=587):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user_email, user_password)
        print("Successfully connected to server")
        return server
    except:
        print("Failed to connect to server")    

def disconnect_smtp_server(server):
    try:
        server.close()
        print("Successfuly disconnected from server")
    except:
        print("Failed to disconnect from server")


# Load name list
name_list = pd.read_csv("name_list.csv", header=0)

# Create email address column from first and last names
name_list['Email address'] = name_list.apply(
                                lambda row: mail_formatting(row['First name']) +'.'+
                                            mail_formatting(row['Last name']) + 
                                            '@lip6.fr', axis=1)


random.seed(0)  # Comment to generate true random
der = random_derangement(len(name_list)) # Generate random derangement

# Create To column from the generated derangement
name_list['To'] = name_list['First name'].iloc[der].reset_index(drop=True)


# Mail subjects
fr_mail_subject = '[Secret Santa] Tu dois faire un cadeau à...'
en_mail_subject = '[Secret Santa] You must give a present to...'

# Mail body templates
fr_mail = load_mail_template('fr')
en_mail = load_mail_template('en')


# User information to connect to smtp server
user_email = input('Enter your email address: ')
user_password = getpass.getpass("Enter your e-mail password: ")

server = connect_smtp_server(user_email, user_password) # Server connection

# Send customized email to every participants
for index, row in name_list.iterrows():
    if row['First name'] != 'Marvin': # Comment to send to everybody
        continue
    msg = MIMEMultipart() # create a message
    
    # setup the parameters of the message
    msg['From'] = user_email
    msg['To'] = row['Email address']
    
    # add in the actual person name to the message template
    if row['Language'] == 'en':
        custom_mail = en_mail.substitute(SANTA_NAME=row['First name'], RECIPIENT_NAME=row['To'])
        msg['Subject'] = en_mail_subject
    elif row['Language'] == 'fr':
        custom_mail = fr_mail.substitute(SANTA_NAME=row['First name'], RECIPIENT_NAME=row['To'])
        msg['Subject'] = fr_mail_subject
        
    # add in the message body
    msg.attach(MIMEText(custom_mail, 'plain'))
        
    # send the message via the server set up earlier.
    server.send_message(msg)

    del msg

disconnect_smtp_server(server) # Server disconnection
