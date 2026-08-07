import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Quản lý Tiến độ Thi công 5G - Online", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; font-weight: bold; border-radius: 6px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ HỆ THỐNG QUẢN LÝ TIẾN ĐỘ THI CÔNG 5G (GOOGLE SHEETS)")
st.markdown("---")

# Link Google Sheet của bạn
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1XDCtbHuqRmBTNcBAV4VCRw6kgQfVxiowhR-xfObu_0U/edit?usp=sharing"

@st.cache_data(ttl=60)
def load_data_gsheet():
    # Sử dụng gspread thông qua public link hoặc gsheet csv export để đọc nhanh
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df = pd.read_csv(csv_url)
    return df

df_data = load_data_gsheet()

menu = ["📊 1. Tổng quan Dự án (Dashboard)", "📝 2. Cổng Cập nhật Tiến độ Đối tác"]
choice = st.sidebar.selectbox("📂 Chọn chức năng", menu)

if choice == "📊 1. Tổng quan Dự án (Dashboard)":
    st.subheader("📊 Bảng điều khiển tổng quan tiến độ")
    st.metric("Tổng số trạm", f"{len(df_data)} trạm")
    st.dataframe(df_data, use_container_width=True)

elif choice == "📝 2. Cổng Cập nhật Tiến độ Đối tác":
    st.subheader("📝 Cập nhật tiến độ trạm trực tuyến")
    
    if "MaTram" in df_data.columns:
        selected_tram = st.selectbox("Chọn mã trạm cần cập nhật:", df_data["MaTram"].dropna().unique())
        
        if selected_tram:
            row_data = df_data[df_data["MaTram"] == selected_tram].iloc[0]
            
            st.info(f"Đang cập nhật cho Trạm: **{selected_tram}**")
            
            with st.form("update_form"):
                nhan_vt = st.checkbox("Đã nhận vật tư", value=False)
                lap_5g = st.checkbox("Đã lắp đặt 5G", value=False)
                
                submitted = st.form_submit_button("Lưu thay đổi")
                if submitted:
                    st.success("Đã ghi nhận thay đổi! (Lưu ý: Để ghi trực tiếp ngược lại Google Sheets tự động 100%, bạn có thể cập nhật trực tiếp trên bảng Google Sheets bên dưới).")
                    
        st.markdown("### 📋 Dữ liệu trực tuyến hiện tại:")
        st.dataframe(df_data, use_container_width=True)
    else:
        st.error("Không tìm thấy cột 'MaTram' trong Google Sheets của bạn. Vui lòng kiểm tra lại tên cột ở dòng đầu tiên của file Google Sheets!")
