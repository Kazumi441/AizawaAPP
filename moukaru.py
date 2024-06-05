import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from scraping.Haversine_Distance import haversine 
from scraping.calculate_amortized import calculate_amortized_payment

# 画像ファイルのパスを指定
image_path = "header.png"

# ヘッダー画像を表示
st.image(image_path)

# カスタムCSSを適用
st.markdown("""
<style>
.stImage > img {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

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

        # SQLクエリを作成してすべてのカラムを含む物件情報を抽出
        query = """
            SELECT *
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
        
        # サブタイトル
        st.subheader("購入物件の検索")

        # 物件情報を表示
        st.write("物件情報:")
        st.dataframe(df_chuko)

        # 緯度と経度からPointオブジェクトを作成
        geometry = gpd.points_from_xy(df_chuko['longitude'], df_chuko['latitude'])

        # GeoDataFrameを作成
        gdf_chuko = gpd.GeoDataFrame(df_chuko, geometry=geometry, crs='EPSG:4326')

        # 地図上へのマッピング
        st.subheader("地図上にマッピング")
        st.map(gdf_chuko)

        st.session_state.property_names = df_chuko['name'].tolist()
        st.session_state.selected_property = st.selectbox("物件を選択", st.session_state.property_names, key="property_selection")
        # 選択した物件情報をセッション状態に保存
        if st.session_state.selected_property:
            st.session_state.selected_property_info = df_chuko[df_chuko['name'] == st.session_state.selected_property].iloc[0]

        # セッション状態から物件情報を取得
        st.session_state.selected_property_info = st.session_state.get("selected_property_info", pd.Series())

        # 選択した物件情報を再度表示
        if not st.session_state.selected_property_info.empty:
            st.write("選択した物件情報:")
            st.write(f"物件名: {st.session_state.selected_property_info['name']}, 所在地: {st.session_state.selected_property_info['location_parts']}, 価格: {st.session_state.selected_property_info['price_range']}万円, 間取り: {st.session_state.selected_property_info['layout_types']}, 築年数: {st.session_state.selected_property_info['age_range']}年, 徒歩距離: {st.session_state.selected_property_info['walk_distance']}分")
            st.write(f"緯度: {st.session_state.selected_property_info['latitude']}, 経度: {st.session_state.selected_property_info['longitude']}")

        # ユーザーが選んだ物件情報の緯度と経度を取得
        if st.session_state.selected_property:
            st.session_state.selected_property_info = df_chuko[df_chuko['name'] == st.session_state.selected_property].iloc[0]
            selected_latitude = st.session_state.selected_property_info['latitude']
            selected_longitude = st.session_state.selected_property_info['longitude']
        else:
            # 物件が選択されていない場合の処理を追加（例: デフォルトの緯度・経度を設定するなど）
            # この部分を適切に設定してください
            pass
        # サブタイトル
        st.subheader("ローンシミュレーション")
        # ユーザーが選んだ物件情報の価格を取得し、万円単位に変換
        if st.session_state.selected_property:
            principal = st.session_state.selected_property_info['price_range'] * 10000
        else:
            # 物件が選択されていない場合の処理を追加（例: デフォルトの価格を設定するなど）
            principal = 0.0
        interest_rate = st.slider("金利 (%)", min_value=0.1, max_value=5.0, value=0.6, step=0.1)
        loan_term = st.slider("融資期間 (年)", min_value=10, max_value=40, value=35, step=1)

        monthly_payment = calculate_amortized_payment(principal, interest_rate, loan_term)
        st.write(f"月々の支払額: {monthly_payment:.2f} 円")

        # 水平の線を入れる
        st.divider()

        # サブタイトル
        st.subheader("賃貸物件にする場合")

        # データベースに接続
        conn_chintai = sqlite3.connect("scraping/chintai_database.db")
        cursor = conn_chintai.cursor()

        # chintai_databaseからすべての物件情報を取得
        df_chintai = pd.read_sql_query("SELECT * FROM my_table", conn_chintai)

        # Haversine Distance を計算して物件の距離を追加
        df_chintai["distance"] = df_chintai.apply(lambda row: haversine(selected_latitude, selected_longitude, row['latitude'], row['longitude']), axis=1)

        # 距離でソートして上位5件を選択
        df_chintai_sorted = df_chintai.sort_values(by="distance").head(5)

        # 物件情報を表示
        st.write("近くの物件情報:")
        st.dataframe(df_chintai_sorted[["物件名", "所在地", "交通", "賃料", "専有面積", "間取り"]])

        # データベース接続を閉じる
        conn_chintai.close()

        # 選んだ物件の賃料と専有面積を取得
        selected_rent = df_chintai_sorted.iloc[0]["賃料"]
        selected_area = df_chintai_sorted.iloc[0]["専有面積"]

        # st.session_state.selected_property の area を数値に変換
        selected_property_area = float(st.session_state.selected_property_info["area"])

        # 想定賃料を計算
        expected_rent = (selected_rent / selected_area) * selected_property_area

        # 結果を表示
        st.write(f"想定賃料：{expected_rent:.2f}円")

        # 水平の線を入れる
        st.divider()

        # サブタイトル
        st.subheader("資産運用物件としての評価")
        # 月々の収支を計算
        monthly_profit = expected_rent - monthly_payment

        # 結果を表示
        st.write(f"月々の収支：{monthly_profit:.2f}円")
        # 選択した物件の価格帯を取得
        selected_price_range = st.session_state.selected_property_info['price_range']

        # 物件利回り（表面）を計算
        property_yield = (expected_rent * 12) / (selected_price_range * 10000)

        # 結果を表示（フォントサイズを大きくするためにst.markdownを使用）
        st.markdown(f"<span style='font-size: 1.2em;'>物件利回り（表面）：{property_yield:.1%}</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
