from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ thống Quản lý Tiến độ 5G - Beta", layout="wide"
)


@st.cache_resource
def get_bll():
  return BusinessLogicLayer()


bll = get_bll()
df_data = bll.get_raw_data()

st.sidebar.title("📌 HỆ THỐNG 5G (BETA)")
page = st.sidebar.radio(
    "Chọn trang:",
    ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"],
)

if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
  st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
  st.markdown("---")

  if not df_data.empty and "Matram" in df_data.columns:
    ds_doi_tac = bll.get_partners(df_data)
    chon_dt = st.selectbox("🏢 Chọn tên Đối tác của bạn:", ds_doi_tac)

    tu_khoa = st.text_input("🔍 Nhập mã trạm cần tìm (VD: AGG0002):")
    df_hien_thi = bll.filter_stations(df_data, chon_dt, tu_khoa)

    if not df_hien_thi.empty:
      list_tram = df_hien_thi["Matram"].tolist()
      tram_chon = st.selectbox("📌 Chọn chính xác Mã trạm:", list_tram)

      st.info(f"Đang thao tác cho Trạm: **{tram_chon}**")

      with st.form("form_bao_cao_doi_tac"):
        st.markdown("### Tích chọn các mốc đã hoàn thành:")
        chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư")
        chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm")
        chk_lap_5g = st.checkbox("⚡ Đã lắp đặt xong thiết bị 5G")

        ghi_chu_ngay = st.text_input(
            "Nhập ngày thực hiện (DD/MM/YYYY):",
            value=pd.Timestamp.now().strftime("%d/%m/%Y"),
        )
        submit_bao_cao = st.form_submit_button("🚀 Gửi Báo Cáo Tiến Độ")

        if submit_bao_cao:
          status, msg = bll.save_progress(
              tram_chon,
              chk_nhan_vt,
              chk_rai_vt,
              chk_lap_5g,
              ghi_chu_ngay,
          )
          if status:
            st.success(f"🎉 {msg}")
            st.rerun()
          else:
            st.error(msg)
    else:
      st.warning("Không tìm thấy trạm phù hợp.")
  else:
    st.warning("Đang tải dữ liệu từ Google Sheets.")

elif page == "📊 2. Trang Quản lý & Dashboard":
  st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
  if not df_data.empty:
    tong_tram = len(df_data)
    col1, col2 = st.columns(2)
    with col1:
      st.metric(label="Tổng số trạm trong dự án", value=tong_tram)

    st.markdown("---")
    st.markdown("### 📈 BÁO CÁO TIẾN ĐỘ LẮP ĐẶT THEO TỪNG ĐỐI TÁC")

    summary_df = bll.process_partner_summary(df_data)
    if not summary_df.empty:
      st.dataframe(
          summary_df[
              [
                  "Tên Đối Tác",
                  "Tổng Trạm Được Giao",
                  "Đã Lắp Đặt 5G",
                  "Tỷ Lệ Hoàn Thành",
              ]
          ],
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.info("Chưa có dữ liệu đối tác để tổng hợp.")

    st.markdown("---")
    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống (Đồng bộ từ Google Sheets)")
    if st.button("🔄 Làm mới dữ liệu"):
      st.cache_data.clear()
      st.rerun()
    st.dataframe(df_data, use_container_width=True)
  else:
    st.warning("Chưa có dữ liệu.")