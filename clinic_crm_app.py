import streamlit as st
import pandas as pd

# データ読み込み
df = pd.read_excel(
    "眼科クリニックリスト実働表（東京都）sub.xlsx",
    sheet_name="【原本】東京都訪問リスト "
)

# 市区町村の抽出関数
def extract_city(address):
    if pd.isna(address):
        return "その他"
    if "区" in address:
        return address.split("区")[0] + "区"
    if "市" in address:
        return address.split("市")[0] + "市"
    return "その他"

df["市区町村"] = df["住所1"].apply(extract_city)

# 絞り込み UI
col1, col2 = st.columns([2, 3])
with col1:
    selected_city = st.selectbox(
        "市区町村で絞り込み",
        ["すべて"] + sorted(df["市区町村"].dropna().unique())
    )
with col2:
    search = st.text_input("医院名で検索")

# フィルタリング
filtered = df
if selected_city != "すべて":
    filtered = filtered[filtered["市区町村"] == selected_city]
if search:
    filtered = filtered[filtered["クリニック名"]\
        .str.contains(search, na=False)]

# 件数表示
st.write(f"全体件数：{len(df)} 件　｜　抽出件数：{len(filtered)} 件")

# クリニック選択
clinics = filtered["クリニック名"].dropna().unique()
selected = st.selectbox("クリニックを選択", clinics)
idx = filtered[filtered["クリニック名"] == selected].index[0]
data = df.loc[idx]

# 情報表示（２列レイアウト）
b1, b2 = st.columns(2)

with b1:
    st.markdown("### 📍 基本情報")
    st.markdown(
        f"- **住所**：{data['住所1']} {data['住所2']}\n"
        f"- **郵便番号**：{data['〒']}\n"
        f"- **HP**：[{data['HP']}]({data['HP']})\n"
        f"- **ドクター**：{data['氏名']} ({data['肩書']})"
    )

    st.markdown("### 🗂️ 分類・提携状況")
    st.markdown(
        f"- **CL処方**：{data['CL処方']}\n"
        f"- **CL提携**：{data['CL提携先']}（{data['CL提携先名']}）\n"
        f"- **KB提携**：{data['KB提携先']}（{data['KB提携先名']}）"
    )

with b2:
    st.markdown("### 📷 訪問記録・写真")
    st.markdown(
        f"- **訪問可能時間**：{data['アポイント・面談可能時間']}\n"
        f"- **写真ファイル名**：{data['写真']}"
    )

    st.markdown("### 📝 備考・ステータス")
    new_note = st.text_area("備考・メモ", value=data["備考"] or "")
    new_status = st.selectbox(
        "ステータス",
        ["未訪問", "訪問済み", "アポ取得", "契約済み", "保留"],
        index=0
    )
    if st.button("💾 保存"):
        df.at[idx, "備考"] = new_note
        df.at[idx, "ステータス"] = new_status
        df.to_excel(
            "眼科クリニックリスト実働表（東京都）sub.xlsx",
            sheet_name="【原本】東京都訪問リスト ",
            index=False
        )
        st.success("保存しました！")

