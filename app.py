import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# ----------------------
# DB 연결
# ----------------------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT,
email TEXT
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

# ----------------------
# AI 분석 함수
# ----------------------
def ai_daily_report(money, study, exercise):
    score = study*2 + exercise*3 - money*0.01
    grade = "C"
    if score > 15:
        grade = "A"
    elif score > 8:
        grade = "B"
    advice = ""
    if money > 50000:
        advice += "지출이 높은 편입니다. 소비를 줄이면 생산성이 올라갑니다.\n"
    if study < 2:
        advice += "공부 시간이 부족합니다. 최소 2시간 이상 추천합니다.\n"
    if exercise == 0:
        advice += "운동이 없었습니다. 운동은 생산성에 큰 영향을 줍니다.\n"
    if advice == "":
        advice = "현재 루틴이 매우 좋습니다. 계속 유지하세요."
    return score, grade, advice

def weekly_report(username):
    df = pd.read_sql_query(f"SELECT * FROM records WHERE username='{username}'", conn)
    if len(df) == 0:
        return None
    df["date"] = pd.to_datetime(df["date"])
    week = df[df["date"] > datetime.now()-timedelta(days=7)]
    if len(week) == 0:
        return None
    avg_score = week["score"].mean()
    avg_money = week["money"].mean()
    report = f"""
이번 주 분석
평균 생산성 점수 : {round(avg_score,2)}
평균 지출 : {round(avg_money,0)}

패턴 분석
"""
    if avg_money > 40000:
        report += "- 소비가 높은 편입니다.\n"
    if avg_score < 8:
        report += "- 생산성이 낮은 주입니다.\n"
    else:
        report += "- 생산성이 안정적인 주입니다.\n"
    report += "\n추천\n"
    report += "- 오전 집중 시간 확보\n- 불필요한 소비 줄이기\n- 주 3회 운동"
    return report

# ----------------------
# 이메일 발송 함수
# ----------------------
def send_email(to_email, report):
    from_email = "your_email@gmail.com"   # ← 실제 Gmail 계정
    password = "앱비밀번호"               # ← Gmail 앱 비밀번호
    msg = MIMEText(report)
    msg["Subject"] = "PAIOS 주간 리포트"
    msg["From"] = from_email
    msg["To"] = to_email
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(from_email,password)
    server.sendmail(from_email,to_email,msg.as_string())
    server.quit()

# ----------------------
# UI
# ----------------------
st.title("🚀 PAIOS - AI 생산성 분석 서비스")

menu = ["로그인","회원가입"]
choice = st.sidebar.selectbox("메뉴",menu)

# ----------------------
# 회원가입
# ----------------------
if choice == "회원가입":
    st.subheader("회원가입")
    new_user = st.text_input("아이디")
    new_pass = st.text_input("비밀번호",type="password")
    new_email = st.text_input("이메일")
    if st.button("가입"):
        c.execute("INSERT INTO users VALUES (?,?,?)",(new_user,new_pass,new_email))
        conn.commit()
        st.success("회원가입 완료")

# ----------------------
# 로그인
# ----------------------
if choice == "로그인":
    st.subheader("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호",type="password")
    if st.button("로그인"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        if user:
            st.success("로그인 성공")
            st.header("오늘 기록")
            money = st.number_input("오늘 지출",min_value=0)
            study = st.number_input("공부 시간",min_value=0)
            exercise = st.number_input("운동 시간",min_value=0)

            if st.button("기록 저장"):
                score, grade, advice = ai_daily_report(money,study,exercise)
                today = datetime.now().strftime("%Y-%m-%d")
                c.execute("INSERT INTO records VALUES (?,?,?,?,?,?)",(username,today,money,study,exercise,score))
                conn.commit()
                st.success("기록 저장 완료")
                st.subheader("AI 하루 리포트")
                st.write("생산성 점수:",round(score,2))
                st.write("등급:",grade)
                st.write(advice)

            df = pd.read_sql_query(f"SELECT * FROM records WHERE username='{username}'",conn)
            if len(df) > 0:
                st.subheader("나의 생산성 그래프")
                st.line_chart(df["score"])
                st.subheader("주간 AI 리포트")
                report = weekly_report(username)
                if report:
                    st.write(report)
                    st.subheader("📧 이메일로 리포트 받기")
                    email = user[2]
                    if st.button("이메일 전송"):
                        send_email(email,report)
                        st.success("이메일 전송 완료")

            st.subheader("💳 유료 구독 (PRO)")
            st.markdown("""
[PAIOS PRO 구독 - 월 9,900원](https://buy.stripe.com/test_link_here)
""")
        else:
            st.error("로그인 실패")





