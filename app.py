import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# DB 연결
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# 테이블 생성
c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS records(
username TEXT,
date TEXT,
money REAL,
study REAL,
exercise REAL,
score REAL
)""")

conn.commit()

st.title("🚀 PAIOS - AI 생산성 분석")

menu = ["로그인","회원가입"]
choice = st.sidebar.selectbox("메뉴",menu)

# 회원가입
if choice == "회원가입":

    st.subheader("회원가입")

    new_user = st.text_input("아이디")
    new_pass = st.text_input("비밀번호", type="password")

    if st.button("가입"):

        c.execute("INSERT INTO users VALUES (?,?)",(new_user,new_pass))
        conn.commit()

        st.success("회원가입 완료")

# 로그인
if choice == "로그인":

    st.subheader("로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):

        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        result = c.fetchone()

        if result:

            st.success("로그인 성공")

            st.header("오늘 데이터 입력")

            money = st.number_input("오늘 사용한 돈",min_value=0)
            study = st.number_input("오늘 공부 시간",min_value=0)
            exercise = st.number_input("오늘 운동 시간",min_value=0)

            if st.button("기록 저장"):

                score = study*2 + exercise*3 - money*0.01
                today = datetime.now().strftime("%Y-%m-%d")

                c.execute("INSERT INTO records VALUES (?,?,?,?,?,?)",
                          (username,today,money,study,exercise,score))
                conn.commit()

                st.success("데이터 저장 완료")

            st.subheader("나의 기록")

            df = pd.read_sql_query(
                f"SELECT * FROM records WHERE username='{username}'",
                conn
            )

            if len(df)>0:

                st.dataframe(df)

                st.subheader("생산성 그래프")
                st.line_chart(df["score"])

                avg = df["score"].mean()

                st.subheader("AI 분석")

                if avg > 12:
                    st.success("최근 생산성이 매우 높습니다.")
                elif avg > 7:
                    st.info("평균적인 생산성입니다.")
                else:
                    st.warning("생산성이 낮습니다.")

        else:
            st.error("로그인 실패")

