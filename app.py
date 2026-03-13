import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

client = OpenAI()

# -----------------------------
# 설정
# -----------------------------

st.set_page_config(page_title="PAIOS", page_icon="🚀")

openai.api_key = "YOUR_OPENAI_API_KEY"

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

# -----------------------------
# DB 생성
# -----------------------------

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT,
plan TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS records(
username TEXT,
date TEXT,
money REAL,
study REAL,
exercise REAL,
score REAL
)
""")

conn.commit()

# -----------------------------
# 함수
# -----------------------------

def ai_analysis(df):

    data = df.tail(7).to_dict()

    prompt = f"""
    사용자의 생산성 데이터를 분석하고
    생활 패턴 개선 조언을 해줘

    데이터:
    {data}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    return response.choices[0].message.content


def weekly_report(username):

    df = pd.read_sql_query(
        f"SELECT * FROM records WHERE username='{username}'",
        conn
    )

    if len(df)==0:
        return None

    last_week = datetime.now() - timedelta(days=7)

    df["date"] = pd.to_datetime(df["date"])

    week = df[df["date"] > last_week]

    return week


# -----------------------------
# UI
# -----------------------------

st.title("🚀 PAIOS - AI 생산성 SaaS")

menu = ["로그인","회원가입","구독"]

choice = st.sidebar.selectbox("메뉴",menu)

# -----------------------------
# 회원가입
# -----------------------------

if choice=="회원가입":

    st.subheader("회원가입")

    new_user = st.text_input("아이디")
    new_pass = st.text_input("비밀번호",type="password")

    if st.button("가입"):

        c.execute(
            "INSERT INTO users VALUES (?,?,?)",
            (new_user,new_pass,"free")
        )

        conn.commit()

        st.success("회원가입 완료")

# -----------------------------
# 로그인
# -----------------------------

if choice=="로그인":

    st.subheader("로그인")

    username = st.text_input("아이디")
    password = st.text_input("비밀번호",type="password")

    if st.button("로그인"):

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()

        if user:

            st.success("로그인 성공")

            st.header("오늘 데이터 입력")

            money = st.number_input("오늘 지출",min_value=0)
            study = st.number_input("공부 시간",min_value=0)
            exercise = st.number_input("운동 시간",min_value=0)

            if st.button("기록 저장"):

                score = study*2 + exercise*3 - money*0.01

                today = datetime.now().strftime("%Y-%m-%d")

                c.execute(
                    "INSERT INTO records VALUES (?,?,?,?,?,?)",
                    (username,today,money,study,exercise,score)
                )

                conn.commit()

                st.success("기록 저장 완료")

            df = pd.read_sql_query(
                f"SELECT * FROM records WHERE username='{username}'",
                conn
            )

            if len(df)>0:

                st.subheader("생산성 그래프")

                st.line_chart(df["score"])

                avg = df["score"].mean()

                st.write("평균 생산성:",round(avg,2))

if st.button("AI 분석"):

    avg_money = df["money"].mean()
    avg_study = df["study"].mean()

    st.write("AI 분석 결과")

    st.write("평균 지출:", avg_money)
    st.write("평균 공부시간:", avg_study)

    if avg_money > 50000:
        st.warning("지출이 높은 편입니다.")
    else:
        st.success("지출 관리가 잘 되고 있습니다.")
                st.subheader("주간 리포트")

                week = weekly_report(username)

                if week is not None:

                    st.dataframe(week)

                    st.bar_chart(week["score"])

        else:

            st.error("로그인 실패")

# -----------------------------
# 구독
# -----------------------------

if choice=="구독":

    st.subheader("PAIOS PRO")

    st.write("""
    월 9.9$
    - AI 분석
    - 주간 리포트
    - 생산성 코치
    """)

    st.write("결제는 Stripe 연동 필요")





