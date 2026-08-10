# (Giữ nguyên các phần import phía trên)
from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

@st.cache_resource
def get_bll():
    return BusinessLogicLayer()

bll = get_bll()
df_data = bll.get_raw_data()

st.sidebar.title("📌 HỆ THỐNG 5G (BETA)")
page = st.sidebar.radio("Chọn trang:", ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"])

if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
    st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG")
    st.markdown("---")

    ds_doi_tac = bll.get_partners(df_data)
    chon_dt = st.selectbox("🏢 Chọn tên Đối tác:", ds_doi_tac)
    tu_khoa = st.text_input("🔍 Nhập mã trạm (Ví dụ: AGG0002):")
    
    # Lọc dữ liệu
    df_hien_thi = bll.filter_stations(df_data, chon_dt, tu_khoa)

    if tu_khoa and not df_hien_thi.empty:
        st.subheader(f"Kết quả tìm kiếm ({len(df_hien_thi)} trạm):")
        
        # Hiển thị danh sách trạm dưới dạng các "hàng" có nút bấm
        for idx, row in df_hien_thi.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Mã trạm:** {row['Matram']} | **Địa chỉ:** {row.get('Unnamed: 3', 'N/A')}")
                with col2:
                    # Tạo một "key" duy nhất cho nút bấm dựa trên mã trạm
                    if st.button("Chọn trạm này", key=f"btn_{row['Matram']}"):
                        st.session_state['tram_dang_chon'] = row['Matram']
                        st.rerun()

        # Nếu đã chọn trạm
        if 'tram_dang_chon' in st.session_state:
            tram_chon = st.session_state['tram_dang_chon']
            st.info(f"Đang cập nhật tiến độ cho trạm: **{tram_chon}**")
            
            with st.form("form_bao_cao_doi_tac"):
                chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư")
                chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm")
                chk_lap_5g = st.checkbox("⚡ Đã lắp đặt xong thiết bị 5G")
                ghi_chu_ngay = st.text_input("Ngày thực hiện (DD/MM/YYYY):", value=pd.Timestamp.now().strftime("%d/%m/%Y"))
                
                if st.form_submit_button("🚀 Gửi Báo Cáo"):
                    status, msg = bll.save_progress(tram_chon, chk_nhan_vt, chk_rai_vt, chk_lap_5g, ghi_chu_ngay)
                    if status:
                        st.success(f"🎉 {msg}")
                        del st.session_state['tram_dang_chon'] # Reset sau khi thành công
                    else:
                        st.error(msg)
    else:
        st.write("Nhập mã trạm để bắt đầu tìm kiếm...")

# (Phần 2. Trang Quản lý & Dashboard giữ nguyên)
