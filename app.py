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
            col_dt = c; break
    if not col_dt and len(df_data.columns) > 5: col_dt = df_data.columns[5]

def count_col_done(dframe, target_cols):
    for col_name in target_cols:
        if col_name in dframe.columns:
            s = dframe[col_name].astype(str).str.strip()
            return len(dframe[(s != "") & (s.str.lower() != "nan") & (s.str.lower() != "none")])
    return 0

# --- HỆ THỐNG XÁC THỰC ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "username": "", "role": "", "partner_name": ""})

def login_screen():
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ 5G")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập:").lower() # Chuyển về lowercase
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
    current_role, current_partner = st.session_state["role"], st.session_state["partner_name"]
    # ... (Sidebar code tương tự cũ) ...
    page = st.sidebar.radio("Chọn trang:", ["🛠️ 1. Cổng Báo cáo Tiến độ", "📊 2. Trang Quản lý & Dashboard", "📅 3. Lịch Dự Kiến Thi Công"] if current_role=="admin" else ["🛠️ 1. Cổng Báo cáo Tiến độ", "📅 3. Lịch Dự Kiến Thi Công"])

    if page == "📊 2. Trang Quản lý & Dashboard" and current_role == "admin":
        st.title("📊 TRANG QUẢN LÝ ĐIỀU HÀNH")
        
        # --- TÍNH NĂNG XUẤT BÁO CÁO THEO NGÀY ---
        st.markdown("---")
        st.subheader("📅 Xuất Báo Cáo Tiến Độ Theo Ngày")
        col_date, col_btn_report = st.columns([2, 2])
        target_date = col_date.date_input("Chọn ngày báo cáo:")
        
        if col_btn_report.button("📥 Tải báo cáo tiến độ trong ngày"):
            target_date_str = target_date.strftime("%d/%m/%Y")
            # Logic lọc: Các trạm có ngày lắp hoặc cột liên quan khớp ngày này
            # Giả định cột chứa ngày lắp là 'Ngày lắp' hoặc tương đương
            df_report = df_data[df_data.astype(str).apply(lambda x: x.str.contains(target_date_str)).any(axis=1)]
            
            output = io.BytesIO()
            with pd.ExcelWriter(output) as writer:
                df_report.to_excel(writer, index=False, sheet_name="BaoCaoNgay")
            st.download_button("Tải file Excel", data=output.getvalue(), file_name=f"BaoCao_{target_date_str.replace('/','_')}.xlsx")

        st.markdown("---")
        # ... (Phần Dashboard cũ giữ nguyên) ...
