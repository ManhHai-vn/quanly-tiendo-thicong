import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1XDCtbHuqRmBTNcBAV4VCRw6kgQfVxiowhR-xfObu_0U/edit?usp=sharing"

@st.cache_data(ttl=10) # TTL ngắn để dữ liệu cập nhật nhanh khi đối tác vừa nhập
def load_data():
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    return pd.read_csv(csv_url)

df_data = load_data()

# --- MENU ĐIỀU HƯỚNG ---
st.sidebar.title("📌 HỆ THỐNG 5G")
page = st.sidebar.radio("Chọn trang:", ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"])

# ==========================================
# TRANG 1: DÀNH CHO ĐỐI TÁC BÁO CÁO TIẾN ĐỘ
# ==========================================
if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
    st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
    st.markdown("Kỹ sư/Đối tác chọn trạm, tìm kiếm và cập nhật tình hình thực hiện hiện trường.")
    st.markdown("---")

    if "Matram" in df_data.columns:
        # Lọc theo đối tác để họ dễ tìm trạm của mình
        ds_doi_tac = ["Tất cả"] + list(df_data["DoiTac"].dropna().unique()) if "DoiTac" in df_data.columns else ["Tất cả"]
        chon_dt = st.selectbox("🏢 Chọn tên Đối tác của bạn:", ds_doi_tac)

        df_hien_thi = df_data.copy()
        if chon_dt != "Tất cả":
            df_hien_thi = df_hien_thi[df_hien_thi["DoiTac"] == chon_dt]

        # Ô tìm kiếm mã trạm
        tu_khoa = st.text_input("🔍 Nhập mã trạm cần cập nhật (VD: AGG0002):")
        if tu_khoa:
            df_hien_thi = df_hien_thi[df_hien_thi["Matram"].astype(str).str.contains(tu_khoa, case=False, na=False)]

        if not df_hien_thi.empty:
            list_tram = df_hien_thi["Matram"].tolist()
            tram_chon = st.selectbox("📌 Chọn chính xác Mã trạm:", list_tram)
            
            # Lấy thông tin trạm được chọn
            thong_tin_tram = df_data[df_data["Matram"] == tram_chon].iloc[0]
            
            st.info(f"Đang thao tác cho Trạm: **{tram_chon}** | Khu vực: {thong_tin_tram.get('KhuVuc', 'N/A')}")
            
            with st.form("form_bao_cao_doi_tac"):
                st.markdown("### Tích chọn các mốc đã hoàn thành:")
                
                # Kiểm tra giá trị cũ (nếu có dữ liệu thì mặc định check true)
                val_nhan_vt = pd.notna(thong_tin_tram.get("DoiTac_NhanVT")) and str(thong_tin_tram.get("DoiTac_NhanVT")) != ""
                val_rai_vt = pd.notna(thong_tin_tram.get("RaiVT")) and str(thong_tin_tram.get("RaiVT")) != ""
                val_lap_5g = pd.notna(thong_tin_tram.get("LapTB_5G")) and str(thong_tin_tram.get("LapTB_5G")) != ""

                chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư", value=val_nhan_vt)
                chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm", value=val_rai_vt)
                chk_lap_5g = st.checkbox("⚡ Đã lắp đặt xong thiết bị 5G", value=val_lap_5g)
                
                ghi_chu_ngay = st.text_input("Nhập ngày thực hiện (DD/MM/YYYY):", value=pd.Timestamp.now().strftime("%d/%m/%Y"))
                
                submit_bao_cao = st.form_submit_button("🚀 Gửi Báo Cáo Tiến Độ")
                
                if submit_bao_cao:
                    st.success(f"Đã ghi nhận báo cáo cho trạm {tram_chon}!")
                    st.warning("⚠️ Vì lý do bảo mật quyền ghi trực tiếp API, sau khi bấm nút này, bạn hãy **vào trực tiếp file Google Sheets để tích chọn** hoặc dùng tính năng quản lý bên dưới để đồng bộ.")
        else:
            st.warning("Không tìm thấy trạm phù hợp.")

# ==========================================
# TRANG 2: DÀNH CHO QUẢN LÝ DỮ LIỆU & DASHBOARD
# ==========================================
elif page == "📊 2. Trang Quản lý & Dashboard":
    st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
    st.markdown("Dành cho Chỉ huy trưởng/Quản lý theo dõi tổng quan tiến độ toàn dự án.")
    st.markdown("---")

    # Hiển thị các chỉ số tổng quan (Metrics)
    tong_tram = len(df_data)
    st.metric(label="Tổng số trạm trong dự án", value=tong_tram)

    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống (Đồng bộ từ Google Sheets)")
    st.dataframe(df_data, use_container_width=True)
    
    st.markdown("### 🔗 Liên kết nhanh:")
    st.markdown("[Mở file Google Sheets gốc để chỉnh sửa nhanh](https://docs.google.com/spreadsheets/d/1XDCtbHuqRmBTNcBAV4VCRw6kgQfVxiowhR-xfObu_0U/edit?usp=sharing)")
