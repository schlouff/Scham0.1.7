import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_sample_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 750, "Dies ist ein Test-PDF für den E-Mail-Versand.")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

st.title("Test: PDF per E-Mail senden mit Streamlit")

# Erstelle ein Beispiel-PDF
pdf = create_sample_pdf()

# E-Mail-Adresse Eingabefeld
email = st.text_input("Empfänger E-Mail-Adresse", "christopher.schleif@gmx.de")

# Button zum Senden der E-Mail
if st.button("PDF per E-Mail senden"):
    try:
        # E-Mail senden
        st.experimental_email(
            to=email,
            subject="Test: Ihr generiertes PDF",
            message="Hier ist Ihr Test-PDF-Dokument.",
            attachments=[pdf]
        )
        st.success("E-Mail wurde erfolgreich gesendet!")
    except Exception as e:
        st.error(f"Fehler beim Senden der E-Mail: {str(e)}")

# Button zum Herunterladen des PDFs (optional, zum Testen)
st.download_button(
    label="Test-PDF herunterladen",
    data=pdf,
    file_name="test.pdf",
    mime="application/pdf"
)