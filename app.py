import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="基金实时盈亏计算器", layout="wide")

# -----------------------------
# 初始化
# -----------------------------
if "funds" not in st.session_state:
    st.session_state.funds = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

# -----------------------------
# 获取真实基金数据（akshare）
# -----------------------------
def get_fund_price(code):
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        latest = df.iloc[-1]
        price = float(latest["单位净值"])
        pct = float(latest["日增长率"].replace("%", ""))
        name = df["基金简称"].iloc[0]
        return name, price, pct
    except:
        return "未知基金", 0, 0

# -----------------------------
# 标题
# -----------------------------
st.title("基金实时盈亏计算器（API稳定版）")
st.caption("数据来源：akshare | 手动刷新，不自动请求")

# -----------------------------
# 添加基金
# -----------------------------
col1, col2, col3 = st.columns([3,2,1])
with col1:
    fund_code = st.text_input("基金代码", placeholder="例如：012349")
with col2:
    fund_amount = st.number_input("持仓金额（元）", min_value=1, value=1000)
with col3:
    if st.button("➕ 添加基金"):
        if fund_code:
            name, price, pct = get_fund_price(fund_code)
            st.session_state.funds[fund_code] = {
                "代码": fund_code,
                "名称": name,
                "持仓金额": fund_amount,
                "当前价格": price,
                "涨跌幅": pct,
            }

st.divider()

# -----------------------------
# 刷新按钮
# -----------------------------
if st.button("🔄 手动刷新全部行情"):
    for code in st.session_state.funds:
        name, price, pct = get_fund_price(code)
        st.session_state.funds[code]["当前价格"] = price
        st.session_state.funds[code]["涨跌幅"] = pct
    st.session_state.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 显示刷新时间
if st.session_state.last_refresh:
    st.info(f"最后刷新时间：{st.session_state.last_refresh}")

# -----------------------------
# 表格
# -----------------------------
rows = []
total_amount = 0
total_profit = 0

for code, info in st.session_state.funds.items():
    amount = info["持仓金额"]
    pct = info["涨跌幅"]
    profit = round(amount * pct / 100, 2)

    total_amount += amount
    total_profit += profit

    rows.append([
        info["代码"],
        info["名称"],
        amount,
        info["当前价格"],
        f"{pct}%",
        profit
    ])

df = pd.DataFrame(rows, columns=[
    "基金代码", "基金名称", "持仓金额", "当前净值", "涨跌幅", "当日盈亏"
])

if not df.empty:
    st.dataframe(df, use_container_width=True)

# -----------------------------
# 底部统计
# -----------------------------
st.divider()
c1, c2 = st.columns(2)
c1.metric("总持仓金额", f"¥{total_amount:,.0f}")
c2.metric("当日总盈亏", f"¥{total_profit:,.2f}")
