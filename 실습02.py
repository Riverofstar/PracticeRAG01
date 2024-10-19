#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import random
from loguru import logger
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS

# 보드게임 CSV 파일에서 데이터 로드 함수
def load_boardgames_data(filepath):
    loader = CSVLoader(filepath)
    documents = loader.load_and_split()
    return documents

# 보드게임 카페 CSV 파일에서 데이터 로드 함수
def load_cafes_data(filepath):
    loader = CSVLoader(filepath)
    documents = loader.load_and_split()
    return documents

# 문서를 청크로 나누는 함수
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(text)
    return chunks

# FAISS 벡터 스토어 생성 함수
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectordb = FAISS.from_documents(text_chunks, embeddings)
    return vectordb

# 대화 체인 생성 함수
def get_conversation_chain(vetorestore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type="stuff", 
        retriever=vetorestore.as_retriever(search_type='mmr', verbose=True), 
        memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer'),
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain

# Streamlit 앱 메인 함수
def main():
    st.set_page_config(page_title="보드게임 RAG 챗봇", page_icon="🎲")

    st.title("보드게임 RAG 챗봇")

    # 초기화 상태
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None

    # 사이드바에서 파일 업로드 및 API 키 입력
    with st.sidebar:
        uploaded_files = st.file_uploader("보드게임 및 카페 CSV 파일을 업로드하세요", type=['csv'], accept_multiple_files=True)
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        process = st.button("Process")

    # 파일 업로드 후 처리
    if process:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        # 보드게임 및 카페 데이터 로드
        for file in uploaded_files:
            if 'boardgames' in file.name:
                files_text = load_boardgames_data(file)
                text_chunks = get_text_chunks(files_text)
                boardgame_vetorestore = get_vectorstore(text_chunks)
            elif 'cafes' in file.name:
                files_text = load_cafes_data(file)
                text_chunks = get_text_chunks(files_text)
                cafe_vetorestore = get_vectorstore(text_chunks)

        st.session_state.conversation = get_conversation_chain(boardgame_vetorestore, openai_api_key)
        st.session_state.processComplete = True

    # 보드게임 또는 카페 추천 선택지
    option = st.selectbox("무엇을 원하시나요?", ("보드게임 추천", "보드게임 카페 추천"))

    # 보드게임 추천 기능
    if option == "보드게임 추천":
        st.write("보드게임 추천을 받으려면 아래 장르를 선택하세요.")
        genre = st.radio("어떠한 장르를 찾으시나요?", ["마피아", "순발력", "파티", "전략", "추리", "협력"])

        if genre and st.session_state.conversation:
            query = f"{genre} 장르의 보드게임 추천해줘"
            result = st.session_state.conversation({"question": query})
            st.write(f"추천하는 {genre} 장르 보드게임:")
            for game in result['answer']:
                st.write(game)

    # 보드게임 카페 추천 기능
    elif option == "보드게임 카페 추천":
        st.write("보드게임 카페 추천을 받으려면 아래 지역을 선택하세요.")
        location = st.radio("어디에서 하실 예정인가요?", ["홍대", "신촌", "건대입구", "이수", "강남역", "부천"])

        if location and st.session_state.conversation:
            query = f"{location}에 있는 보드게임 카페 추천해줘"
            result = st.session_state.conversation({"question": query})
            st.write(f"추천하는 {location}의 보드게임 카페:")
            for cafe in result['answer']:
                st.write(cafe)

    # 사용자 질문 처리
    if query := st.text_input("챗봇에게 질문해보세요."):
        if st.session_state.conversation:
            st.write(f"'{query}'에 대한 답변을 찾고 있습니다...")
            result = st.session_state.conversation({"question": query})
            st.write(result['answer'])

if __name__ == '__main__':
    main()

