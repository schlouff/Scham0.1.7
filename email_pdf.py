import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

def send_test_pdf(receiver_email):
    sender_email = "jakobschleiff@gmail.com"  # Ersetzen Sie dies durch Ihre E-Mail-Adresse
    password = "(]8mmj0^P=PL;V+g66=g"  # Ersetzen Sie dies durch Ihr E-Mail-Passwort

    # E-Mail-Inhalt erstellen
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Test PDF-Versand"

    # E-Mail-Text
    body = "Dies ist eine Test-E-Mail mit einem PDF-Anhang."
    message.attach(MIMEText(body, "plain"))

    # PDF-Datei anhängen
    filename = "test_pdf.pdf"  # Stellen Sie sicher, dass diese Datei existiert
    attachment = open(filename, "rb")

    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)

    # Verbindung zum SMTP-Server herstellen und E-Mail senden
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Ändern Sie dies entsprechend Ihrem E-Mail-Anbieter
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
        print("E-Mail erfolgreich gesendet")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

if __name__ == "__main__":
    receiver_email = "christopher.schleif@gmx.de"
    send_test_pdf(receiver_email)