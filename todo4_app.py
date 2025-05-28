import streamlit as st
import pandas as pd
from datetime import date
import os

# タイトル
st.title("やることリスト（ユーザー別）")

# ユーザー名入力
username = st.text_input("お名前を入力してください（例：taro）")

# ユーザー名が入力された場合のみ続行
if username:
    # ファイル名を定義
    filename = f"{username}_todo_list.csv"

    # 死亡予定日の入力と余命の表示（セッションステートで保持）
    if "death_date" not in st.session_state:
        st.session_state.death_date = date.today()

    st.session_state.death_date = st.date_input("死亡予定日", value=st.session_state.death_date, min_value=date.today())
    remaining_days = (st.session_state.death_date - date.today()).days
    st.markdown(f"🕰 **余命：{remaining_days} 日**")

    # CSV読み込み（空ファイル対策付き）
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=["No", "日付", "タスク", "達成度", "完了"])

    # 入力フォーム（達成度入力は削除）
    with st.form("task_form"):
        task = st.text_input("タスク")
        submitted = st.form_submit_button("新規追加")

        if submitted:
            if len(df) >= 30:
                st.warning("最大30件までです。古いタスクを削除してください。")
            elif task:
                new_task = {
                    "No": len(df) + 1,
                    "日付": date.today().isoformat(),
                    "タスク": task,
                    "達成度": 1,  # デフォルト達成度
                    "完了": False,
                }
                df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
                df["No"] = range(1, len(df) + 1)
                df.to_csv(filename, index=False)
                st.rerun()

    # ✅ 完了タスクの表示切替
    show_completed = st.checkbox("完了タスクを表示する", value=True)

    # 表示と操作
    for i, row in df.iterrows():
        if not show_completed and row["完了"]:
            continue  # 完了タスクを非表示にする

        cols = st.columns([1, 2, 4, 2, 1, 1])
        cols[0].write(int(row["No"]))
        cols[1].write(row["日付"])
        cols[2].write(row["タスク"])

        # 達成度の選択
        current_progress = int(row["達成度"]) if pd.notnull(row["達成度"]) else 1
        new_progress = cols[3].selectbox("達成度", options=[1, 2, 3, 4, 5], index=current_progress - 1, key=f"progress_{i}")
        if new_progress != current_progress:
            df.at[i, "達成度"] = new_progress
            df.to_csv(filename, index=False)

        # 完了チェック
        done = cols[4].checkbox("完了", value=row["完了"], key=f"done_{i}")
        if done != row["完了"]:
            df.at[i, "完了"] = done
            df.to_csv(filename, index=False)

        # 削除ボタン
        delete = cols[5].button("削除", key=f"delete_{i}")
        if delete:
            df = df.drop(index=i).reset_index(drop=True)
            df["No"] = range(1, len(df) + 1)
            df.to_csv(filename, index=False)
            st.rerun()

else:
    st.info("はじめにお名前を入力してください。")