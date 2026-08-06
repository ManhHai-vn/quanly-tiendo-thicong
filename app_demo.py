import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Demo Quản lý Tiến độ Thi công", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; font-weight: bold; border-radius: 6px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ DEMO HỆ THỐNG QUẢN LÝ & BÁO CÁO TIẾN ĐỘ THI CÔNG")
st.markdown("Hệ thống giúp quản lý tập trung 3 nhà thầu, phân tích báo cáo ngày và tự động tổng hợp số liệu lũy kế.")
st.markdown("---")

menu = ["📊 1. Tổng quan Dự án (Dashboard)", "🤖 2. Phân tích Ảnh Báo cáo Ngày (AI Mock)", "📝 3. Xuất Báo cáo Ngày (Zalo Text)", "📈 4. Tổng hợp theo Nhà thầu"]
choice = st.sidebar.selectbox("📂 Chọn chức năng quản lý", menu)

DATA_FILE = "demo_dulieu_tiendo.csv"

if not os.path.exists(DATA_FILE):
    initial_data = [
        {"Ngay": "2026-08-02", "NhaThau": "Nhà thầu A", "NhanThietBi_Ngay": 29, "RaiThietBi_Ngay": 29, "LapDat_Ngay": 3, "DanhSachTram": "KGG0322-11, KGG0330, KGG0684", "BienBanKy": 0, "GhiChu": "Hoàn thành tốt"},
        {"Ngay": "2026-08-02", "NhaThau": "Nhà thầu B", "NhanThietBi_Ngay": 10, "RaiThietBi_Ngay": 10, "LapDat_Ngay": 2, "DanhSachTram": "KGG0725, KGG0587-12", "BienBanKy": 1, "GhiChu": "Vướng mặt bằng 1 trạm"},
        {"Ngay": "2026-08-03", "NhaThau": "Nhà thầu A", "NhanThietBi_Ngay": 5, "RaiThietBi_Ngay": 5, "LapDat_Ngay": 4, "DanhSachTram": "KGG0726, KGG0727, KGG0728, KGG0729", "BienBanKy": 3, "GhiChu": "Đẩy nhanh tiến độ"},
    ]
    pd.DataFrame(initial_data).to_csv(DATA_FILE, index=False)

df_data = pd.read_csv(DATA_FILE)

if choice == "📊 1. Tổng quan Dự án (Dashboard)":
    st.subheader("📊 Bảng điều khiển tổng quan tiến độ toàn dự án")
    total_nhan = df_data["NhanThietBi_Ngay"].sum()
    total_lap = df_data["LapDat_Ngay"].sum()
    total_bb = df_data["BienBanKy"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="Tổng Nhà thầu", value="3 Nhà thầu")
    with col2: st.metric(label="Tổng TB đã nhận", value=f"{total_nhan} / 235 trạm")
    with col3: st.metric(label="Tổng Trạm đã lắp", value=f"{total_lap} trạm")
    with col4: st.metric(label="Biên bản đã ký", value=f"{total_bb} trạm")
        
    st.markdown("### 📋 Nhật ký toàn bộ dữ liệu báo cáo đã ghi nhận")
    st.dataframe(df_data, use_container_width=True)

elif choice == "🤖 2. Phân tích Ảnh Báo cáo Ngày (AI Mock)":
    st.subheader("🤖 Trợ lý AI Đọc Hình ảnh Báo cáo / Biên bản hiện trường")
    col1, col2 = st.columns(2)
    with col1:
        nt_chon = st.selectbox("Chọn nhà thầu báo cáo", ["Nhà thầu A", "Nhà thầu B", "Nhà thầu C"])
        ngay_bc = st.date_input("Ngày báo cáo", datetime.date(2026, 8, 4))
        uploaded_file = st.file_uploader("📤 Tải lên ảnh báo cáo", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Hình ảnh báo cáo thực tế", use_container_width=True)
    with col2:
        st.markdown("### 🔍 Kết quả AI bóc tách thông tin")
        if uploaded_file is not None:
            if st.button("⚡ Chạy AI Nhận diện Văn bản & Số liệu"):
                st.success("✅ Phân tích hoàn tất thành công!")
                st.info(f"**Nhà thầu:** {nt_chon}\n**Nhận:** 8 trạm\n**Rải:** 8 trạm\n**Lắp đặt:** 3 trạm\n**Mã trạm:** `KGG0801, KGG0802`")
                if st.button("💾 Lưu báo cáo này vào hệ thống"):
                    new_row = {"Ngay": str(ngay_bc), "NhaThau": nt_chon, "NhanThietBi_Ngay": 8, "RaiThietBi_Ngay": 8, "LapDat_Ngay": 3, "DanhSachTram": "KGG0801, KGG0802", "BienBanKy": 2, "GhiChu": "AI tự động trích xuất"}
                    df_data = pd.concat([df_data, pd.DataFrame([new_row])], ignore_index=True)
                    df_data.to_csv(DATA_FILE, index=False)
                    st.success("🎉 Đã lưu thành công vào file hệ thống!")
        else:
            st.warning("Vui lòng tải lên một hình ảnh mẫu.")

elif choice == "📝 3. Xuất Báo cáo Ngày (Zalo Text)":
    st.subheader("📝 Tạo & Xuất Mẫu Báo cáo Nhanh cho Nhóm Zalo")
    ngay_xem = st.selectbox("Chọn ngày cần xuất báo cáo", df_data["Ngay"].unique())
    df_ngay_chon = df_data[df_data["Ngay"] == ngay_xem]
    st.dataframe(df_ngay_chon, use_container_width=True)
    
    zalo_msg = f"📌 *BÁO CÁO TIẾN ĐỘ THI CÔNG - NGÀY {ngay_xem}* 📌\n\n"
    for idx, row in df_ngay_chon.iterrows():
        zalo_msg += f"🔹 *{row['NhaThau']}*:\n   - Nhận: {row['NhanThietBi_Ngay']} trạm\n   - Lắp đặt: {row['LapDat_Ngay']} trạm (Mã: {row['DanhSachTram']})\n   - Biên bản ký: {row['BienBanKy']}\n\n"
    st.code(zalo_msg, language="text")

elif choice == "📈 4. Tổng hợp theo Nhà thầu":
    st.subheader("📈 Tổng hợp Khối lượng Lũy kế theo Từng Nhà thầu")
    df_summary = df_data.groupby("NhaThau")[["NhanThietBi_Ngay", "RaiThietBi_Ngay", "LapDat_Ngay", "BienBanKy"]].sum().reset_index()
    df_summary.columns = ["Nhà thầu", "Tổng Nhận TB", "Tổng Rải TB", "Tổng Lắp Đặt", "Tổng Biên Bản"]
    st.dataframe(df_summary, use_container_width=True)
    st.bar_chart(df_summary.set_index("Nhà thầu")["Tổng Lắp Đặt"])