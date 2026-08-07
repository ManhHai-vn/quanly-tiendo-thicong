import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quản lý Tiến độ Thi công 5G", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; font-weight: bold; border-radius: 6px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ HỆ THỐNG QUẢN LÝ TIẾN ĐỘ THI CÔNG 5G")
st.markdown("---")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1XDCtbHuqRmBTNcBAV4VCRw6kgQfVxiowhR-xfObu_0U/edit?usp=sharing"

@st.cache_data(ttl=60)
def load_data_gsheet():
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    # Đọc trực tiếp không bỏ dòng nào vì dòng 1 đã là tiêu đề chuẩn
    df = pd.read_csv(csv_url)
    return df

try:
    df_data = load_data_gsheet()
    
    # Gán lại tên cột chuẩn xác theo đúng thứ tự các cột từ trái sang phải trong ảnh của bạn
    cols_chuan = [
        "STT", "Matram", "Ma5G", "KhuVuc", "GiaoTrienKhai", "DoiTac", 
        "TrangThai", "MaCongTrinh", "Network", 
        "VietPhieu", "DoiTac_NhanVT", "RaiVT", "LapTB_5G"
    ]
    
    # Chỉ định lại tên cột nếu số lượng cột khớp
    if len(df_data.columns) >= len(cols_chuan):
        df_data.columns = cols_chuan + list(df_data.columns[len(cols_chuan):])

    menu = ["📊 1. Tổng quan Dự án (Dashboard)", "🔍 2. Tra cứu & Lọc Trạm"]
    choice = st.sidebar.selectbox("📂 Chọn chức năng", menu)

    if choice == "📊 1. Tổng quan Dự án (Dashboard)":
        st.subheader("📊 Bảng điều khiển tổng quan tiến độ")
        st.metric("Tổng số trạm", f"{len(df_data)} trạm")
        st.dataframe(df_data, use_container_width=True)

    elif choice == "🔍 2. Tra cứu & Lọc Trạm":
        st.subheader("🔍 Tra cứu thông tin trạm")
        keyword = st.text_input("Nhập mã trạm cần tìm (VD: AGG0002):")
        if keyword:
            result = df_data[df_data["Matram"].astype(str).str.contains(keyword, case=False, na=False)]
            st.dataframe(result, use_container_width=True)
        else:
            st.dataframe(df_data, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Lỗi đọc dữ liệu từ Google Sheets: {e}")
