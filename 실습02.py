import streamlit as st
import openai
import os
import pandas as pd
import random
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI

# API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# 추천용 데이터 불러오기
df_games = pd.read_csv('boardgames.csv')
# df_cafes = pd.read_csv('cafes.csv')  # 당분간 제외

# RAG 챗봇용 데이터 불러오기
df_gameinfo = pd.read_csv('gameinfo.csv')
# df_cafeinfo = pd.read_csv('cafeinfo.csv')  # 당분간 제외

# 초기 상태 설정
def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant", 
                                         "content": "안녕하세요! 주어진 문서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!"}]

# 벡터스토어 생성
def get_vectorstore(text_chunks):
    # Document 객체로 텍스트 청크 변환
    documents = [Document(page_content=chunk) for chunk in text_chunks]

    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectordb = FAISS.from_documents(documents, embeddings)
    return vectordb

# 대화 체인 생성
def get_conversation_chain(vetorestore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)
    
    # ConversationBufferWindowMemory 설정 (최근 4개의 대화 기억)
    memory = ConversationBufferWindowMemory(memory_key="chat_history", k=4)
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type="stuff", 
        retriever=vetorestore.as_retriever(search_type='mmr', verbose=True), 
        memory=memory,
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain

# 보드게임 추천 함수
def show_recommended_games(genre):
    filtered_games = df_games[df_games['장르'].str.contains(genre, na=False)]['게임 이름'].tolist()
    random.shuffle(filtered_games)
    return filtered_games[:5]

# 메인 함수
def main():
    init_session_state()

    st.title("보드게임 추천 시스템")
    st.subheader("원하시는 서비스를 선택하세요:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎲 보드게임 추천"):
            st.session_state.service = 'game_recommendation'
    with col2:
        pass  # 카페 추천 관련 부분 임시 제거
    with col3:
        if st.button("🧚 보드게임 요정에게 질문하기"):
            st.session_state.service = 'chat_with_fairy'

    if 'service' in st.session_state:
        if st.session_state.service == 'game_recommendation':
            st.subheader("어떠한 장르의 보드게임을 찾으시나요?")
            genre = st.selectbox("장르 선택", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
            if genre:
                st.write("다음 보드게임들을 추천합니다:")
                games = show_recommended_games(genre)
                for game in games:
                    st.write(f"- {game}")

        elif st.session_state.service == 'chat_with_fairy':
            st.subheader("보드게임 요정에게 질문하기")

            # 대화 체인 설정
            if st.session_state.conversation is None:
                # 필요한 텍스트 청크를 문서화
                text_chunks = df_gameinfo['보드게임간략소개'].tolist()  # df_cafeinfo 부분 제외
                vetorestore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vetorestore, os.getenv("OPENAI_API_KEY"))

            # 사용자 질문 입력 및 대화
            if query := st.chat_input("질문을 입력해주세요."):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

                with st.chat_message("assistant"):
                    chain = st.session_state.conversation

                    with st.spinner("Thinking..."):
                        result = chain({"question": query})
                        st.session_state.chat_history = result['chat_history']
                        response = result['answer']
                        source_documents = result['source_documents']
                        st.markdown(response)

if __name__ == "__main__":
    main()


