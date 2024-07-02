#Scham mit Image_Generating v0.2

import streamlit as st
from io import BytesIO

from pdf_utils import create_10x15_pdf_with_image
from upload_pdf import upload_pdf_to_gcs

import os
import time

from openai import OpenAI
from datetime import datetime

# Setze den API-Schlüssel

api_key = st.secrets["api"]["api_key"]
assert api_key.startswith('sk-'), 'Error loading the API key. The API key starts with "sk-"'
os.environ['OPENAI_API_KEY'] = api_key

#openai.api_key = api_key

client = OpenAI()

# Initialisierungen
questions = [
    "Hallo. Schön, dass du hier bist.\n\nDu hast jetzt die Möglichkeit eine Situation zu untersuchen, die bei dir Scham ausgelöst hat, die dir peinlich/unangenehm war und es vielleicht noch ist. Was für eine peinliche oder schamauslösende Situation fällt dir ein? Du wirst mit der Erinnerung an diese Situation weiterarbeiten. Wenn du merkst, das ist jetzt gerade zu krass, vielleicht gibt es ja auch eine Situation, in der du nicht so tief einsteigst, aber wo das Gefühl auch wieder auftaucht.\nDu übernimmst die Verantwortung für dich selbst in dieser Arbeit, aber wir geben dir Raum und Zeit zum reflektieren und vielleicht sogar anstöße das Gefühl zu der Situation zu verändern. Also bist du startklar?\nSchreib “ok” - und dann kann es losgehen.",
    "Schau, welche Peinliche/schamhafte Situation heute für dich passt. Schau mal in deinem inneren, was du alles siehst in dieser Situation und was du dabei fühlst. Lass dir dabei zeit und schreib “ok” wenn du eine Situation vor Augen hast.",
    "Gibt es in dieser Situation etwas, dass jemand gesagt hat? Was ein bestimmtes Gefühl ausgelöst hat? Gibt es was was dir an dieser Situation besonders auffällt vielleicht ein Detail?\nSchreib “ok”, wenn es weitergehen kann.",
    "Jetzt überleg mal. Kannst du dieser Situation einen Namen geben? Oder eine Überschrift? Die Überschrift kann sich darauf beziehen, oder ein Headliner sein.\nWas wäre ein Songtitel für diese Situation? Schreibe die Überschrift oder den Songtitel in das unten liegende Feld. Bitte verzichte hier auf konkrete Namen(eigentlich hatten wir diese Aufgabe im Kopf gemacht weil da auch krasse sachen rauskommen können die vielleicht so nicht ausgesprochen werden müssen. )\nJetzt schreib den Namen auf.",
    "Wenn diese Situation ein Bild bekommen würde, wie sähe das aus?\nWas für eine Landschaft wäre diese Situation? Eine Landschaft kann irgendein Ort sein, kann auch in der Stadt sein oder ein Raum. Das muss gar nichts mit dem Ort zu tun haben, wo die Situation stattgefunden hat. Es geht eher um das Gefühl von der Situation. Ist das eng, oder ganz weit?\nBeschreib jetzt diese Landschaft. Wie sieht sie aus?\n",
    "Vielleicht ist es eher ein Tier? Vielleicht denkt ihr an euch, was für ein Tier ihr gewesen wärt, z.b. wie eine Maus, die sich verkrümeln wollte oder ihr denkt an das Gegenüber welches Tier wäre das im Vergleich zu euch gewesen. Beschreibt dieses Tier wie sieht das aus.\nNimm dir Zeit, wenn du deine Landschaft oder dein Tier vor Augen hast schreib alles dazu unten in das Feld hinein.",
    "Super, du hast jetzt ein Gefühl, eine Überschrift und ein Bild. Du hast gerade gesehen, wie Kunst entstehen kann.\n\nJetzt soll die Bildbeschreibung kreiert werden."
]

bot_responses = list()
messages = list()

#system_prompt = 'Answer as concisely as possible.'
#messages.append({'role': 'system', 'content': system_prompt})

def chat_with_bot(user_input):
    messages.append({'role': 'user', 'content': user_input})

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.7,
    )

    current_response = completion.choices[0].message.content
    bot_responses.append(current_response)
    messages.append({'role': 'assistant', 'content': current_response})
    return current_response

# user-description ohne Eingaben
#description_prompt = "Eine Ente wackelt über die Straße"

def create_artistic_description(responses):
    description_prompt = (
        f"Erstelle (auf deutsch) eine künstlerische Beschreibung, die auf den Eingaben beruht:\n"
        f"1. Situation: {responses[0]}\n"
        f"2. Situation Details: {responses[1]}\n"
        f"3. Detail: {responses[2]}\n"
        f"4. Title: {responses[3]}\n"
        f"5. Landscape: {responses[4]}\n"
        f"6. Animal (if applicable): {responses[5] if len(responses) > 5 else 'N/A'}"
    )

    messages.append({'role': 'user', 'content': description_prompt})

    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.7,
    )

    artistic_description = completion.choices[0].message.content
    return artistic_description

def create_image_url(description_prompt):
    response = client.images.generate(
        model='dall-e-3',
        prompt=description_prompt,
        style='vivid',
        size='1024x1024', # 1024x1792, 1792x1024 pixels
        quality='standard',
        n=1
    )
    image_url = response.data[0].url
    return image_url



if __name__ == '__main__':
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title('Chat Bot')
    with col2:
        st.image('ai.png', width=70)

    # Neues Eingabefeld für den Namen
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""

    if not st.session_state.user_name:
        st.write("Damit wir dir am Ende dein geschaffenes Bild übergeben können, brauchen wir deinen Namen. Bitte gib hier deinen Namen ein.")
        user_name = st.text_input("Dein Name:")
        if st.button("Name bestätigen"):
            if user_name:
                st.session_state.user_name = user_name
                print(f"Benutzername: {st.session_state.user_name}")  # Anzeige im Terminal
                st.success(f"Danke, {st.session_state.user_name}! Lass uns beginnen.")
                st.write(f"Eingegebener Name: {st.session_state.user_name}")  # Anzeige in der Streamlit-App
            else:
                st.warning("Bitte gib deinen Namen ein.")
    else:
        # Anzeige des gespeicherten Namens, wenn bereits eingegeben
        st.write(f"Eingegebener Name: {st.session_state.user_name}")
        print(f"Gespeicherter Benutzername: {st.session_state.user_name}")  # Anzeige im Terminal bei jedem Neustart

    # Nur den Chat-Bot anzeigen, wenn der Name eingegeben wurde
    if st.session_state.user_name:
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0

        if 'responses' not in st.session_state:
            st.session_state.responses = []



    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

    if 'responses' not in st.session_state:
        st.session_state.responses = []

    with st.form(key='chat_form'):
        if st.session_state.current_question_index < len(questions):
            current_question = questions[st.session_state.current_question_index]
        else:
            current_question = "Thank you for your responses. How else can I assist you?"

        st.write(f'Chat Bot: {current_question}')
        user_input = st.text_input('You:', '')

        submit_button = st.form_submit_button(label='Send')

        if submit_button:
            if user_input.lower() in ['exit', 'quit']:
                st.write('Chat Bot: I was happy to assist you. Bye bye!')
                time.sleep(2)
                st.stop()

            if user_input.lower() == '':
                st.warning('Please enter a message.')
            else:
                st.session_state.responses.append(user_input)

                if 'history' not in st.session_state:
                    st.session_state['history'] = f'You: {user_input}\n'
                else:
                    st.session_state['history'] += f'You: {user_input}\n'

                st.text_area(label='Chat History', value=st.session_state['history'], height=400)

                if st.session_state.current_question_index < len(questions) - 1:
                    st.session_state.current_question_index += 1
                elif st.session_state.current_question_index == len(questions) - 1:
                    artistic_description = create_artistic_description(st.session_state.responses)
                    st.write(f'Artistic Description: {artistic_description}')

                    # Erzeuge die Bild-URL und zeige sie an
                    image_url = create_image_url(artistic_description)
                    st.write(f'Image URL: {image_url}')
                    st.image(image_url)

                    # Erzeuge das PDF mit der generierten Bild-URL
                    pdf = create_10x15_pdf_with_image(image_url, st.session_state.user_name)

                    st.session_state.current_question_index += 1
    if 'pdf' in locals():
        # Konvertieren Sie das PDF in ein BytesIO-Objekt
        pdf_bytes = BytesIO(pdf.getvalue())

        # Generiere einen Timestamp für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Lade das PDF in Google Cloud Storage hoch
        bucket_name = "vse-schamstaton24-07"
        destination_blob_name = f"MemePDFs/generated_pdf_{timestamp}.pdf"

        # Angepasste upload_pdf_to_gcs Funktion aufrufen
        upload_pdf_to_gcs(bucket_name, pdf_bytes, destination_blob_name)

        # Biete das PDF zum Download an
        st.download_button(
            label=f"10x15 PDF herunterladen ({timestamp})",
            data=pdf,
            file_name=f"10x15_pdf_mit_bild_{timestamp}.pdf",
            mime="application/pdf"
        )


# asbnkdsja