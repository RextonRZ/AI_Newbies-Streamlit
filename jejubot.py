import streamlit as st
import os
import base64
from datetime import datetime
from predibase import Predibase
from dataclasses import dataclass
from typing import Literal

try:
    api_token = st.secrets["predibase"]["PREDIBASE_API_TOKEN"]
    pb = Predibase(api_token=api_token)
except KeyError:
    st.error("API token is missing in secrets.toml. Please make sure it is set correctly.")

# Convert images to base64 for embedding in HTML
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

bot_image_base64 = image_to_base64(os.path.join(os.getcwd(), 'static', 'bot.png'))
profile_image_base64 = image_to_base64(os.path.join(os.getcwd(), 'static', 'profile.png'))

@dataclass
class Message:
    origin: Literal["human", "ai"]
    message: str
    timestamp: str  # New field for timestamp

def load_css():
    with open("static/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "lorax_client" not in st.session_state:
        model_name = "solar-1-mini-chat-240612"
        st.session_state.lorax_client = pb.deployments.client(model_name)

def generate_response(prompt, lorax_client, adapter_id):
    try:
        with spinner_placeholder:
            with st.spinner("AINewbies is thinking..."):
                response = lorax_client.generate(prompt, adapter_id=adapter_id, max_new_tokens=30000)
        return response.generated_text
    except Exception as e:
        print("Error generating response:", e)
        return "Error generating response"

def expand_abbreviations(text):
    abbreviation_dict = {
        "u": "you", "r": "are", "pls": "please", "msg": "message", 
        "btw": "by the way", "lol": "laugh out loud", "rsvp": "please reply", 
        "asap": "as soon as possible", "am": "morning", "pm": "afternoon", 
        "lmk": "let me know", "brb": "be right back", "dob": "date of birth", 
        "cc": "carbon copy", "bcc": "blind carbon copy", "tba": "to be announced", 
        "tbc": "to be confirmed", "eta": "estimated time of arrival", "tgif": "thank God it's Friday", 
        "fomo": "fear of missing out", "imo": "in my opinion", "imho": "in my humble opinion", 
        "n/a": "not available", "aka": "also known as", "diy": "do it yourself", 
        "ty": "thank you", "fyi": "for your information", "idk": "I don't know", 
        "ttyl": "talk to you later", "omg": "oh my God", "smh": "shaking my head", 
        "tmi": "too much information", "yolo": "you only live once", "jk": "just kidding", 
        "tbh": "to be honest", "bff": "best friends forever", "gtg": "got to go", 
        "nvm": "never mind", "idc": "I don't care", "irl": "in real life", 
        "dm": "direct message", "ttys": "talk to you soon"
    }
    words = text.split()
    expanded_text = " ".join([abbreviation_dict.get(word.lower(), word) for word in words])
    return expanded_text

def on_click_callback():
    human_prompt = st.session_state.human_prompt.strip()

    if not human_prompt:
        return

    expanded_prompt = expand_abbreviations(human_prompt)
    new_human_prompt = expanded_prompt.lower().capitalize()

    if not new_human_prompt.endswith(('.', '?', '!')):
        if new_human_prompt.lower().startswith(('who', 'what', 'where', 'when', 'why', 'how', 'whom', 'whose', 'which')):
            new_human_prompt += '?'
        else:
            new_human_prompt += '.'

    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.history.append(Message("human", human_prompt, timestamp))

    lorax_client = st.session_state.lorax_client
    adapter_id = "Uncle_Roger_AINewbiesTourismGPT/5"  # Adapter ID

    llm_response = generate_response(new_human_prompt, lorax_client, adapter_id)
    st.session_state.history.append(Message("ai", llm_response, timestamp))

    st.session_state.human_prompt = ""

def display_chat_history():
    chat_placeholder.empty()
    with chat_placeholder:
        for chat in st.session_state.history:
            if chat.origin == 'human':
                display_human_message(chat.message, chat.timestamp)
            elif chat.origin == 'ai':
                display_bot_message(chat.message, chat.timestamp)

def display_human_message(message, timestamp):
    div = f"""
    <div style="display: flex; align-items: flex-end; justify-content: flex-end; margin-bottom: 10px;">
        <div class="chat-bubble human-bubble" style="background-color: #d7c4fd; padding: 10px; border-radius: 10px; max-width: 70%; margin-right: 10px;margin-top: 10px;">
            &#8203;{message}
            <div style="font-size: 10px; color: #ececec; text-align: right;">{timestamp}</div>
        </div>
        <img src="data:image/png;base64,{profile_image_base64}" style="width: 42px; height: 40px; margin-left: 10px; margin-top: 80px;">
    </div>
    """
    st.markdown(div, unsafe_allow_html=True)

def display_bot_message(message, timestamp):
    div = f"""
    <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
        <img src="data:image/png;base64,{bot_image_base64}" style="width: 42px; height: 60px; margin-right: 10px; margin-top: 10px;">
        <div class="chat-bubble ai-bubble" style="background-color: #f5eaff; padding: 10px; border-radius: 10px; max-width: 70%;">
            &#8203;{message}
            <div style="font-size: 10px; color: #999; text-align: right;">{timestamp}</div>
        </div>
    </div>
    """
    st.markdown(div, unsafe_allow_html=True)

load_css()
initialize_session_state()

st.markdown("<h1 style='text-align: center;'>AINewbies Tourism GPT🗺️⁀જ✈︎</h1>", unsafe_allow_html=True)

st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

chat_placeholder = st.container()

display_chat_history()

with st.form("chat-form"):
    st.markdown('<div class="fixed-chat-form">', unsafe_allow_html=True)
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    cols[0].text_input(
        "Chat",
        value="",
        placeholder="Ask something...",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit", 
        type="primary", 
        on_click=on_click_callback, 
    )
    spinner_placeholder = st.empty()  # Placeholder for spinner
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
    <div class="footer" style="position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; background-color: #f8f9fa; box-shadow: 0 -2px 5px rgba(0,0,0,0.1);">
        <p>&copy; 2024 AINewbies Tourism GPT. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)