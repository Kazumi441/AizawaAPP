import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

# セッション状態を初期化
if 'user_input' not in st.session_state:
    st.session_state.user_input = {
        'selected_districts': [],
        'walk_distance': (0, 30),
        'age_range': (0, 50),
        'layout_types': [],
        'price_range': (0, 20000)
    }

def main():
    st.title("マンション買うなら儲かるくん")
    st.sidebar.title("希望条件を入れてください")

    # サイドバーの要素
    selected_districts = st.sidebar.multiselect("東京23区から選択", ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区","品川区", "渋谷区", "目黒区", "大田区", "世田谷区", "練馬区", "杉並区", "豊島区", "北区", "板橋区","足立区", "荒川区", "江戸川区", "葛飾区"])
    walk_distance = st.sidebar.slider("駅からの徒歩距離（分）", 0, 30, (0, 30))
    age_range = st.sidebar.slider("築年数（年）", 0, 50, (0, 50))
    layout_types = st.sidebar.multiselect("間取り", ["ワンルーム", "1K", "1DK", "1LDK" , "2K" ,"2DK" ,"2LDK", "3K", "3DK","3LDK","4K","4DK","4LDK以上"])
    price_range = st.sidebar.slider("金額（万円）", 0, 2000, (0, 20000), step=500)

    # ユーザーの入力をセッション状態に保存
    st.session_state.user_input = {
        'selected_districts': selected_districts,
        'walk_distance': walk_distance,
        'age_range': age_range,
        'layout_types': layout_types,
        'price_range': price_range
    }
    # セッション状態からデータを取得
    user_input = st.session_state.user_input
    selected_districts = user_input['selected_districts']
    walk_distance = user_input['walk_distance']
    age_range = user_input['age_range']
    layout_types = user_input['layout_types']
    price_range = user_input['price_range']

    # 検索ボタンを追加
    search_button = st.sidebar.button("検索")

    if search_button:
        # データベースに接続
        conn = sqlite3.connect("scraping/chuko_database.db")
        cursor = conn.cursor()

        # SQLクエリを作成して物件情報を抽出
        query = """
            SELECT name, location_parts, price_range, layout_types, age_range, walk_distance
            FROM chuko_table
            WHERE selected_districts IN ({})
                AND walk_distance BETWEEN ? AND ?
                AND age_range BETWEEN ? AND ?
                AND layout_types IN ({})
                AND price_range BETWEEN ? AND ?
        """.format(", ".join(["?"] * len(selected_districts)), ", ".join(["?"] * len(layout_types)))

        # パラメータを設定
        params = (
            *selected_districts,
            walk_distance[0], walk_distance[1],
            age_range[0], age_range[1],
            *layout_types,
            price_range[0], price_range[1]
        )

        # クエリを実行して結果をDataFrameに格納
        df_chuko = pd.read_sql_query(query, conn, params=params)


        # データベース接続を閉じる
        conn.close()

        # 物件情報を表示
        st.write("物件情報:")
        property_names = df_chuko['name'].tolist()
        selected_property = st.selectbox("物件を選択", property_names, key="property_selection")
        selected_property_info = df_chuko[df_chuko['name'] == selected_property].iloc[0]


        # 選択した物件情報を再度表示
        if not selected_property_info.empty:
            st.write("選択した物件情報:")
            st.write(f"物件名: {selected_property_info['name']}, 所在地: {selected_property_info['location_parts']}, 価格: {selected_property_info['price_range']}万円, 間取り: {selected_property_info['layout_types']}, 築年数: {selected_property_info['age_range']}年, 徒歩距離: {selected_property_info['walk_distance']}分")


if __name__ == "__main__":
    main()
