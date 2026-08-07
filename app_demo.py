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
st.markdown("Hệ thống quản lý tiến độ, theo dõi hiện trường và báo cáo ngày chi tiết.")
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
    
    menu = [
        "📊 1. Tổng quan Tiến độ (Dashboard)", 
        "🔍 2. Tra cứu & Lọc Trạm Hiện Trường", 
        "📅 3. Báo cáo Chi tiết theo Ngày",
        "📈 4. Tổng hợp Khối lượng theo Đối tác"
    ]
    choice = st.sidebar.selectbox("📂 Chọn chức năng nghiệp vụ", menu)

    # 1. Dashboard tổng quan
    if choice == "📊 1. Tổng quan Tiến độ (Dashboard)":
        st.subheader("📊 Bảng điều khiển tổng quan dự án 5G")
        
        total_tram = len(df_data)
        tram_tk = len(df_data[df_data["TrangThai"] == "Triển khai"])
        tram_dp = len(df_data[df_data["TrangThai"] == "Dự phòng"])
        tram_lap_dat = df_data["LapTB_5G"].dropna().count()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="Tổng số trạm", value=f"{total_tram}")
        with col2: st.metric(label="Trạm Triển khai", value=f"{tram_tk}")
        with col3: st.metric(label="Trạm Dự phòng", value=f"{tram_dp}")
        with col4: st.metric(label="Đã lắp TB 5G", value=f"{tram_lap_dat}")
            
        st.markdown("### 📋 Danh sách tổng hợp tiến độ chi tiết")
        st.dataframe(df_data, use_container_width=True)

    # 2. Tra cứu chi tiết
    elif choice == "🔍 2. Tra cứu & Lọc Trạm Hiện Trường":
        st.subheader("🔍 Tra cứu và Lọc danh sách trạm")
        
        col_a, col_b = st.columns(2)
        with col_a:
            keyword = st.text_input("🔍 Nhập mã trạm (VD: AGG0019):")
        with col_b:
            selected_dt = st.selectbox("🏢 Lọc theo đối tác", ["Tất cả"] + list(df_data["DoiTac"].dropna().unique()))
            
        result = df_data.copy()
        if keyword:
            result = result[result["MaTram"].astype(str).str.contains(keyword, case=False, na=False)]
        if selected_dt != "Tất cả":
            result = result[result["DoiTac"] == selected_dt]
            
        st.markdown(f"**Kết quả tìm kiếm:** Tìm thấy {len(result)} trạm phù hợp.")
        st.dataframe(result, use_container_width=True)

    # 3. Tab Báo cáo theo ngày
    elif choice == "📅 3. Báo cáo Chi tiết theo Ngày":
        st.subheader("📅 Báo cáo Sản lượng và Tiến độ theo Ngày")
        st.markdown("Chọn mốc công việc để lọc danh sách các trạm đã thực hiện.")
        
        date_columns = {
            "YCVT Chuyển kho": "YCVT_ChuyenKho",
            "Cấp TB về kho tỉnh": "CapTB_KhoTinh",
            "Viết phiếu cho đối tác": "VietPhieu",
            "Đối tác nhận vật tư": "DoiTac_NhanVT",
            "Rải VT đến trạm": "RaiVT",
            "Lắp TB 5G": "LapTB_5G"
        }
        
        selected_milestone_label = st.selectbox("📌 Chọn mốc công việc báo cáo:", list(date_columns.keys()))
        col_name = date_columns[selected_milestone_label]
        
        df_filtered = df_data[df_data[col_name].notna()].copy()
        
        if not df_filtered.empty:
            st.success(f"Đã lọc thành công các trạm đạt mốc: {selected_milestone_label}")
            
            if "DoiTac" in df_filtered.columns:
                st.markdown("### 📊 Tổng hợp sản lượng theo Đối tác cho mốc này:")
                thong_ke_ngay = df_filtered["DoiTac"].value_counts().reset_index()
                thong_ke_ngay.columns = ["Đối tác", "Số lượng trạm"]
                st.dataframe(thong_ke_ngay, use_container_width=True)
            
            st.markdown("### 📋 Danh sách chi tiết các trạm:")
            st.dataframe(df_filtered[["STT", "MaTram", "Ma5G", "KhuVuc", "DoiTac", "TrangThai", col_name, "MaCongTrinh"]], use_container_width=True)
        else:
            st.warning(f"Chưa có dữ liệu ghi nhận cho mốc công việc: {selected_milestone_label}")

    # 4. Tổng hợp theo đối tác
    elif choice == "📈 4. Tổng hợp Khối lượng theo Đối tác":
        st.subheader("📈 Phân tích khối lượng công việc theo Đối tác")
        if "DoiTac" in df_data.columns:
            summary = df_data.groupby("DoiTac").agg(
                Tong_Trang=("MaTram", "count"),
                Triển_Khai=("TrangThai", lambda x: (x == "Triển khai").sum()),
                Đã_Lắp_5G=("LapTB_5G", lambda x: x.dropna().count())
            ).reset_index()
            
            st.dataframe(summary, use_container_width=True)
            st.bar_chart(summary.set_index("DoiTac")[["Tong_Trang", "Đã_Lắp_5G"]])
else:
    st.error(f"⚠️ Không tìm thấy file `{EXCEL_FILE}` trên kho chứa GitHub. Vui lòng tải file Excel lên kho chứa!")
