#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import random

# CSV 파일을 로드하는 함수
def load_data():
    boardgames = pd.read_csv('boardgames.csv')  # 보드게임 데이터
    cafes = pd.read_csv('cafes.csv')  # 카페 데이터
    return boardgames, cafes

# 추천 보드게임을 반환하는 함수
def recommend_boardgame(genre, boardgames):
    filtered_games = boardgames[boardgames['Genre'] == genre]
    recommended_games = random.sample(filtered_games['Name'].tolist(), 3)  # 3개 랜덤 추천
    return recommended_games  # 리스트로 반환

# 추천 카페를 반환하는 함수
def recommend_cafe(location, cafes):
    filtered_cafes = cafes[cafes['Location'] == location]
    recommended_cafes = random.sample(filtered_cafes['Name'].tolist(), 3)  # 3개 랜덤 추천
    return recommended_cafes  # 리스트로 반환

# Streamlit 앱의 메인 함수
def main():
    st.title("보드게임 추천 챗봇")

    boardgames, cafes = load_data()

    # 사용자에게 선택지를 먼저 보여줌
    st.markdown(
        """
        <style>
        .button-box {
            display: flex;
            justify-content: space-around;
        }
        .custom-button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 30px;
            text-align: center;
            font-size: 16px;
            border-radius: 8px;
            margin: 10px;
            width: 45%;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="button-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # 큰 버튼 UI 추가
    with col1:
        if st.markdown('<a href="#"><div class="custom-button">보드게임 추천</div></a>', unsafe_allow_html=True):
            choice = "보드게임 추천"
    with col2:
        if st.markdown('<a href="#"><div class="custom-button">보드게임 카페 추천</div></a>', unsafe_allow_html=True):
            choice = "보드게임 카페 추천"

    # 사용자의 선택에 따라 다음 질문 표시
    if choice == "보드게임 추천":
        genre = st.selectbox("어떤 장르를 찾으시나요?", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
        if st.button("추천 받기"):
            recommended_games = recommend_boardgame(genre, boardgames)
            st.write("추천 보드게임:")
            for game in recommended_games:
                st.write(f"- {game}")  # 한 줄씩 출력

    elif choice == "보드게임 카페 추천":
        location = st.selectbox("어디에서 하실 예정인가요?", ['홍대', '신촌', '건대입구', '이수', '강남역', '부천'])
        if st.button("추천 받기"):
            recommended_cafes = recommend_cafe(location, cafes)
            st.write("추천 보드게임 카페:")
            for cafe in recommended_cafes:
                st.write(f"- {cafe}")  # 한 줄씩 출력

if __name__ == "__main__":
    main()




