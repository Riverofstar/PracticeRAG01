#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import streamlit as st
import random
import pandas as pd

# 보드게임과 카페 데이터를 불러옵니다
df_games = pd.read_csv('boardgames.csv')
df_cafes = pd.read_csv('cafes.csv')

def show_recommended_games(genre):
    # 선택한 장르에 맞는 보드게임 필터링 (포함)
    filtered_games = df_games[df_games['장르'].str.contains(genre, na=False)]['게임 이름'].tolist()

    random.shuffle(filtered_games)  # 게임 목록을 랜덤으로 섞음
    return filtered_games[:5]  # 상위 5개의 게임만 반환

def show_recommended_cafes(location):
    # 선택한 지역에 맞는 카페 필터링 (포함)
    filtered_cafes = df_cafes[df_cafes['지역'].str.contains(location, na=False)]['카페 이름'].tolist()
    random.shuffle(filtered_cafes)  # 카페 목록을 랜덤으로 섞음
    return filtered_cafes[:5]  # 상위 5개의 카페만 반환

def main():
    st.title("보드게임 추천 시스템")

    # 첫 번째 선택지: 보드게임 추천과 보드게임 카페 추천
    st.subheader("원하시는 서비스를 선택하세요:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎲 보드게임 추천"):
            st.session_state.service = 'game_recommendation'
    with col2:
        if st.button("🏠 보드게임 카페 추천"):
            st.session_state.service = 'cafe_recommendation'
    with col3:
        if st.button("🧚 보드게임 요정과 대화하기"):
            st.session_state.service = 'chat_with_fairy'

    # 사용자가 선택한 서비스에 따라 다음 단계로 이동
    if 'service' in st.session_state:
        if st.session_state.service == 'game_recommendation':
            st.subheader("어떠한 장르의 보드게임을 찾으시나요?")
            genre = st.selectbox("장르 선택", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
            if genre:
                st.write("다음 보드게임들을 추천합니다:")
                games = show_recommended_games(genre)
                for game in games:
                    st.write(f"- {game}")

        elif st.session_state.service == 'cafe_recommendation':
            st.subheader("어디에서 하실 예정인가요?")
            location = st.selectbox("지역 선택", ['홍대', '신촌', '건대입구', '이수', '강남역', '부천'])
            if location:
                st.write("다음 카페들을 추천합니다:")
                cafes = show_recommended_cafes(location)
                for cafe in cafes:
                    st.write(f"- {cafe}")

        elif st.session_state.service == 'chat_with_fairy':
            if 'query' not in st.session_state:
                st.session_state.query = ""
            if 'conversation_history' not in st.session_state:
                st.session_state.conversation_history = []

            st.subheader("보드게임 요정과 대화하기")
            user_input = st.text_input("질문을 입력하세요:", value=st.session_state.query)
            if st.button("질문하기") or st.session_state.query and st.session_state.query.strip():
                st.session_state.conversation_history.append({"user": st.session_state.query})
                # 요정에게 질문 보내기 로직 추가 (예: OpenAI API 호출)
                response = "여기에 요정의 답변이 들어갑니다."  # 예시 응답
                st.session_state.conversation_history.append({"fairy": response})
                st.session_state.query = ""  # 질문을 보낸 후 입력창 비우기

            # 대화 기록 표시
            for entry in st.session_state.conversation_history:
                if 'user' in entry:
                    st.write(f"💬 사용자: {entry['user']}")
                if 'fairy' in entry:
                    st.write(f"🧚 요정: {entry['fairy']}")

if __name__ == "__main__":
    main()


