import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Cổng Báo cáo Tiến độ Đối tác", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #28a745; color: white; font-weight: bold; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ CỔNG CẬP NHẬT TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
st.markdown("Chọn trạm cần cập nhật, tích chọn các mốc hoàn thành và bấm lưu để cập nhật vào dữ liệu.")
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

# Đọc dữ liệu
if os.path.exists(EXCEL_FILE):
    # Dùng st.session_state để lưu dữ liệu tạm thời khi cập nhật trực tiếp
    if 'df_data' not in st.session_state:
        st.session_state.df_data = load_data(EXCEL_FILE)
    
    df_data = st.session_state.df_data

    # Giao diện tìm kiếm trạm để cập nhật
    st.subheader("🔍 1. Tìm kiếm trạm cần cập nhật tiến độ")
    col1, col2 = st.columns(2)
    with col1:
        search_tram = st.text_input("Nhập Mã Trạm hoặc Mã 5G cần cập nhật (VD: AGG0019):")
    with col2:
        chon_dt = st.selectbox("Lọc theo Đối tác của bạn:", ["Tất cả"] + list(df_data["DoiTac"].dropna().unique()))

    # Lọc danh sách trạm theo từ khóa
    filtered_df = df_data.copy()
    if search_tram:
        filtered_df = filtered_df[
            filtered_df["MaTram"].astype(str).str.contains(search_tram, case=False, na=False) |
            filtered_df["Ma5G"].astype(str).str.contains(search_tram, case=False, na=False)
        ]
    if chon_dt != "Tất cả":
        filtered_df = filtered_df[filtered_df["DoiTac"] == chon_dt]

    if not filtered_df.empty:
        # Chọn trạm cụ thể từ danh sách tìm thấy
        list_tram_hien_thi = filtered_df["MaTram"].tolist()
        selected_tram_code = st.selectbox("📌 Chọn chính xác Trạm cần thao tác:", list_tram_hien_thi)
        
        # Lấy thông tin dòng của trạm được chọn
        tram_row = df_data[df_data["MaTram"] == selected_tram_code].index[0]
        current_data = df_data.loc[tram_row]
        
        st.markdown("---")
        st.subheader(f"📝 2. Cập nhật mốc hiện trường cho trạm: **{selected_tram_code}**")
        st.info(f"Khu vực: {current_data['KhuVuc']} | Đối tác: {current_data['DoiTac']} | Trạng thái: {current_data['TrangThai']}")
        
        with st.form(key="update_form"):
            # Kiểm tra trạng thái hiện tại (nếu có dữ liệu ngày tháng nghĩa là đã check)
            val_nhan_vt = pd.notna(current_data["DoiTac_NhanVT"])
            val_rai_vt = pd.notna(current_data["RaiVT"])
            val_lap_5g = pd.notna(current_data["LapTB_5G"])
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư", value=val_nhan_vt)
            with col_b:
                chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm", value=val_rai_vt)
            with col_c:
                chk_lap_5g = st.checkbox("⚡ Đã lắp đặt xong TB 5G", value=val_lap_5g)
                
            ghichu_date = st.text_input("Ghi chú ngày tháng thực hiện (Để trống sẽ tự động lấy ngày hôm nay DD/MM/YYYY):", value=datetime.now().strftime("%d/%m/%Y"))
            
            submit_button = st.form_submit_button(label="💾 Cập nhật và Lưu vào hệ thống")
            
            if submit_button:
                ngay_ghi_nhan = ghichu_date if ghichu_date else datetime.now().strftime("%d/%m/%Y")
                
                # Cập nhật giá trị vào DataFrame trong bộ nhớ
                if chk_nhan_vt:
                    df_data.at[tram_row, "DoiTac_NhanVT"] = ngay_ghi_nhan
                else:
                    df_data.at[tram_row, "DoiTac_NhanVT"] = pd.NA
                    
                if chk_rai_vt:
                    df_data.at[tram_row, "RaiVT"] = ngay_ghi_nhan
                else:
                    df_data.at[tram_row, "RaiVT"] = pd.NA
                    
                if chk_lap_5g:
                    df_data.at[tram_row, "LapTB_5G"] = ngay_ghi_nhan
                else:
                    df_data.at[tram_row, "LapTB_5G"] = pd.NA
                
                # Lưu lại vào session state
                st.session_state.df_data = df_data
                
                # Lưu đè file trên máy (nếu chạy local) hoặc tạo file tải về
                df_data.to_excel(EXCEL_FILE, sheet_name="Sheet1", index=False, header=False)
                
                st.success(f"🎉 Đã cập nhật thành công tiến độ cho trạm {selected_tram_code}!")
        
        st.markdown("---")
        st.subheader("📋 Xem lại bảng dữ liệu sau khi cập nhật:")
        st.dataframe(df_data, use_container_width=True)
        
        # Nút tải file Excel mới nhất về máy để đồng bộ
        st.download_button(
            label="📥 Tải file Excel mới nhất về máy",
            data=open(EXCEL_FILE, "rb").read(),
            file_name="test_file_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    else:
        st.warning("Không tìm thấy trạm phù hợp với từ khóa bạn nhập.")
else:
    st.error(f"⚠️ Không tìm thấy file `{EXCEL_FILE}` trên GitHub!")
