import streamlit as st
from google.cloud import storage
import os
import tempfile


def upload_to_gcs(bucket_name, source_file, destination_blob_name):
    """Lädt eine Datei in den Google Cloud Storage Bucket hoch."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file)
    return f"gs://{bucket_name}/{destination_blob_name}"


# Streamlit UI
st.title("PDF Uploader für Google Cloud Storage")

uploaded_file = st.file_uploader("Wählen Sie eine PDF-Datei aus", type="pdf")

if uploaded_file is not None:
    # Dateinamen aus dem hochgeladenen File extrahieren
    file_name = uploaded_file.name

    # GCS Bucket Name aus den Secrets lesen
    bucket_name = st.secrets["gcs_bucket"]

    if st.button("Datei hochladen"):
        try:
            # Temporäre Datei erstellen
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Datei zu GCS hochladen
            destination_blob_name = f"uploads/{file_name}"
            gcs_uri = upload_to_gcs(bucket_name, uploaded_file, destination_blob_name)

            st.success(f"Datei erfolgreich hochgeladen! GCS URI: {gcs_uri}")

            # Temporäre Datei löschen
            os.unlink(tmp_file_path)
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {str(e)}")