import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Quản lý Tiến độ Thi công 5G", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; font-weight: bold; border-radius: 6px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ HỆ THỐNG QUẢN LÝ & BÁO CÁO TIẾN ĐỘ THI CÔNG 5G")
st.markdown("Hệ thống đọc trực tiếp toàn bộ dữ liệu từ file Excel chuẩn.")
st.markdown("---")

EXCEL_FILE = "test_file.xlsx"

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    df = pd.read_excel(file_path, sheet_name="Sheet1", header=None)
    cols = [
        "STT", "MaTram", "Ma5G", "KhuVuc", "GiaoTrienKhai", "DoiTac", 
        "TrangThai", "MaCongTrinh", "Network", 
        "YCVT_ChuyenKho", "CapTB_KhoTinh", "VietPhieu", "DoiTac_NhanVT", "RaiVT", "LapTB_5G"
    ]
    if df.shape[1] >= len(cols):
        df = df.iloc[:, :len(cols)]
        df.columns = cols
    return df

if os.path.exists(EXCEL_FILE):
    df_data = load_data(EXCEL_FILE)
    
    menu = ["📊 1. Tổng quan Dự án (Dashboard)", "🔍 2. Tra cứu Chi tiết Trạm", "📈 3. Tổng hợp theo Đối tác"]
    choice = st.sidebar.selectbox("📂 Chọn chức năng quản lý", menu)

    if choice == "📊 1. Tổng quan Dự án (Dashboard)":
        st.subheader("📊 Bảng điều khiển tổng quan tiến độ toàn dự án")
        
        total_tram = len(df_data)
        tram_trien_khai = len(df_data[df_data["TrangThai"] == "Triển khai"])
        tram_du_phong = len(df_data[df_data["TrangThai"] == "Dự phòng"])
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="Tổng số trạm", value=f"{total_tram} trạm")
        with col2: st.metric(label="Trạm Triển khai", value=f"{tram_trien_khai} trạm")
        with col3: st.metric(label="Trạm Dự phòng", value=f"{tram_du_phong} trạm")
            
        st.markdown("### 📋 Danh sách chi tiết dữ liệu trạm")
        st.dataframe(df_data, use_container_width=True)

    elif choice == "🔍 2. Tra cứu Chi tiết Trạm":
        st.subheader("🔍 Tra cứu thông tin chi tiết từng trạm")
        keyword = st.text_input("Nhập mã trạm cần tìm (ví dụ: AGG0019-11):")
        if keyword:
            result = df_data[df_data["MaTram"].astype(str).str.contains(keyword, case=False, na=False)]
            if not result.empty:
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("Không tìm thấy mã trạm phù hợp!")
        else:
            st.info("Vui lòng nhập mã trạm vào ô tìm kiếm ở trên.")

    elif choice == "📈 3. Tổng hợp theo Đối tác":
        st.subheader("📈 Tổng hợp số lượng trạm theo Đối tác")
        if "DoiTac" in df_data.columns:
            summary = df_data["DoiTac"].value_counts(dropna=False).reset_index()
            summary.columns = ["Đối tác", "Số lượng trạm"]
            st.dataframe(summary, use_container_width=True)
            st.bar_chart(summary.set_index("Đối tác"))
else:
    st.error(f"⚠️ Không tìm thấy file `{EXCEL_FILE}` trên kho chứa GitHub. Vui lòng tải file `test_file.xlsx` lên GitHub cùng thư mục với file app_demo.py!")
