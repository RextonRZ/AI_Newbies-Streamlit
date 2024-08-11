from predibase import Predibase
pb = Predibase(api_token="PREDIBASE_API_KEY")
import streamlit as st
import streamlit.components.v1 as components
import os
import base64
from dataclasses import dataclass
from typing import Literal


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


bot_image_base64 = image_to_base64(os.path.join(os.getcwd(), 'static', 'bot.png'))
profile_image_base64 = image_to_base64(os.path.join(os.getcwd(), 'static', 'profile.png'))

@dataclass
class Message:
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/style.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "lorax_client" not in st.session_state:
    
        model_name = "solar-1-mini-chat-240612"
        
    
        st.session_state.lorax_client = pb.deployments.client(model_name)

def generate_response(prompt, lorax_client):
    try:
        response = lorax_client.generate(prompt, max_new_tokens=1000)
        return response.generated_text
    except Exception as e:
        print("Error generating response:", e)
        return "Error generating response"

def on_click_callback():
    human_prompt = st.session_state.human_prompt
    if not human_prompt.strip():  
        return  

    lorax_client = st.session_state.lorax_client

    llm_response = generate_response(human_prompt, lorax_client)

    st.session_state.history.append(
        Message("human", human_prompt)
    )
    st.session_state.history.append(
        Message("ai", llm_response)
    )

    st.session_state.human_prompt = ""
    
load_css()
initialize_session_state()

st.title("AINewbies Tourism GPT🗺️⁀જ✈︎")

chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

with chat_placeholder:
    for chat in st.session_state.history:
        if chat.origin == 'ai':
            div = f"""
            <div class="dropDown" style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <img src="data:image/png;base64,{bot_image_base64}" style="width: 42px; height: 60px; margin-right: 10px; margin-top: 10px;">
                <div class="chat-bubble ai-bubble" style="background-color: #f5eaff; padding: 10px; border-radius: 10px; max-width: 70%;">
                    &#8203;{chat.message}
                </div>
            </div>
            """
        else:
            div = f"""
            <div class="dropDown" style="display: flex; align-items: flex-end; justify-content: flex-end; margin-bottom: 10px;">
                <div class="chat-bubble human-bubble" style="background-color: #d7c4fd; padding: 10px; border-radius: 10px; max-width: 70%; margin-right: 10px;">
                    &#8203;{chat.message}
                </div>
                <img src="data:image/png;base64,{profile_image_base64}" style="width: 42px; height: 40px; margin-left: 10px; margin-top: 80px;">
            </div>
            """
        st.markdown(div, unsafe_allow_html=True)
    
    for _ in range(3):
        st.markdown("")

with prompt_placeholder:
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

credit_card_placeholder.caption(f"""
Used {st.session_state.token_count} tokens \n
""")

components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""", 
    height=0,
    width=0,
)
