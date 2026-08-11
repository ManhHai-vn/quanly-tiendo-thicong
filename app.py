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
    st.error(f"Lỗi khởi tạo dữ liệu: {e}")
    df_data = pd.DataFrame()

# Hàm dùng chung
def count_col_done(dframe, target_cols):
    for col_name in target_cols:
        if col_name in dframe.columns:
            s = dframe[col_name].astype(str).str.strip()
            return len(dframe[(s != "") & (s.str.lower() != "nan") & (s.str.lower() != "none")])
    return 0

col_dt = None
if not df_data.empty:
    for c in ["ĐỐI TÁC", "Đối tác", "doi_tac"]:
        if c in df_data.columns: col_dt = c; break
    if not col_dt and len(df_data.columns) > 5: col_dt = df_data.columns[5]

# --- HỆ THỐNG XÁC THỰC ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "username": "", "role": "", "partner_name": ""})

def login_screen():
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ 5G")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập:").lower()
            password = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("Đăng Nhập", use_container_width=True):
                users_db = {
                    "admin_agg": {"pass": "admin123", "role": "admin", "partner": "Tất cả"},
                    "vtk": {"pass": "vtk123", "role": "partner", "partner": "VTK"},
                    "vcc": {"pass": "vcc123", "role": "partner", "partner": "VCC"},
                }
                if username in users_db and users_db[username]["pass"] == password:
                    st.session_state.update({"authenticated": True, "username": username, "role": users_db[username]["role"], "partner_name": users_db[username]["partner"]})
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")

if not st.session_state["authenticated"]:
    login_screen()
else:
    # Sidebar
    st.sidebar.info(f"👤 {st.session_state['username'].upper()} | 🏢 {st.session_state['partner_name']}")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.update({"authenticated": False})
        st.rerun()

    menu = ["🛠️ 1. Cổng Báo cáo Tiến độ", "📊 2. Trang Quản lý & Dashboard"] if st.session_state["role"] == "admin" else ["🛠️ 1. Cổng Báo cáo Tiến độ"]
    page = st.sidebar.radio("Chọn trang:", menu)

    # --- TRANG QUẢN LÝ & DASHBOARD ---
    if page == "📊 2. Trang Quản lý & Dashboard":
        st.title("📊 TRANG QUẢN LÝ & DASHBOARD")
        
        # TÍNH NĂNG XUẤT BÁO CÁO NGÀY
        st.markdown("### 📅 Xuất tiến độ ngày")
        col1, col2 = st.columns([1, 2])
        target_date = col1.date_input("Chọn ngày báo cáo:")
        
        if col2.button("📥 Xuất báo cáo tiến độ ngày này"):
            date_str = target_date.strftime("%d/%m/%Y")
            # Lọc các dòng có ngày khớp
            df_filtered = df_data[df_data.astype(str).apply(lambda x: x.str.contains(date_str)).any(axis=1)]
            
            # Tính toán nhanh
            report_data = []
            for dt in df_data[col_dt].unique():
                df_dt = df_filtered[df_filtered[col_dt] == dt]
                report_data.append({
                    "Đối tác": dt,
                    "Số trạm lắp trong ngày": len(df_dt),
                    "Số trạm đã nhận VT": count_col_done(df_dt, ["Nhận VT", "Nhận thiết bị"])
                })
            
            output = io.BytesIO()
            pd.DataFrame(report_data).to_excel(output, index=False)
            st.download_button("Tải file Excel báo cáo", data=output.getvalue(), file_name=f"BaoCao_{date_str.replace('/','_')}.xlsx")

        st.markdown("---")
        # (Giữ nguyên logic bảng dashboard cũ của bạn bên dưới đây)
        summary_df = bll.process_partner_summary(df_data)
        st.dataframe(summary_df, use_container_width=True)

    # --- TRANG BÁO CÁO (Logic cũ) ---
    elif page == "🛠️ 1. Cổng Báo cáo Tiến độ":
        st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ")
        # ... (Phần logic báo cáo trạm cũ của bạn) ...
