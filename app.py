from datetime import datetime
import io
from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G - Phân quyền", layout="wide")

@st.cache_resource
def get_bll():
    return BusinessLogicLayer()

try:
    bll = get_bll()
    df_data = bll.get_raw_data()
except Exception as e:
    st.error(f"Lỗi khởi tạo dữ liệu: {e}")
    df_data = pd.DataFrame()

col_dt = None
if not df_data.empty:
    for c in ["ĐỐI TÁC", "Đối tác", "doi_tac"]:
        if c in df_data.columns:
            col_dt = c
            break
    if not col_dt and len(df_data.columns) > 5:
        col_dt = df_data.columns[5]

def count_col_done(dframe, target_cols):
    for col_name in target_cols:
        if col_name in dframe.columns:
            s = dframe[col_name].astype(str).str.strip()
            return len(dframe[(s != "") & (s.str.lower() != "nan") & (s.str.lower() != "none")])
    return 0

if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "username": "", "role": "", "partner_name": ""})

def login_screen():
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ 5G")
    st.markdown("---")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập (Username):").lower()
            password = st.text_input("Mật khẩu (Password):", type="password")
            if st.form_submit_button("Đăng Nhập", use_container_width=True):
                users_db = {
                    "admin_agg": {"pass": "admin123", "role": "admin", "partner": "Tất cả"},
                    "vtk": {"pass": "vtk123", "role": "partner", "partner": "VTK"},
                    "vcc": {"pass": "vcc123", "role": "partner", "partner": "VCC"},
                }
                if username in users_db and users_db[username]["pass"] == password:
                    st.session_state.update({"authenticated": True, "username": username, "role": users_db[username]["role"], "partner_name": users_db[username]["partner"]})
                    st.rerun()
                else: st.error("Sai tên đăng nhập hoặc mật khẩu!")

if not st.session_state["authenticated"]:
    login_screen()
else:
    current_role = st.session_state["role"]
    current_partner = st.session_state["partner_name"]
    st.sidebar.title("📌 HỆ THỐNG 5G (BETA)")
    st.sidebar.info(f"👤 Đang đăng nhập: **{st.session_state['username'].upper()}**\n\n🏢 Quyền hạn: **{'Admin Hệ thống' if current_role == 'admin' else 'Nhà thầu ' + current_partner}**")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.update({"authenticated": False, "username": "", "role": "", "partner_name": ""})
        st.rerun()

    menu_options = ["🛠️ 1. Cổng Báo cáo Tiến độ", "📊 2. Trang Quản lý & Dashboard", "📅 3. Lịch Dự Kiến Thi Công"] if current_role == "admin" else ["🛠️ 1. Cổng Báo cáo Tiến độ", "📅 3. Lịch Dự Kiến Thi Công"]
    page = st.sidebar.radio("Chọn trang:", menu_options)

    if page == "🛠️ 1. Cổng Báo cáo Tiến độ":
        st.title("🛠️ CỔNG BÁO CÁO & XUẤT DỮ LIỆU TIẾN ĐỘ")
        # (Giữ nguyên logic trang 1 cũ của bạn...)
        st.write("Cổng báo cáo đang hoạt động.") 

    elif page == "📊 2. Trang Quản lý & Dashboard" and current_role == "admin":
        st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
        
        # MỤC BÁO CÁO THEO NGÀY
        with st.expander("📅 Xuất báo cáo tiến độ theo ngày", expanded=True):
            target_date = st.date_input("Chọn ngày báo cáo:")
            if st.button("📥 Xuất dữ liệu"):
                d_str = target_date.strftime("%d/%m/%Y")
                df_day = df_data[df_data.astype(str).apply(lambda x: x.str.contains(d_str)).any(axis=1)]
                report = []
                for dt in df_data[col_dt].dropna().unique():
                    df_sub = df_day[df_day[col_dt] == dt]
                    report.append({"Đối tác": dt, "Trạm lắp trong ngày": len(df_sub), "Tổng trạm đã nhận VT": count_col_done(df_sub[df_sub['Nhận VT'].notna()] if 'Nhận VT' in df_sub else df_sub, ["Nhận VT"])})
                
                buffer = io.BytesIO()
                pd.DataFrame(report).to_excel(buffer, index=False)
                st.download_button("Tải File Excel Báo Cáo", data=buffer.getvalue(), file_name=f"BaoCao_{d_str.replace('/','-')}.xlsx")

        summary_df = bll.process_partner_summary(df_data)
        st.dataframe(summary_df, use_container_width=True)

    elif page == "📅 3. Lịch Dự Kiến Thi Công":
        st.title("📅 QUẢN LÝ & LẬP LỊCH DỰ KIẾN THI CÔNG")
        # (Giữ nguyên logic trang 3 cũ của bạn...)
