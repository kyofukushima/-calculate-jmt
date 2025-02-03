import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import io


# アプリケーションのタイトル
st.title('費用試算')

default_dict = {
    '市民向け':{
        '単価':{
            'シンプル':{
                '新規': 208,
                '更新': 31,
            },
            'フル':{
                '新規': 1042,
                '更新': 625,
            },
        },
        '更新回数':2,
    },
    '事業者向け':{
        '単価':{
            'シンプル':{
                '新規': 417,
                '更新': 250,
            },
            'フル':{
                '新規': 2083,
                '更新': 938,
            },
        },
        '更新回数':2,
    },
    '自治体向け':{
        '単価':{
            'シンプル':{
                '新規': 417,
                '更新': 250,
            },
            'フル':{
                '新規': 2083,
                '更新': 938,
            },
        },
        '更新回数':2,  
    }
    
}

# 数値設定
mode = st.sidebar.radio('ジャンル',default_dict.keys())
st.sidebar.header(mode)
tanka_simple_dict = default_dict[mode]['単価']['シンプル']
initial_price = st.sidebar.number_input('初期単価', min_value=0, value=tanka_simple_dict['新規'])
continuous_price = st.sidebar.number_input('継続単価', min_value=0, value=tanka_simple_dict['更新'])
quantity = st.sidebar.number_input('制度数', min_value=1, value=10)
area_count = st.sidebar.number_input('対象自治体数', min_value=1, value=5)
purchase_frequency = st.sidebar.number_input('更新回数（年）', min_value=1, value=default_dict[mode]['更新回数'])
other_initial_cost = st.sidebar.number_input('その他費用（初期）', min_value=0, value=0)
other_continuous_cost = st.sidebar.number_input('その他費用（更新）', min_value=0, value=0)

# 計算
initial_total = (initial_price * quantity * area_count) + other_initial_cost
continuous_total = ((continuous_price * quantity * area_count) * purchase_frequency) + other_continuous_cost 

# 結果表示
st.header('計算結果')
col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric(label="初期費用",value=f'¥{initial_total}')
# st.write(f'¥{initial_total:,.0f}')
with col2:
    st.metric(label=f"更新費用（年{purchase_frequency}回）",value=f'¥{continuous_total}')
# st.write(f'¥{continuous_total:,.0f}')

# グラフ作成
# st.header('数値の関係性')

# # データフレーム作成
# df = pd.DataFrame({
#     '項目': ['初期単価', '継続単価', '数量', '対象エリア数', '購入回数（年）'],
#     '値': [initial_price, continuous_price, quantity, area_count, purchase_frequency]
# })

# # 棒グラフ
# fig = px.bar(df, x='項目', y='値', title='入力値の比較')
# st.plotly_chart(fig)

# 散布図（数量 vs 対象エリア数）
# st.subheader('数量と対象エリア数の関係')
# fig2 = px.scatter(x=[quantity], y=[area_count], 
#                   labels={'x': '数量', 'y': '対象エリア数'},
#                   title='数量 vs 対象エリア数')
# st.plotly_chart(fig2)

# # 予算内で購入できる数量と対象エリア数の範囲を可視化
# st.header('予算内での購入可能範囲')

# max_budget = st.number_input('最大予算', min_value=0, value=initial_total + continuous_total)

# quantity_range = range(1, 101)
# area_range = range(1, 51)

# heatmap_data = []
# for q in quantity_range:
#     row = []
#     for a in area_range:
#         total_cost = (initial_price * q * a) + ((continuous_price * q * a) * purchase_frequency)
#         row.append(total_cost <= max_budget)
#     heatmap_data.append(row)

# df_heatmap = pd.DataFrame(heatmap_data, index=quantity_range, columns=area_range)

# fig3 = px.imshow(df_heatmap, 
#                  labels=dict(x="対象エリア数", y="数量", color="購入可能"),
#                  title='予算内で購入可能な組み合わせ')
# fig3.update_layout(coloraxis_showscale=False)
# st.plotly_chart(fig3)

# st.caption('緑色の領域が予算内で購入可能な組み合わせを示しています。')

# ユーザー入力
st.sidebar.header('3Dグラフ設定')
budget_dict = {'初期費のみ': initial_price,
               '更新費のみ': continuous_price,
               '初期費+更新費':initial_price+continuous_price,
               }
budget_select = st.sidebar.selectbox('費用',budget_dict.keys())
max_quantity = st.sidebar.number_input('制度数の最大値', min_value=1, max_value=1000, value=100)
max_area = st.sidebar.number_input('導入自治体数の最大値', min_value=1, max_value=1000, value=100)
# unit_price = st.number_input('単価', min_value=100, max_value=10000, value=budget_dict[budget_select])
max_budget = st.sidebar.number_input('最大予算額', min_value=1000, max_value=10000000, value=1000000)

# データ生成（固定）
quantities = range(1, max_quantity + 1)
areas = range(1, max_area + 1)

data = []
for q in quantities:
    for a in areas:
        budget = q * a * budget_dict[budget_select]
        is_over_budget = budget > max_budget
        data.append({'quantity': q, 'area': a, 'budget': budget, 'over_budget': is_over_budget})

df = pd.DataFrame(data)

# 3次元散布図（バブルチャート）の作成
fig = px.scatter_3d(
    df,
    x='quantity',
    y='area',
    z='budget',
    size='budget',
    color='over_budget',
    color_discrete_map={False: 'blue', True: 'red'},
    title='制度数、自治体数、予算額の関係',
    labels={'quantity': '制度数', 'area': '自治体数', 'budget': '予算額', 'over_budget': '予算超過'}
)

# グラフのレイアウト設定
fig.update_layout(width=800, height=600)

st.header('グラフ')
st.write('青色: 予算内, 赤色: 予算超過')
# Streamlitでグラフを表示
st.plotly_chart(fig)

# 凡例の説明
st.write('青色: 予算内, 赤色: 予算超過')

# def change_gif_speed(image, speed_factor):
#     frames = []
#     for frame in range(image.n_frames):
#         image.seek(frame)
#         frames.append(image.copy())
    
#     output = io.BytesIO()
#     frames[0].save(output, format='GIF', append_images=frames[1:],
#                    save_all=True, duration=image.info['duration'] // speed_factor, loop=0)
#     return output.getvalue()

# st.title('GIF再生速度調整')

# uploaded_file = st.file_uploader("GIF画像をアップロードしてください", type="gif")
# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
    
#     speed_factor = st.slider('再生速度', min_value=0.01, max_value=3.0, value=1.0, step=0.01)
    
#     modified_gif = change_gif_speed(image, speed_factor)
#     st.image(modified_gif)
