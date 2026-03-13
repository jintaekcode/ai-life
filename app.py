import streamlit as st
import pandas as pd
import os

st.title("PAIOS - AI 생산성 분석")

st.write("PAIOS는 당신의 돈, 시간, 습관을 분석하는 AI 생산성 앱입니다.")

money = st.number_input("오늘 사용한 돈", min_value=0)
study = st.number_input("오늘 공부 시간", min_value=0)
exercise = st.number_input("오늘 운동 시간", min_value=0)

if st.button("기록 저장"):

    score = study*2 + exercise*3 - money*0.01

    new_data = pd.DataFrame({
        "money":[money],
        "study":[study],
        "exercise":[exercise],
        "score":[score]
    })

    if os.path.exists("data.csv"):
        old = pd.read_csv("data.csv")
        new_data = pd.concat([old,new_data])

    new_data.to_csv("data.csv",index=False)

    st.success("기록이 저장되었습니다!")

if os.path.exists("data.csv"):

    df = pd.read_csv("data.csv")

    st.subheader("PAIOS 기록 데이터")
    st.dataframe(df)

    st.subheader("생산성 그래프")
    st.line_chart(df["score"])

    avg = df["score"].mean()

    st.subheader("PAIOS AI 분석")

    if avg > 10:
        st.success("생산성이 매우 높습니다. 현재 루틴을 유지하세요.")
    elif avg > 5:
        st.info("생산성이 평균 수준입니다. 공부 시간을 조금 늘리면 좋습니다.")
    else:
        st.warning("생산성이 낮습니다. 생활 패턴을 조정해보세요.")
