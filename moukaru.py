import streamlit as st

# サイドバーの要素
st.sidebar.title("①希望条件を入れてください")
selected_districts = st.sidebar.multiselect("東京23区から選択", ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区","品川区", "渋谷区", "目黒区", "大田区", "世田谷区", "練馬区", "杉並区", "豊島区", "北区", "板橋区","足立区", "荒川区", "江戸川区", "葛飾区"])
walk_distance = st.sidebar.slider("駅からの徒歩距離（分）", 0, 30, (0, 30))
age_range = st.sidebar.slider("築年数（年）", 0, 50, (0, 50))
layout_types = st.sidebar.multiselect("間取り", ["ワンルーム", "1K", "1DK", "1LDK" , "2K" ,"2DK" ,"2LDK", "3K", "3DK","3LDK","4K","4DK","4LDK以上"])
price_range = st.sidebar.slider("金額（万円）", 0, 2000, (0, 20000), step=500)

# メインセクション
st.title("マンション買うなら儲かるくん")
# chuko_mansionのデータを10個出力する処理
chuko_mansion_data = get_chuko_mansion_data()  # Assuming there is a function called get_chuko_mansion_data() that retrieves the data
for data in chuko_mansion_data[:10]:
    st.write(data)

# 地図上に出力したデータの位置情報を表示する処理
for data in chuko_mansion_data[:10]:
    st.write(data["location"])
# 物件選択と詳細情報表示の処理
selected_property = st.selectbox("物件を選択してください", chuko_mansion_data)
if selected_property:
    st.write("詳細情報")
    st.write(selected_property)
# 頭金、ローン期間、金利の選択と元金均等返済の毎月返済額表示の処理
down_payment = st.number_input("頭金（万円）", min_value=0, max_value=1000, value=0, step=10)
loan_term = st.number_input("ローン期間（年）", min_value=1, max_value=30, value=20, step=1)
interest_rate = st.number_input("金利（%）", min_value=0.0, max_value=10.0, value=2.0, step=0.1)

loan_amount = selected_property["price"] - down_payment
monthly_interest_rate = interest_rate / 100 / 12
num_payments = loan_term * 12

monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments / ((1 + monthly_interest_rate) ** num_payments - 1)

st.write("毎月の返済額：", round(monthly_payment, 2), "万円")
# chintai_mansionのデータベースから住所が近いものを5個出力する処理
chintai_mansion_data = get_chintai_mansion_data()  # Assuming there is a function called get_chintai_mansion_data() that retrieves the data
nearby_properties = find_nearby_properties(chintai_mansion_data, selected_property["location"], 5)  # Assuming there is a function called find_nearby_properties() that finds nearby properties
for property in nearby_properties:
    st.write(property)
# 賃貸価格と専有面積から専有面積あたりの金額を表示する処理
# 専有面積あたりの金額平均にchuko_mansionで選んだ物件の専有面積をかけて「想定賃料」を表示する処理

# サブタイトル「不動産の資産価値」
# キャッシュフローと利回りの計算と表示の処理
