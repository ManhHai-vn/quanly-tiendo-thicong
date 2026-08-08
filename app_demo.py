import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1XDCtbHuqRmBTNcBAV4VCRw6kgQfVxiowhR-xfObu_0U/edit?usp=sharing"

@st.cache_data(ttl=5)
def load_data():
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df = pd.read_csv(csv_url)
    cols_chuan = [
        "STT", "Matram", "Ma5G", "KhuVuc", "GiaoTrienKhai", "DoiTac", 
        "TrangThai", "MaCongTrinh", "Network", 
        "VietPhieu", "DoiTac_NhanVT", "RaiVT", "LapTB_5G"
    ]
    if len(df.columns) >= len(cols_chuan):
        df.columns = cols_chuan + list(df.columns[len(cols_chuan):])
    return df

df_data = load_data()

# --- MENU ĐIỀU HƯỚNG ---
st.sidebar.title("📌 HỆ THỐNG 5G")
page = st.sidebar.radio("Chọn trang:", ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"])

# ==========================================
# TRANG 1: DÀNH CHO ĐỐI TÁC BÁO CÁO TIẾN ĐỘ
# ==========================================
if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
    st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
    st.markdown("Kỹ sư/Đối tác chọn trạm và cập nhật tình hình thực hiện hiện trường.")
    st.markdown("---")

    if "Matram" in df_data.columns:
        ds_doi_tac = ["Tất cả"] + list(df_data["DoiTac"].dropna().unique()) if "DoiTac" in df_data.columns else ["Tất cả"]
        chon_dt = st.selectbox("🏢 Chọn tên Đối tác của bạn:", ds_doi_tac)

        df_hien_thi = df_data.copy()
        if chon_dt != "Tất cả":
            df_hien_thi = df_hien_thi[df_hien_thi["DoiTac"] == chon_dt]

        tu_khoa = st.text_input("🔍 Nhập mã trạm cần tìm (VD: AGG0002):")
        if tu_khoa:
            df_hien_thi = df_hien_thi[df_hien_thi["Matram"].astype(str).str.contains(tu_khoa, case=False, na=False)]

        if not df_hien_thi.empty:
            list_tram = df_hien_thi["Matram"].tolist()
            tram_chon = st.selectbox("📌 Chọn chính xác Mã trạm:", list_tram)
            
            thong_tin_tram = df_data[df_data["Matram"] == tram_chon].iloc[0]
            st.info(f"Đang thao tác cho Trạm: **{tram_chon}** | Khu vực: {thong_tin_tram.get('KhuVuc', 'N/A')}")
            
            with st.form("form_bao_cao_doi_tac"):
                st.markdown("### Tích chọn các mốc đã hoàn thành:")
                
                val_nhan_vt = pd.notna(thong_tin_tram.get("DoiTac_NhanVT")) and str(thong_tin_tram.get("DoiTac_NhanVT")) != ""
                val_rai_vt = pd.notna(thong_tin_tram.get("RaiVT")) and str(thong_tin_tram.get("RaiVT")) != ""
                val_lap_5g = pd.notna(thong_tin_tram.get("LapTB_5G")) and str(thong_tin_tram.get("LapTB_5G")) != ""

                chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư", value=val_nhan_vt)
                chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm", value=val_rai_vt)
                chk_lap_5g = st.checkbox("⚡ Đã lắp đặt xong thiết bị 5G", value=val_lap_5g)
                
                ghi_chu_ngay = st.text_input("Nhập ngày thực hiện (DD/MM/YYYY):", value=pd.Timestamp.now().strftime("%d/%m/%Y"))
                
                submit_bao_cao = st.form_submit_button("🚀 Gửi Báo Cáo Tiến Độ")
                
                if submit_bao_cao:
                    st.success(f"🎉 Đã ghi nhận báo cáo thành công cho trạm {tram_chon}!")
                    st.markdown(f"👉 [Bấm vào đây để mở trực tiếp Google Sheets cập nhật nhanh dòng trạm {tram_chon}]({GOOGLE_SHEET_URL})")
        else:
            st.warning("Không tìm thấy trạm phù hợp.")

# ==========================================
# TRANG 2: DÀNH CHO QUẢN LÝ DỮ LIỆU & DASHBOARD
# ==========================================
elif page == "📊 2. Trang Quản lý & Dashboard":
    st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
    st.markdown("Dành cho Chỉ huy trưởng/Quản lý theo dõi tổng quan tiến độ toàn dự án.")
    st.markdown("---")

    tong_tram = len(df_data)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Tổng số trạm trong dự án", value=tong_tram)
    
    st.markdown("### 📈 Báo cáo Lắp đặt theo từng Đối tác")
    if "DoiTac" in df_data.columns and "LapTB_5G" in df_data.columns:
        df_dt = df_data[df_data["DoiTac"].notna() & (df_data["DoiTac"].astype(str).str.strip() != "")]
        summary_df = df_dt.groupby("DoiTac").agg(
            Tong_Giao=("Matram", "count"),
            Da_Lap_Dat=("LapTB_5G", lambda x: x.dropna().loc[x.astype(str).str.strip() != ""].count())
        ).reset_index()
        
        summary_df["Ty_Le_%"] = (summary_df["Da_Lap_Dat"] / summary_df["Tong_Giao"] * 100).round(1)
        summary_df["Ti_Le_Hien_Thi"] = summary_df["Ty_Le_%"].astype(str) + "%"
        
        summary_df = summary_df.rename(columns={
            "DoiTac": "Tên Đối Tác",
            "Tong_Giao": "Tổng Trạm Đã Giao",
            "Da_Lap_Dat": "Đã Lắp Đặt",
            "Ti_Le_Hien_Thi": "Tỷ Lệ Hoàn Thành"
        })
        
        st.dataframe(summary_df[["Tên Đối Tác", "Tổng Trạm Đã Giao", "Đã Lắp Đặt", "Tỷ Lệ Hoàn Thành"]], use_container_width=True, hide_index=True)
    else:
        st.warning("Chưa xác định được cột 'DoiTac' hoặc 'LapTB_5G' để tổng hợp.")

    st.markdown("---")
    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống (Đồng bộ từ Google Sheets)")
    st.dataframe(df_data, use_container_width=True)
