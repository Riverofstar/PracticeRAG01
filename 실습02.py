#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import streamlit as st
import random
import pandas as pd

# 보드게임과 카페 데이터를 불러옵니다
df_games = pd.read_csv('boardgames.csv')
df_cafes = pd.read_csv('cafes.csv')

# 스타일 추가
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f0;
        font-family: 'Arial', sans-serif;
    }
    .title {
        color: #4CAF50;
        font-size: 2.5em;
        text-align: center;
    }
    .subheader {
        font-size: 1.5em;
        color: #333;
    }
    .button {
        font-size: 1.2em;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    .button:hover {
        background-color: #45a049;
    }
    .arrow {
        font-size: 1.5em;
        color: #007BFF;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def show_recommended_games(genre):
    filtered_games = df_games[df_games['장르'].str.contains(genre)]['게임 이름'].tolist()
    random.shuffle(filtered_games)
    return filtered_games[:5]

def show_recommended_cafes(location):
    # 선택한 지역에 맞는 카페 필터링
    filtered_cafes = df_cafes[df_cafes['지역'].str.contains(location)]
    if filtered_cafes.empty:
        return []  # 카페가 없을 경우 빈 리스트 반환
    random.shuffle(filtered_cafes)  # 카페 목록을 랜덤으로 섞음
    return filtered_cafes  # DataFrame 반환

def main():
    st.title("보드게임 추천 시스템")

    st.subheader("원하시는 서비스를 선택하세요:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎲 보드게임 추천"):
            st.session_state.service = 'game_recommendation'
    with col2:
        if st.button("🏠 보드게임 카페 추천"):
            st.session_state.service = 'cafe_recommendation'
    with col3:
        if st.button("🧚‍♀️ 보드게임 요정과 대화하기"):
            st.session_state.service = 'fairy_chat'

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
                if cafes:  # 카페가 존재할 경우에만 출력
                    for index, row in cafes.iterrows():
                        st.write(f"- {row['카페 이름']} (방문자리뷰: {row['방문자리뷰수']}) ")
                        st.markdown(f'<a class="arrow" href="{row["네이버지도주소"]}" target="_blank">➡️</a>', unsafe_allow_html=True)
                else:
                    st.write("해당 지역에 카페가 없습니다.")

        elif st.session_state.service == 'fairy_chat':
            # 요정과 대화하는 부분 추가
            st.subheader("보드게임 요정에게 질문하세요:")
            query = st.text_input("질문을 입력하세요", key="query")
            if st.button("전송", key="send_question"):
                st.session_state.query = query
                st.session_state.query = ""  # 질문을 보낸 후 입력창 비우기
                # 요정과 대화 로직 추가 필요

if __name__ == "__main__":
    main()
