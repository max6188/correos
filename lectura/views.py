from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CrispyLecturaForm
import io, xlsxwriter
#https://pypi.org/search/?q=emaileasily
import email
import imaplib
import os
import smtplib
import socket
import webbrowser
from email.header import decode_header
from email.message import EmailMessage
from tkinter.filedialog import askopenfilenames

message = EmailMessage()
# filenames = []
body = []
global subject



@login_required(login_url='login')
def lectura(request):
    form =CrispyLecturaForm()
    context={'form':form}
    return  render(request,'ingreso/leo_correo.html',context)

@login_required(login_url='login')
def recupera(request):
    if request.method == "POST":
        form = CrispyLecturaForm(request.POST)
        if form.is_valid():
            correo=request.POST['correo']
            clave= request.POST['clave']
            nfile ='media/'+correo[:10]

            workbook = xlsxwriter.Workbook(nfile+'.xlsx')
            worksheet = workbook.add_worksheet()
            
            label='INBOX'
            host='imap.gmail.com',
            port=993
            number_of_emails=2 
            global subject
            imap = imaplib.IMAP4_SSL(host, port)
            imap.login(correo, clave)
            status, all_messages = imap.select(label)
            messages = int(all_messages[0])
            
            fx=1
            worksheet.write(gX('a',fx), 'numero de mensajes:'+str(messages))
            #read eemail
            for i in range(messages, messages - number_of_emails, -1):
                _, email_messages = imap.fetch(str(i), "(RFC822)")
                for email_message in email_messages:
                    if isinstance(email_message, tuple):
                        msg = email.message_from_bytes(email_message[1])
                        fx=fx+2
                        worksheet.write(gX('a',fx), msg)
         

                        #Graba asunto, from y date
                        t=get_subject_and_from(msg)
                        fx=fx+2
                        worksheet.write(gX('d',fx), "from")
                        worksheet.write(gX('e',fx), t[1])
                        fx=fx+1
                        worksheet.write(gX('d',fx), 'asunto')
                        worksheet.write(gX('e',fx), t[0])
         
         
         

                        if msg.is_multipart():
                            fx=fx+2
                            fb=get_multipart_email(msg) 
                            if fb[0]=='Archivo':
                                worksheet.write(gX('a',fx), "Archivo:")
                                worksheet.write(gX('b',fx), t[1])
                            else:
                                worksheet.write(gX('a',fx), "Body:")
                                worksheet.write(gX('b',fx), t[1])

                        else:
                            fe=get_non_multipart_emails(msg)
                            fx=fx+2
                            worksheet.write(gX('a',fx), "body:")
                            worksheet.write(gX('b',fx), fe[0])

            close_imap(imap)

         

            workbook.close()


        return render(request,"presentacion.html")
    
#######################################################################################################
def gX(columna,fila):
    return columna+str(fila)

def close_imap(imap):
    """
    Closes the imaplib connection and logs out the user.
    :param imap: The imaplib connection.
    :return: 0
    """
    imap.close()
    imap.logout()


def get_attachments(part):
    """
    Gets the attached files in a email.
    Creates a folder based on email subject.
    Stores the attached in the folder.
    :param part: The email attachment part
    :return: email attached files.
    """
    filename = part.get_filename()
    if filename:
        folder_name = name_folder(subject)
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        file_path = os.path.join(folder_name, filename)
        open(file_path, "wb").write(part.get_payload(decode=True))
        print('Attached files saved at: ' + file_path)


def get_multipart_email(msg):
    """
    Classifies multipart emails based on content type.
    Prints the body of emails without attachments.
    For emails with attachments it returns the get_attachments function.
    param msg: email content.
    :return: email_body.
    """
    global subject
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        email_body = None
        try:
            email_body = part.get_payload(decode=True).decode()
        except (AttributeError, UnicodeDecodeError):
            pass
        if content_type == "text/plain" and "attachment" not in content_disposition:
            return ['body',email_body]
            #print(email_body)
        elif "attachment" in content_disposition:
            return get_attachments(part)


def get_attachments(part):
    """
    Gets the attached files in a email.
    Creates a folder based on email subject.
    Stores the attached in the folder.
    :param part: The email attachment part
    :return: email attached files.
    """
    filename = part.get_filename()
    if filename:
        folder_name = name_folder(subject)
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        file_path = os.path.join(folder_name, filename)
        open(file_path, "wb").write(part.get_payload(decode=True))
        return ['archivo',file_path]
        #print('Attached files saved at: ' + file_path)


def get_non_multipart_emails(msg):
    """
    Fetches emails without attachments.
    If email content type is text/plain it prints out the email content(email body).
    If email content type is text/html it returns the get_html_emails function.
    :param msg: email message type
    :return: email_body
    """
    content_type = msg.get_content_type()
    email_body = msg.get_payload(decode=True).decode()
    if content_type == 'text/plain':
        #print(email_body)
        return [email_body]
    if content_type == "text/html":
        return get_html_emails(email_body)

def get_subject_and_from(msg):
    """
    Gets the email subject, date and sender.
    Convert them to human-readable form.
    :param msg: email content
    :return: email subject, sender and date.
    """
    global subject
    subject, encoding = decode_header(msg['Subject'])[0]
    if isinstance(subject, bytes):
        try:
            subject = subject.decode(encoding)
        except TypeError:
            pass
    sender, encoding = decode_header(msg.get("From"))[0]
    if isinstance(sender, bytes):
        sender = sender.decode(encoding)
    date, encoding = decode_header(msg.get("Date"))[0]
    if isinstance(date, bytes):
        date = date.decode(encoding)
    return [subject,sender,date] 
    #SENDER ES FROM
    print('==' * 50)
    print("Subject: ", subject)
    print("From: ", sender)
    print("Date: ", date)



def get_html_emails(email_body):
    """
    Creates a folder with name based on the email subject.
    Creates a html file inside the folder.
    Writes the email content in the file and opens it in a web browser.
    :param email_body: fetched email body.
    :return: email_body.
    """
    try:
        folder_name = name_folder(subject)
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        filename = subject + '.html'
        file_path = os.path.join(folder_name, filename)
        open(file_path, "w").write(email_body)
        #print(email_body)
        webbrowser.open(file_path)
        return [email_body]
    except UnicodeEncodeError:
        pass


def name_folder(subject_email):
    """
    Returns the snake case naming convention for emails' attachment folders and filenames.
    :param subject_email: email subject.
    :return: folder name
    """
    return "".join(c if c.isalnum() else "_" for c in subject_email)

