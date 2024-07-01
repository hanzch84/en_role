import openai
import os
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from googletrans import Translator

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정 (환경 변수에서 가져오기)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# ChatGPT API 호출 함수
def generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
    messages=[
        {"role": "system",
        "content": "You are a skilled playwright specializing in role-playing scripts as a teacher. You excel at writing scripts with easy words, especially for elementary school students. You can write engaging role-play scripts using educationally appropriate words and situations that help students to use the key expressions in an interesting way."},
        {"role": "user", "content": f'''Create a role-play script for {grade} grade Korean elementary school students. The script should play for {duration} seconds (a line in the script takes 4~5 seconds). Include {num_people} balanced roles in the script. Include Key phrases: {key_phrases} and Key words: {key_words}. The format of the script is 'name:line'. Return scripts only.
        #script example (make a script like this example's format. Same format, different content.)
        [Characters]
        1. Sumi: An active and curious student.
        2. Jin: A calm and inquisitive student.
        3. Minho: A student interested in history.
        4. Hana: A responsible student who takes care of her friends.
        
        [Backgrounds]
        When: Monday morning, right before the field trip.
        Where: In the classroom and on the school bus.
        Elementary school students are getting ready for a field trip to the museum.
        They are discussing what they want to see and are excited about the trip.

        [script]
        Sumi: Hello, everyone! How are you today?    
        Jin: I'm good, thank you. How about you, Sumi?        
        Minho: I'm excited! We have a field trip today.        
        Hana: Yes, we are going to the museum. What do you want to see first?        
        Sumi: I want to see the dinosaur bones!        
        Jin: Me too! Dinosaurs are so cool.
        '''}
    ]

    )

    # Convert the response to a Python dictionary
    response_dict = response['choices'][0]['message']['content']
    return response_dict


def translate_script(script, src='en', dest='ko'):
    translator = Translator()
    lines = script.split('\n')
    translated_lines = []
    
    for line in lines:
        if ':' in line:
            name, sentence = line.split(':', 1)
            translated_sentence = translator.translate(sentence.strip(), src=src, dest=dest).text
            translated_lines.append(f'{name}: {translated_sentence}')
        else:
            translated_lines.append(line)
    
    return '\n'.join(translated_lines)


def remove_korean_translation(script):
    # Extract lines after 'scripts:'
    start_marker = "[script]"
    
    # Find the start position of the marker
    start_pos = script.find(start_marker)
    
    # Check if the start_marker exists in the script
    if start_pos == -1:
        raise ValueError("The marker '[script]' not found in the script")

    start_pos += len(start_marker)
    
    # Extract the lines after the marker
    script_lines = script[start_pos:].strip().split("\n")
    
    # Remove the lines with Korean translations and character names
    english_lines = []
    for line in script_lines:
        if ":" in line:
            parts = line.split(":")
            if len(parts) > 1:
                english_line = parts[1].strip()
                if english_line:  # Ensure the line is not empty
                    english_lines.append(english_line)
    
    # Join the English lines into the final script
    final_script = "\n".join(english_lines).strip()
    
    if not final_script:
        raise ValueError("Final script after removing Korean translation is empty")
    
    return final_script

def download_audio(script):
    script_without_korean = remove_korean_translation(script)
    tts = gTTS(script_without_korean, lang='en')
    audio_file_path = "script_audio.mp3"
    tts.save(audio_file_path)
    return audio_file_path

def download_script(script):
    script_file_path = "script.txt"
    with open(script_file_path, "w", encoding="utf-8") as file:
        file.write(script)
    return script_file_path

# Streamlit UI 구성
st.title("초등 영어 상황극 대본 생성기")
col1, col2, col3 = st.columns(3)

grade = col1.selectbox("학년", ["3rd", "4th", "5th", "6th"], index=3)
num_people = col2.slider("상황극 인원", min_value=2, max_value=10, value=4)
duration = col3.slider("길이(초)", min_value=10, max_value=300, value=30)
key_phrases = st.text_input("주요 표현 입력")
key_words = st.text_area("주요 단어 입력")
try:
    content = st.session_state['script']
except:
    content = "\n"*10

script_placeholder = st.code(content,"http")
translate_placeholder = st.code(translate_script(content),"http")

if 'script' not in st.session_state:
    st.session_state['script'] = ""

if st.button("상황극 대본 생성"):
    try:
        st.session_state['script'] = generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words)
        
    except ValueError as e:
        st.error(str(e))

if st.session_state['script']:
    if st.button("음성파일 생성"):
        try:
            audio_file = download_audio(st.session_state['script'])
            with open(audio_file, "rb") as file:
                st.download_button(label="Download audio", data=file, file_name="script_audio.mp3", mime="audio/mp3")
        except ValueError as e:
            st.error(str(e))

    if st.button("대본 다운로드"):
        script_file = download_script(st.session_state['script'])
        with open(script_file, "rb") as file:
            st.download_button(label="Download script", data=file, file_name="script.txt", mime="text/plain")

