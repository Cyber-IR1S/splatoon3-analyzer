import streamlit as st
import pandas as pd
import os
import datetime # ★日付を扱うためのライブラリを追加

CSV_FILE = "splatoon_battles.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # ★【互換性ケア】過去に入力したデータに「日付」列がない場合、自動で今日の日付を入れてエラーを防ぐ
        if "日付" not in df.columns:
            df["日付"] = str(datetime.date.today())
        return df
    else:
        # 新しく列に「日付」を追加
        return pd.DataFrame(columns=["日付", "ルール", "使用ブキ", "勝敗", "キル数", "デス数", "敗因分類", "詳細理由", "改善案", "次の意識"])

def save_data(new_data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")


# --- ✨ フォント＆デザインの超カスタム ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reggae+One&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], button, select, input, label, p, span {
        font-family: 'Reggae One', system-ui, sans-serif !important;
    }
    
    .splatoon-title {
        color: #E6FF00; 
        text-shadow: 3px 3px 0px #2F195A, -1px -1px 0px #2F195A, 1px -1px 0px #2F195A, -1px 1px 0px #2F195A;
        font-size: 36px; 
        text-align: center; 
        border-bottom: 4px dashed #E6FF00; 
        padding-bottom: 10px;
        margin-bottom: 25px;
        line-height: 1.3; 
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<div class="splatoon-title">🦑 SPLATOON 3<br>戦績・反省分析ツール</div>', unsafe_allow_html=True)

battle_df = load_data()

# --- サイドバー：データ入力 ---
st.sidebar.markdown("<h2 style='color: #E6FF00;'>【試合データの入力】</h2>", unsafe_allow_html=True)

# ★【新機能】カレンダーから日付を選択（標準は今日の日付）
match_date = st.sidebar.date_input("試合日", datetime.date.today())

rule = st.sidebar.selectbox("ルール", ["ガチエリア", "ガチヤグラ", "ガチホコ", "ガチアサリ", "ナワバリバトル"])
weapon = st.sidebar.text_input("使用ブキ", value="スプラシューター")
result = st.sidebar.radio("勝敗", ["WIN", "LOSE"], horizontal=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    kills = st.number_input("キル数", min_value=0, value=5)
with col2:
    deaths = st.number_input("デス数", min_value=0, value=4)

lose_reason_type = "-"
lose_reason = ""
improvement = ""
next_mindset = ""

if result == "LOSE":
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color: #FF3B30;'>❌ 負けの分析</h3>", unsafe_allow_html=True)
    lose_reason_type = st.sidebar.selectbox(
        "主な敗因の分類", 
        ["デスが多すぎた", "カウント・関与不足", "打開で焦って単騎突撃した", "味方との連携ミス", "相手のウルトラショット等にやられた", "その他"]
    )
    lose_reason = st.sidebar.text_area("具体的な負け理由（詳細）")
    improvement = st.sidebar.text_area("どうすれば良かったか（改善案）")
    next_mindset = st.sidebar.text_area("🔥 次の試合で意識すること")

if st.sidebar.button("この戦績を記録する"):
    new_battle = {
        "日付": str(match_date), # ★日付を文字列にして保存
        "ルール": rule, "使用ブキ": weapon, "勝敗": result, "キル数": kills, "デス数": deaths,
        "敗因分類": lose_reason_type, "詳細理由": lose_reason, "改善案": improvement, "次の意識": next_mindset
    }
    save_data(new_battle)
    st.sidebar.success("CSVファイルにデータを保存しました！")
    st.rerun()


# --- メイン画面：分析と次へのアクション ---
st.markdown("<h3 style='color: #E6FF00;'>📋 今回の試合結果 & ネクストアクション</h3>", unsafe_allow_html=True)

if result == "WIN":
    st.success(f"🎉 【WIN】{rule}（ブキ: {weapon}） | {kills}キル / {deaths}デス")
else:
    st.error(f"😢 【LOSE】{rule}（ブキ: {weapon}） | {kills}キル / {deaths}デス")
    st.markdown("### 🔍 敗因と次への約束")
    st.warning(f"**【分類】** {lose_reason_type}\n\n**【具体的な理由】**\n{lose_reason if lose_reason else '未入力'}")
    st.info(f"💡 **【改善案】**\n{improvement if improvement else '未入力'}")
    st.success(f"🎯 **【次の試合で意識すること！】**\n{next_mindset if next_mindset else '未入力'}")


# --- 📊 リアルタイムデータ分析エリア ---
st.markdown("---")
st.markdown("<h3 style='color: #E6FF00;'>📊 実際の戦績データ分析</h3>", unsafe_allow_html=True)

if not battle_df.empty:
    total_matches = len(battle_df)
    win_matches = len(battle_df[battle_df["勝敗"] == "WIN"])
    win_rate = (win_matches / total_matches) * 100
    
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric("総試合数", f"{total_matches} 試合")
    with metrics_col2:
        st.metric("トータル勝率", f"{win_rate:.1f} %")
        
    # 分析グラフを横並びにするためのレイアウト調整
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.markdown("#### 🔹 ルール別の勝率")
        summary_rule = battle_df.groupby(["ルール", "勝敗"]).size().unstack(fill_value=0)
        if "WIN" not in summary_rule.columns: summary_rule["WIN"] = 0
        if "LOSE" not in summary_rule.columns: summary_rule["LOSE"] = 0
        summary_rule["勝率(%)"] = (summary_rule["WIN"] / (summary_rule["WIN"] + summary_rule["LOSE"])) * 100
        st.bar_chart(summary_rule["勝率(%)"])
        
    with graph_col2:
        # ★【新機能】ブキ別の勝率グラフ
        st.markdown("#### 🔹 ブキ別の勝率")
        summary_weapon = battle_df.groupby(["使用ブキ", "勝敗"]).size().unstack(fill_value=0)
        if "WIN" not in summary_weapon.columns: summary_weapon["WIN"] = 0
        if "LOSE" not in summary_weapon.columns: summary_weapon["LOSE"] = 0
        summary_weapon["勝率(%)"] = (summary_weapon["WIN"] / (summary_weapon["WIN"] + summary_weapon["LOSE"])) * 100
        st.bar_chart(summary_weapon["勝率(%)"])
        
    # ★【新機能】日付別のプレイ数（活動量の可視化）
    st.markdown("#### 📈 日付別のプレイ数（活動量）")
    date_counts = battle_df.groupby("日付").size().reset_index(name="試合数")
    st.line_chart(date_counts.set_index("日付"))
    
    st.markdown("#### 🔹 過去の戦績一覧（最新5試合）")
    # 表示する列の順番をきれいに整理
    display_df = battle_df[["日付", "ルール", "使用ブキ", "勝敗", "キル数", "デス数", "敗因分類"]]
    st.dataframe(display_df.tail(5))
else:
    st.info("まだ戦績データがありません。左側のサイドバーから最初の1試合を記録してみましょう！")