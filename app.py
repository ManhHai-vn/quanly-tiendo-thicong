from datetime import datetime
import io
from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G", layout="wide")

@st.cache_resource
def get_bll():
    return BusinessLogicLayer()

try:
    bll = get_bll()
    df_data = bll.get_raw_data()
except Exception as e:
    st.error(f"Lỗi dữ liệu: {e}")
    df_data = pd.DataFrame()

col_dt = "ĐỐI TÁC" if "ĐỐI TÁC" in df_data.columns else "Đối tác"

def count_col_done(dframe, target_cols):
    for col in target_cols:
        if col in dframe.columns:
            s = dframe[col].astype(str).str.strip()
            return len(dframe[(s != "") & (s.str.lower() != "nan") & (s.str.lower() != "none")])
    return 0

if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "username": "", "role": "", "partner_name": ""})

def login_screen():
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Username:").lower()
            pw = st.text_input("Password:", type="password")
            if st.form_submit_button("Đăng Nhập"):
                users = {"admin_agg": {"pass": "admin123", "role": "admin", "partner": "Tất cả"}}
                if user in users and users[user]["pass"] == pw:
                    st.session_state.update({"authenticated": True, "username": user, "role": users[user]["role"], "partner_name": users[user]["partner"]})
                    st.rerun()
                else: st.error("Sai thông tin!")

if not st.session_state["authenticated"]:
    login_screen()
else:
    page = st.sidebar.radio("Chọn trang:", ["🛠️ Cổng Báo cáo", "📊 Trang Quản lý & Dashboard"])
    
    if page == "📊 Trang Quản lý & Dashboard":
        st.title("📊 TRANG QUẢN LÝ & ĐIỀU HÀNH")
        
        with st.expander("📅 Báo cáo tiến độ theo ngày", expanded=True):
            target_date = st.date_input("Chọn ngày:")
            if st.button("Xem báo cáo"):
                st.session_state["show_rep"] = True
                st.session_state["rep_date"] = target_date
            
            if st.session_state.get("show_rep"):
                d_str = st.session_state["rep_date"].strftime("%d/%m/%Y")
                df_day = df_data[df_data.astype(str).apply(lambda x: x.str.contains(d_str)).any(axis=1)]
                
                if not df_day.empty:
                    c1, c2 = st.columns(2)
                    data_exp = {}
                    for idx, dt in enumerate(["VCC", "VTK"]):
                        df_sub = df_day[df_day[col_dt].astype(str).str.upper() == dt]
                        data_exp[dt] = df_sub
                        with (c1 if idx == 0 else c2):
                            st.subheader(f"🏢 Đối tác: {dt}")
                            st.metric("Tổng lắp trong ngày", count_col_done(df_sub, ["Lắp TB 5G", "Lắp đặt 5G"]))
                            st.dataframe(df_sub[["Matram", "Phường xã"]], use_container_width=True, hide_index=True)
                    
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf) as writer:
                        for dt in ["VCC", "VTK"]: data_exp[dt].to_excel(writer, sheet_name=dt, index=False)
                    st.download_button("📥 Tải Báo Cáo Excel", data=buf.getvalue(), file_name=f"BC_{d_str.replace('/','-')}.xlsx", mime="application/vnd.ms-excel")
                else: st.warning("Không có dữ liệu ngày này.")

        # Dashboard tổng quan bên dưới
        st.markdown("---")
        st.dataframe(bll.process_partner_summary(df_data), use_container_width=True)
        if st.button("🔄 Làm mới"): st.rerun()
        st.dataframe(df_data, use_container_width=True)

    else:
        st.write("Cổng báo cáo cá nhân...")
