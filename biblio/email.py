import smtplib, ssl
from email.message import EmailMessage

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



from biblio.credentials import email_access






def send_email(receiver, livro, nome,biblio):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    password = email_access().get_password()
    sender_email = email_access().get_address()
    receiver_email = receiver
    mail_content =  f'''\
    Prezado(a) {nome},
    
    Informamos que um exemplar do livro {livro} encontra-se reservado para retirada.
    
    Favor retirar o livro em até 7 dias.
    
    Atenciosamente,
    
    Equipe {biblio}

    This message is sent from BiblioSystem.'''


    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = f'Exemplar de {livro} disponivel'
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_email, password) #login with mail_id and password
    session.sendmail(sender_email, receiver_email, message.as_string())
    session.quit()


