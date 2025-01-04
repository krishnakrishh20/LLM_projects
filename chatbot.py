import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import(
                        SystemMessagePromptTemplate,
                        HumanMessagePromptTemplate,
                        ChatPromptTemplate,
                        MessagesPlaceholder
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

st.title("Your own chatbot")
st.write("Chat with me")

base_url = 'http://localhost:11434'
model = 'llama3.2:3b'
user_id =  st.text_input('Enter your user_id','Ammu')


def get_session_history(session_id):
    return SQLChatMessageHistory(session_id,"sqlite:///chat_history.db")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if st.button('start a new convo'):
    st.session_state.chat_history = []
    history = get_session_history(user_id)
    history.clear()

for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

llm =ChatOllama(base_url=base_url , model= model)


system = SystemMessagePromptTemplate.from_template("You are a helpful assistant")
human = HumanMessagePromptTemplate.from_template("{input}")
message = [system,MessagesPlaceholder(variable_name='history'),human]
prompt = ChatPromptTemplate(messages = message)
chain = prompt |llm|StrOutputParser()

runnable_with_history =RunnableWithMessageHistory(chain, get_session_history,
                    input_messages_key='input',
                    history_messages_key='history')


def chat_with_llm(session_id, input):
    for output in runnable_with_history.stream({'input':input},config = {'configurable':{'session_id':session_id}}):
        yield output

prompt = st.chat_input('what is up?')
st.write(prompt)

if prompt:
    st.session_state.chat_history.append({'role':'user','content':prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
     

    with st.chat_message("assistant"):
        response = st.write_stream(chat_with_llm(user_id, prompt))
                        
    st.session_state.chat_history.append({'role':'assistant','content':response})