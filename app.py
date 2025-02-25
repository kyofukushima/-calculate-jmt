import streamlit as st
import pandas as pd
import numpy as np
import datetime, re
import time
import plotly.express as px
from PIL import Image
import io
from io import BytesIO

# 関数の設定
# 

def authenticate(password):
    if str(st.secrets['SALES']['pass']) == str(password):
        st.sidebar.success('認証成功')
        return True
    else:
        st.sidebar.error('認証失敗')
        return False

# アプリケーションのタイトル
st.title('費用試算')

# 設定
if 'sales_mode' not in st.session_state:
    # st.write('初期値の設定')
    st.session_state['sales_mode'] = False


# st.write(st.session_state['sales_mode'])

# サイドバーコンテナの設定
container1 = st.sidebar.container()
# 数値設定
container1.header('予算の設定')
max_budget = container1.number_input('予算額（¥）', min_value=1000, max_value=10000000, value=1000000)
container1.header('コンテンツの設定')
mode = container1.radio('ジャンル',['市民向け','事業者向け','自治体向け'])
# container1.header()


# パスワード認証の処理
sales_on = st.sidebar.toggle("営業部専用設定")
if sales_on:
    p_word = st.sidebar.text_input('パスワードを入力', type='password')
    if p_word:
        st.session_state['sales_mode'] = authenticate(p_word)

# st.write(st.session_state['sales_mode'])
# tanka_simple_dict = default_dict[mode]['単価']['シンプル']

## 営業部専用項目の設定
tanka_simple_dict = st.secrets[mode]['単価']['シンプル']
profit_rate = st.secrets['SALES']['利益率']
if st.session_state['sales_mode'] == True:
     initial_price = st.sidebar.number_input('初期単価（¥）', min_value=0.0, value=tanka_simple_dict['新規'])
     continuous_price = st.sidebar.number_input('継続単価（¥）', min_value=0.0, value=tanka_simple_dict['更新'])
     profit_rate = st.sidebar.number_input('利益率', min_value=0.0, value=st.secrets['SALES']['利益率'])

else:
    initial_price = tanka_simple_dict['新規']
    continuous_price = tanka_simple_dict['更新']



quantity = container1.number_input('制度数', min_value=1, value=10)
area_count = container1.number_input('対象自治体数', min_value=1, value=5)
purchase_frequency = container1.number_input('更新回数（年）', min_value=0, value=st.secrets[mode]['更新回数'])
container1.header('その他費用の設定')
container1.subheader('追加費用')
other_initial_cost = container1.number_input('初期費用（¥）', min_value=0.0, value=0.0)
other_continuous_cost = container1.number_input('更新費用（¥）', min_value=0.0, value=0.0)

# 計算
## 初期費
initial_total = (initial_price * quantity * area_count) + other_initial_cost
## 初期費（利益率上乗せ）
selling_initial_total = initial_total / (1-profit_rate)
## 更新費
continuous_total = ((continuous_price * quantity * area_count) * purchase_frequency) + other_continuous_cost 
## 更新費（利益率上乗せ）
selling_continuous_total = continuous_total / (1-profit_rate)
## 合計額
selling_all = selling_initial_total+selling_continuous_total
## 合計額と予算の差分
diff_selling_all_budget = max_budget - selling_all

# 結果表示
st.header('計算結果')
with st.container(border=True):
    st.subheader('合計額')
    metric_help_text = '合計額の下に、予算との差分額を表示します'
    def total_metric(delta_color):
        st.metric(f'初期費用＋更新費用（年{purchase_frequency}回）',
                value=f'¥{selling_all:,.0f}',
                delta=f'¥{diff_selling_all_budget:,.0f}',
                delta_color=delta_color,
                help=metric_help_text,
                )
    if diff_selling_all_budget > 0:
        total_metric('normal')
    elif diff_selling_all_budget < 0:
        total_metric('inverse')
    else:
        total_metric('off')
col1, col2 = st.columns(2,border=True)
with col1:
    st.subheader('初期費用')
    st.metric(f'見積価格',f'¥{selling_initial_total:,.0f}')
    if st.session_state['sales_mode'] == True:
        st.metric(f'社内原価',f'¥{initial_total:,.0f}')

with col2:
    st.subheader(f'更新費用（年{purchase_frequency}回）')
    st.metric(f'見積価格',f'¥{selling_continuous_total:,.0f}')
    if st.session_state['sales_mode'] == True:
        st.metric(f'社内原価',f'¥{continuous_total:,.0f}')

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
container1.header('3Dグラフ設定')
budget_dict = {'初期費のみ': initial_price,
               '更新費のみ': continuous_price,
               '初期費+更新費':initial_price+continuous_price,
               }
budget_select = container1.selectbox('費用',budget_dict.keys())
max_quantity = container1.number_input('制度数の最大値', min_value=1, max_value=1000, value=100)
max_area = container1.number_input('導入自治体数の最大値', min_value=1, max_value=1000, value=100)
# unit_price = st.number_input('単価', min_value=100, max_value=10000, value=budget_dict[budget_select])
# max_budget = container1.number_input('予算額', min_value=1000, max_value=10000000, value=1000000)

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
# Streamlitでグラフを表示
st.plotly_chart(fig)
# 凡例の説明
st.write('青色: 予算内, 赤色: 予算超過')

st.header('メモ')
st.write('一番右の「備考」列のみ編集可')

# セッション状態の初期化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        '予算額': [],
        'ジャンル': [],
        '制度数': [],
        '自治体数': [],
        '追加費用_初期':[],
        '初期費用':[],
        '更新回数':[],
        '追加費用_更新':[],
        '更新費用': [],
        '合計額': [],
        '備考':[],
    })


# 入力フィールドの作成


# 「今の設定を追加」ボタン
if st.button('今の設定を追加'):
    new_row = pd.DataFrame({
        '予算額': [max_budget],
        'ジャンル': [mode],
        '制度数': [quantity],
        '自治体数': [area_count],
        '追加費用_初期':[other_initial_cost],
        '初期費用':[selling_initial_total],
        '更新回数':[purchase_frequency],
        '追加費用_更新':[other_continuous_cost],
        '更新費用': [selling_continuous_total],
        '合計額': [selling_all],
        '備考':['なし'],
    })
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

# 編集可能な表の表示
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        '予算額': {"editable": False},
        'ジャンル': {"editable": False},
        '制度数': {"editable": False},
        '自治体数': {"editable": False},
        '追加費用_初期':{"editable": False},
        '初期費用':{"editable": False},
        '更新回数':{"editable": False},
        '追加費用_更新':{"editable": False},
        '更新費用':{"editable": False},
        '合計額':{"editable": False},
    }
)

# 編集された表をセッション状態に保存
st.session_state.df = edited_df

# ダウンロード設定
now = datetime.datetime.now().strftime('%Y%m%d')
edited_df.to_csv(buf := BytesIO(), index=False,encoding='utf-8-sig',date_format="%Y/%m/%d %H:%M:%S")


st.download_button(
        "csvのダウンロード",buf.getvalue(),f"ジモトク試算_{now}.csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

edited_df.to_excel(buf := BytesIO(), index=False,na_rep='')
st.download_button(
    "エクセルのダウンロード",
    buf.getvalue(),
    f"ジモトク試算_{now}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
