import streamlit as st
from google.cloud import storage
import os


def upload_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """Lädt eine Datei in den Google Cloud Storage Bucket hoch."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    return f"gs://{bucket_name}/{destination_blob_name}"


# Streamlit UI
st.title("PDF Uploader für Google Cloud Storage")

# Fester Dateipfad
file_path = "test_pdf.pdf"
file_name = os.path.basename(file_path)

# GCS Bucket Name aus den Secrets lesen
bucket_name = st.secrets["gcs_bucket"]

if st.button("Datei hochladen"):
    try:
        # Datei zu GCS hochladen
        destination_blob_name = f"uploads/{file_name}"
        gcs_uri = upload_to_gcs(bucket_name, file_path, destination_blob_name)

        st.success(f"Datei erfolgreich hochgeladen! GCS URI: {gcs_uri}")
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {str(e)}")

# Anzeigen des Dateiinhalts (optional)
if os.path.exists(file_path):
    with open(file_path, "rb") as file:
        st.text("Inhalt der Datei test_pdf.pdf:")
        st.text(file.read().decode('utf-8', errors='ignore'))
else:
    st.warning(f"Die Datei {file_path} wurde nicht gefunden.")