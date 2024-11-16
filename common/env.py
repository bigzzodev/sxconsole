import os
import streamlit as st

# ---------------------------------------------------------------------------------------
def int_env():
    # https://python.langchain.com/docs/expression_language/interface
    if 'openai_api_key' in st.secrets:
        global openai_api_key
        global pinecone_api_key
        openai_api_key = st.secrets.openai_api_key
        pinecone_api_key = st.secrets.pinecone_api_key
        os.environ["LANGCHAIN_API_KEY"] = st.secrets.langchain_api_key
        # # 데이터베이스 정보 가져오기
        # db_user = st.secrets["database"]["user"]
        # db_password = st.secrets["database"]["password"]
        # db_host = st.secrets["database"]["host"]
        # db_port = st.secrets["database"]["port"]
    else:
        st.info('Enter an OpenAI API Key to continue')
        st.stop()

# ---------------------------------------------------------------------------------------
def langsmith(_project_name=None):
    os.environ["LANGCHAIN_ENDPOINT"] = ("https://api.smith.langchain.com")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = _project_name