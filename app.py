import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="基金实时估值盈亏系统", layout="wide")

if "funds" not in st.session_state:
    st.session_state.funds = []
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

# 实时估值接口
def get_fund_estimate(code):
    try:
        df = ak.fund_value_estimation_em()
        row = df[df["基金代码"] == code].iloc[0]
        name = row["基金简称"]
        estimate = float(row["估算净值"])
        pct = float(row["估算涨跌幅"].replace("%", ""))
        time = row["估值时间"]
        return name, estimate, pct, time
    except:
        return "未知基金", 0, 0, ""

st.title("基金实时估值盈亏系统（新浪级数据源）")
st.caption("盘中估值 | 数据源：东方财富 / 新浪财经体系")

# 输入
c1,c2,c3,c4 = st.columns([2,2,2,1])
with c1:
    code = st.text_input("基金代码")
with c2:
    share = st.number_input("持仓份额", value=1000.0)
with c3:
    cost = st.number_input("成本价", value=1.0)
with c4:
    if st.button("➕ 添加"):
        name, est, pct, time = get_fund_estimate(code)
        st.session_state.funds.append({
            "代码": code,
            "名称": name,
            "份额": share,
            "成本价": cost,
            "估值": est,
            "涨跌幅": pct,
            "时间": time
        })

st.divider()

# 手动刷新
if st.button("🔄 手动刷新估值"):
    for f in st.session_state.funds:
        name, est, pct, time = get_fund_estimate(f["代码"])
        f["估值"] = est
        f["涨跌幅"] = pct
        f["时间"] = time
        f["名称"] = name
    st.session_state.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if st.session_state.last_refresh:
    st.info(f"最后刷新时间：{st.session_state.last_refresh}")

# 计算
rows = []
total_cost = 0
total_value = 0

for f in st.session_state.funds:
    cost_value = f["份额"] * f["成本价"]
    now_value = f["份额"] * f["估值"]
    profit = now_value - cost_value
    rate = profit / cost_value * 100 if cost_value else 0

    total_cost += cost_value
    total_value += now_value

    rows.append([
        f["代码"], f["名称"], f["份额"], f["成本价"],
        f["估值"], f"{f['涨跌幅']}%",
        round(now_value,2), round(profit,2), f"{round(rate,2)}%",
        f["时间"]
    ])

df = pd.DataFrame(rows, columns=[
    "代码","名称","份额","成本价",
    "实时估值","估值涨跌幅",
    "当前市值","浮动盈亏","收益率","估值时间"
])

st.dataframe(df, use_container_width=True)

st.divider()
a,b,c = st.columns(3)
a.metric("总成本", f"¥{round(total_cost,2)}")
b.metric("当前总市值", f"¥{round(total_value,2)}")
c.metric("总盈亏", f"¥{round(total_value-total_cost,2)}")
