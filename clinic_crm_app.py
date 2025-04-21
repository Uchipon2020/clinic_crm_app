import streamlit as st
import pandas as pd

# データ読み込み（仮：ローカルExcelファイル）
df = pd.read_excel("眼科クリニックリスト実働表（東京都）sub.xlsx", sheet_name="【原本】東京都訪問リスト ")

# 区を抽出する関数
def extract_city(address):
    if pd.isna(address):
        return "その他"
    if "区" in address:
        return address.split("区")[0] + "区"
    if "市" in address:
        return address.split("市")[0] + "市"
    return "その他"

# 区分の追加
df["市区町村"] = df["住所1"].apply(extract_city)
city_options = sorted(df["市区町村"].dropna().unique())
selected_city = st.selectbox("市区町村で絞り込み：", ["すべて"] + city_options)

# フィルタリング
filtered_df = df.copy()
if selected_city != "すべて":
    filtered_df = filtered_df[filtered_df["市区町村"] == selected_city]

# 検索バー
search = st.text_input("医院名で検索：")
if search:
    filtered_df = filtered_df[filtered_df["クリニック名"].str.contains(search, na=False)]

# 統計表示
st.markdown(f"**全体件数：{len(df)} 件　｜　抽出件数：{len(filtered_df)} 件**")

# クリニック名の選択
doctors = filtered_df["クリニック名"].dropna().unique()
selected_clinic = st.selectbox("クリニックを選択", doctors)

# 選択されたクリニックの情報を取得
clinic_index = filtered_df[filtered_df["クリニック名"] == selected_clinic].index[0]
clinic_data = df.loc[clinic_index]

st.markdown("""
<style>
.card {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.title(f"🩺 {selected_clinic} のカルテ")

st.subheader("📍 基本情報")
st.markdown(f"**住所：** {clinic_data['住所1']} {clinic_data['住所2']}")
st.markdown(f"**HP：** [{clinic_data['HP']}]({clinic_data['HP']})")
st.markdown(f"**ドクター：** {clinic_data['氏名']} ({clinic_data['肩書']})")
st.markdown(f"**郵便番号：** {clinic_data['〒']}")

st.subheader("🗂️ 分類・提携状況")
st.markdown(f"**コンタクト処方：** {clinic_data['CL処方']}")
st.markdown(f"**CL提携先：** {clinic_data['CL提携先']}（{clinic_data['CL提携先名']}）")
st.markdown(f"**KB提携先：** {clinic_data['KB提携先']}（{clinic_data['KB提携先名']}）")

st.subheader("📷 訪問記録・写真")
st.markdown(f"**訪問可能時間：** {clinic_data['アポイント・面談可能時間']}")
st.markdown(f"**写真ファイル名：** {clinic_data['写真']}")

st.subheader("📝 備考・メモ 入力")
new_note = st.text_area("備考を書き込む", value=clinic_data["備考"] if pd.notna(clinic_data["備考"]) else "")

st.subheader("🔄 ステータス変更")
status_options = ["未訪問", "訪問済み", "アポ取得", "契約済み", "保留"]
new_status = st.selectbox("現在のステータスを選択", status_options, index=0)

if st.button("変更を保存"):
    df.at[clinic_index, "備考"] = new_note
    df.at[clinic_index, "ステータス"] = new_status
    df.to_excel("眼科クリニックリスト実働表（東京都）sub.xlsx", sheet_name="【原本】東京都訪問リスト ", index=False)
    st.success("変更を保存しました！")

    # ダウンロードボタン
    with open("眼科クリニックリスト実働表（東京都）sub.xlsx", "rb") as file:
        st.download_button(
            label="📥 最新Excelファイルをダウンロード",
            data=file,
            file_name="最新_眼科クリニックリスト.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("</div>", unsafe_allow_html=True)
