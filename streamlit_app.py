import streamlit as st
from openai import OpenAI

system_message = """
The goal of this is to help user learn Japanese by having a conversation.
Act as a {role} for this entire conversation. 
Use only Japanese vocabulary of {level} level.
For every user input:
1. First repeat the user input in Japanese hiragana/katakana/kanji, Romanji, and English.
2. Then give your response in Japanese hiragana/katakana/kanji, Romanji, and English.

<Example>

<User> 
I want friend chicken!
</User>

<Assistant>
User input:
- フライドチキンが欲しい！
- Furaido chikin ga hoshii!
- I want fried chicken!

Assistant response:
- 何度も言ってるだろうが、それは完売しているんだ！
- Nandomo itteru darou ga, sore wa kanbai shite irunda!
- I've said it multiple times, but that item is sold out!
</Assistant>
</Example>
"""

suggest_question_prompt = """
What would the user say next to continue the conversation below? Do the following:
1. Suggest 5 possible humourous one liner for the user.
2. The suggestion should respond to the last assistant response to continue the conversation.
3. You should now play the role of the user, not the assistant.
Format the output in a dashed list.

<ExampleOutput>
- [first suggestion]
- [second suggestion]
- [third suggestion]
- [forth suggestion]
- [fifth suggestion]
</ExampleOutput>
"""

with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="chatbot_api_key", type="password"
    )
    role = st.selectbox(
        "Select AI role",
        ["angry store manager", "sarcastic high school friend", "funny stranger"],
        index=0,
    )
    level = st.selectbox(
        "Japanese vocabulary level", ["beginner", "intermediate", "advanced"], index=0
    )

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{}]

if "messages" in st.session_state:
    st.session_state["messages"][0] = {
        "role": "system",
        "content": system_message.format(role=role, level=level),
    }

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    st.chat_message(msg["role"]).write(msg["content"])


selected_suggestion = None
if "selected_suggestion" in st.session_state:
    selected_suggestion = st.session_state.selected_suggestion
    st.session_state.selected_suggestion = None

prompt = st.chat_input()
if prompt or selected_suggestion:
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    if selected_suggestion:
        prompt = selected_suggestion
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=st.session_state.messages
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    messages = [
        {"role": "system", "content": suggest_question_prompt.format(role=role)},
        *st.session_state.messages[1:],
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    msg = response.choices[0].message.content
    x = [message.strip("- ") for message in msg.split("\n") if message.strip("- ")]
    st.session_state.suggestions = x

if "suggestions" in st.session_state and st.session_state.suggestions:
    for suggestion in st.session_state.suggestions:
        if not suggestion:
            continue
        if st.button(suggestion):
            st.session_state.selected_suggestion = suggestion
            st.session_state.suggestions = None
            st.rerun()
