import os
import streamlit as st
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import folium
from streamlit_folium import folium_static

# 環境変数の読み込み
load_dotenv()

# データベースファイルのパスを環境変数から取得
DATABASE_PATH = os.getenv("DATABASE_PATH", "/Users/amacha_air/biz×Tech/copy_aizawa/scraping/chuko_database.db")

# データベースからデータを読み込む関数
def load_data_from_database(districts, walk, age, layouts, price):
    conn = sqlite3.connect(DATABASE_PATH)
    query = """
    SELECT * FROM chuko_table 
    WHERE selected_districts IN ({}) 
    AND walk_distance BETWEEN ? AND ? 
    AND age_range BETWEEN ? AND ? 
    AND layout_types IN ({}) 
    AND price_range BETWEEN ? AND ?
""".format(','.join('?'*len(districts)), ','.join('?'*len(layouts)))


    params = districts + [walk[0], walk[1], age[0], age[1]] + layouts + [price[0], price[1]]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# 地図を作成し、マーカーを追加する関数
def create_map(df):
    center = [df['latitude'].mean(), df['longitude'].mean()]
    m = folium.Map(location=center, zoom_start=12)
    for idx, row in df.iterrows():
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"<b>名称:</b> {row['name']}<br><b>家賃:</b> {row['price']}万円<br><a href='{row['detail_url']}' target='_blank'>物件詳細</a>",
        ).add_to(m)
    return m

# メインのアプリケーション関数
def main():
    st.title("マンション買うなら儲かるくん")
    st.sidebar.title("希望条件を入れてください")

    districts = st.sidebar.multiselect("東京23区から選択", ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "渋谷区", "目黒区", "大田区", "世田谷区", "練馬区", "杉並区", "豊島区", "北区", "板橋区", "足立区", "荒川区", "江戸川区", "葛飾区"])
    walk = st.sidebar.slider("駅からの徒歩距離（分）", 0, 30, (5, 15))
    age = st.sidebar.slider("築年数（年）", 0, 50, (10, 30))
    layouts = st.sidebar.multiselect("間取り", ["1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK", "4K", "4DK", "4LDK以上"])
    price = st.sidebar.slider("金額（万円）", 100, 2000, (500, 1500), 100)

    if st.sidebar.button("検索"):
        df = load_data_from_database(districts, walk, age, layouts, price)
        if not df.empty:
            st.success("物件情報の取得が完了しました。")
            map_ = create_map(df)
            folium_static(map_)
            show_all_option = st.radio("表示オプションを選択してください:", ['地図上の検索物件のみ', 'すべての検索物件'])
            if show_all_option == 'すべての検索物件':
                st.dataframe(df)  # 全データを表示
        else:
            st.error("条件に合う物件が見つかりませんでした。")

if __name__ == "__main__":
    main()
