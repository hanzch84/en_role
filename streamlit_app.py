import openai
import os
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from googletrans import Translator
from datetime import datetime

# CSS 스타일 정의
css = '''
<style>
    
    [data-testid="baseButton-secondary"]{
    width: 100% !important;
    color: orange;
    font-weight: 500;
    font-size: 16px;
    background-color: #0e0e0e;
    }

    .code-wrap {
        white-space: pre-wrap; /* 줄 바꿈을 허용 */
    }
    h1{
        text-align: center; /* 텍스트를 가운데 정렬 */
        line-height: 0.6;
    }
    h3{
        text-align: center; /* 텍스트를 가운데 정렬 */
        line-height: 0.6;
        font-size: 16px;

    }
    p {
        text-align: center; /* 텍스트를 가운데 정렬 */
        font-size: 14px;
        line-height: 0.8;
    }
    [data-testid="baseButton-secondary"]{
    width: 100% !important;
    color: orange;
    }
</style>
'''

# 스타일 적용 및 코드 출력
st.markdown(css, unsafe_allow_html=True)

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정 (환경 변수에서 가져오기)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# ChatGPT API 호출 함수
def generate_situation_with_gpt(num_people):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
    messages=[
        {"role": "system",
        "content": "You are a knowledgeable theater teacher with a knack for humor and creativity."},
        {"role": "user", "content": f"In one short sentence(in 15 words), provide a unique background and situation in Korean for {num_people} people to role play. role can be adults not only students.(ex)우주선 고장으로 조난 당한 긴박한 상황."}
    ]
    )
    # Convert the response to a Python dictionary
    response_dict = response['choices'][0]['message']['content']
    return response_dict

# ChatGPT API 호출 함수
def generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
    messages=[
        {"role": "system",
        "content": "You are a skilled playwright specializing in role-playing scripts as a teacher. You excel at writing scripts with easy words, especially for elementary school students. You can write engaging role-play scripts using educationally appropriate words and situations that help students to use the key expressions in an interesting way."},
        {"role": "user", "content": f'''Create a role-play script for {grade} grade Korean elementary school students. The script should play for {duration} seconds (a line in the script takes 4~5 seconds). Include {num_people} balanced roles in the script. Include Key phrases: {key_phrases} and Key words: {key_words}.
         The format of the script is 'name:line'. Return scripts only.
         {"" if situations=="" else "("+situations+") is The setting for the scenario you are creating. Reflect it in the background of the role-play scenario."}
        #script example (make a script like this example's format. Same format, different content.)
        [Characters]
        1. Sumi: An active and curious student.
        2. Jin: A calm and inquisitive student.
        3. Minho: A student interested in history.
        4. Hana: A responsible student who takes care of her friends.
        
        [Backgrounds]
        When: Monday morning, right before the field trip.
        Where: In the classroom and on the school bus.
        Scene: Elementary school students are getting ready for a field trip to the museum.
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

def translate_gpt(script):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
    messages=[
    {"role": "system",
    "content": "You are a skilled playwright specializing in translating role-playing scripts for elementary school students. Your expertise is in using simple, educationally appropriate language that engages young learners. You excel at translating English scripts to Korean, maintaining the original context and simplicity."},
    {"role": "user", "content": f'Please translate the following script to Korean, maintaining the same format and context. Ensure that the translation uses easy words suitable for elementary school students.\n{script}'}
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


def remove_extras(script):
    # Extract lines after 'scripts:'
    start_marker = "[script]"
    
    # Find the start position of the marker
    start_pos = script.find(start_marker)
    
    # Check if the start_marker exists in the script
    if start_pos == -1:
        start_pos = script.find("[Script]")
    if start_pos == -1:
        start_pos = script.find("[Scripts]")
    if start_pos == -1:
        start_pos = script.find("[scripts]")
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
    script_without_korean = remove_extras(script)
    tts = gTTS(script_without_korean, lang='en')
    audio_file_path = "script_audio.mp3"
    tts.save(audio_file_path)
    return audio_file_path

def download_script(script):
    script_file_path = "script.txt"
    with open(script_file_path, "w", encoding="utf-8") as file:
        file.write(script)
    return script_file_path

if 'situation' not in st.session_state:
    st.session_state.situation = ''

# Streamlit UI 구성
st.title("영어 대본 생성기")
st.subheader("EnRole: English Role-play Scripter")
st.write("교사 박현수, 버그 및 개선 문의: hanzch84@gmail.com")
cola, colb, colc = st.columns([2,3,4])

grade = cola.selectbox("학년", ["3rd", "4th", "5th", "6th"], index=3)
num_people = colb.slider("상황극 인원", min_value=2, max_value=10, value=3)
duration = colc.slider("상황극 길이(초)", min_value=10, max_value=300, value=30)
col_sit,col_rnd_btn = st.columns([10,1])
if col_rnd_btn.button("랜덤"):
    st.session_state.situation = generate_situation_with_gpt(num_people)
situations = col_sit.text_input("간단한 상황 입력(한글 혹은 영어)",value=st.session_state.situation,key="situations",placeholder="대략적 상황을 한글이나 영어로 입력.(예)우주선 고장으로 조난 당함.",label_visibility="collapsed")


with st.expander("상세 옵션"):
    key_words = st.text_input("주요 단어 입력",key="words",placeholder="cold, headache, medicine 등 연습할 단어를 쉼표로 구분해서 입력하세요.")
    key_phrases = st.text_area("주요 표현 입력",key="expressions",placeholder="What's wrong?, Get some rest 등 연습할 표현을 쉼표나 엔터로 구분해서 입력하세요.")
    

col1, col2, col22, col3, col33 = st.columns([3,2,3,2,3])

# 스피너를 표시하면서 계산 진행 오버레이와 스피너를 위한 컨테이너 생성
overlay_container = st.empty()
# 오버레이와 스피너 추가
overlay_container.markdown("""
<style>
.overlay {
    position: fixed;top: 0;left: 0;width: 100%;height: 100%;
    background: rgba(0, 0, 0, 0.7);z-index: 999;display: flex;
    justify-content: center;align-items: center;                }
.spinner {margin-bottom: 10px;}
</style>
<div class="overlay"><div><div class="spinner">
            <span class="fa fa-spinner fa-spin fa-3x"></span>
        </div><div style="color: white;">대본을 출력하는 중...</div></div></div>""", unsafe_allow_html=True)
try:
    content = st.session_state['script']
    trans = st.session_state['translated']
    script_placeholder = st.code(content,"http")
    translate_placeholder = st.code(trans,"http")
except:
    content = "\n"*10+"Engish Script"
    trans = "\n"*10+"한국어 번역"
    script_placeholder = st.code(content,"http")
    translate_placeholder = st.code(trans,"http")

# 작업이 완료되면 오버레이와 스피너를 제거합니다.
overlay_container.empty()

if 'script' not in st.session_state:
    st.session_state['script'] = ""
    st.session_state['translated'] = ""

if col1.button("상황극 대본 생성"):
    try:
        # 스피너를 표시하면서 계산 진행 오버레이와 스피너를 위한 컨테이너 생성
        overlay_container = st.empty()
        # 오버레이와 스피너 추가
        overlay_container.markdown("""
        <style>
        .overlay {
            position: fixed;top: 0;left: 0;width: 100%;height: 100%;
            background: rgba(0, 0, 0, 0.7);z-index: 999;display: flex;
            justify-content: center;align-items: center;                }
        .spinner {margin-bottom: 10px;}
        </style>
        <div class="overlay"><div><div class="spinner">
                    <span class="fa fa-spinner fa-spin fa-3x"></span>
                </div><div style="color: white;">대본을 만들고 번역하는 중...</div></div></div>""", unsafe_allow_html=True)
        st.session_state['script'] = generate_script_with_gpt(grade, num_people, duration, key_phrases, key_words)
        st.session_state['translated'] = translate_gpt(st.session_state['script'])
        content = st.session_state['script']
        trans = st.session_state['translated']    
        script_placeholder.code(content,"http")
        translate_placeholder.code(trans,"http")
            
        # 작업이 완료되면 오버레이와 스피너를 제거합니다.
        overlay_container.empty()
        st.balloons()
        
    except ValueError as e:
        st.error(str(e))

if st.session_state['script']:
    if col2.button("음성 생성"):
        # 스피너를 표시하면서 계산 진행 오버레이와 스피너를 위한 컨테이너 생성
        overlay_container = st.empty()
        # 오버레이와 스피너 추가
        overlay_container.markdown("""
            <style>
                .overlay {
                    position: fixed;top: 0;left: 0;width: 100%;height: 100%;
                    background: rgba(0, 0, 0, 0.7);z-index: 999;display: flex;
                    justify-content: center;align-items: center;                }
                .spinner {margin-bottom: 10px;} 
            </style>
            <div class="overlay"><div><div class="spinner">
                <span class="fa fa-spinner fa-spin fa-3x"></span>
            </div><div style="color: white;">"대본을 오디오 파일로 생성 중..."</div></div></div>""", unsafe_allow_html=True)
        try:
            audio_file = download_audio(st.session_state['script'])
            with open(audio_file, "rb") as file:
                col22.download_button(label="음성 다운로드", data=file, file_name="script_audio.mp3", mime="audio/mp3")
        except ValueError as e:
            st.error(str(e))
        overlay_container.empty()


    if col3.button("대본 생성"):
        script_file = download_script(st.session_state['script']+'\n\n\n'+st.session_state['translated'])
        with open(script_file, "rb") as file:
            col33.download_button(label="대본 다운로드", data=file, file_name="script.txt", mime="text/plain")
