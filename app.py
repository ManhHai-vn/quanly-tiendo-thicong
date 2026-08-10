from datetime import datetime
import io
from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

# ... (các phần code trước giữ nguyên)

# [ĐOẠN CODE THAY THẾ CHO PHẦN TRANG QUẢN LÝ & DASHBOARD TRONG app.py]

if page == "📊 2. Trang Quản lý & Dashboard" and current_role == "admin":
  st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
  st.markdown("---")

  if not df_data.empty:
    tong_tram = len(df_data)
    st.metric(label="📊 Tổng số trạm trong dự án", value=tong_tram)

    st.markdown("---")
    st.markdown("### 📈 BÁO CÁO TIẾN ĐỘ LẮP ĐẶT THEO TỪNG ĐỐI TÁC")

    # 1. Hiển thị bảng tổng hợp (như hệ thống cũ)
    summary_df = bll.process_partner_summary(df_data)
    if not summary_df.empty:
      st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # =====================================================================
    # 2. KHU VỰC THẺ THỐNG KÊ CHI TIẾT THEO MẪU YÊU CẦU
    # =====================================================================

    # Nút Xuất excel tổng
    col_btn_tong, _ = st.columns([2, 8])
    with col_btn_tong:
      # Tạo file Excel tổng trong bộ nhớ để tải về
      output_tong = io.BytesIO()
      with pd.ExcelWriter(output_tong, engine="xlsxwriter") as writer:
        df_data.to_excel(writer, index=False, sheet_name="TongHop")
      output_tong.seek(0)

      st.download_button(
        label="📥 Xuất excel tổng",
        data=output_tong,
        file_name=f"BaoCao_TongHop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tự động lấy danh sách các đối tác từ dữ liệu
    ds_doi_tac_thuc_te = []
    if col_dt and col_dt in df_data.columns:
      ds_doi_tac_thuc_te = [
          x for x in df_data[col_dt].dropna().unique() if str(x).strip() != ""
      ]

    # Chia các thẻ đối tác thành các cột (ví dụ mỗi hàng 2 đối tác)
    if ds_doi_tac_thuc_te:
      cols = st.columns(2)
      for idx, doi_tac in enumerate(ds_doi_tac_thuc_te):
        with cols[idx % 2]:
          # Lọc dữ liệu của riêng đối tác này
          df_dt = df_data[df_data[col_dt].astype(str).str.strip().str.upper() == str(doi_tac).upper()]
          
          tong_giao = len(df_dt)
          
          # Đếm tiến độ dựa trên các cột trạng thái thực tế
          def count_done(col_name):
            if col_name in df_dt.columns:
              return len(df_dt[df_dt[col_name].astype(str).str.strip() != "" & (df_dt[col_name].astype(str).str.lower() != "nan") & (df_dt[col_name].astype(str).str.lower() != "none")])
            return 0

          nhan_tb = count_done("Nhận VT" if "Nhận VT" in df_dt.columns else "")
          rai_tb = count_done("Rải TB" if "Rải TB" in df_dt.columns else "")
          lap_tb = count_done("Lắp TB 5G" if "Lắp TB 5G" in df_dt.columns else "")
          ngay_hien_tai = datetime.now().strftime("%d/%m/%Y")

          # Hiển thị khung (container) giao diện theo mẫu
          with st.container(border=True):
            st.markdown(f"#### **Đối tác: {doi_tac}**")
            st.markdown(f"📅 **Ngày:** {ngay_hien_tai}")
            st.markdown(f"📋 **Tổng trạm đã giao:** {tong_giao}")
            st.markdown(f"📦 **Nhận thiết bị:** {nhan_tb}/{tong_giao}")
            st.markdown(f"🚚 **Rải thiết bị:** {rai_tb}/{tong_giao}")
            st.markdown(f"⚡ **Lắp đặt thiết bị:** {lap_tb}/{tong_giao}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Nút xuất excel riêng cho đối tác này
            output_dt = io.BytesIO()
            with pd.ExcelWriter(output_dt, engine='xlsxwriter') as writer:
                df_dt.to_excel(writer, index=False, sheet_name=str(doi_tac))
            output_dt.seek(0)
            
            st.download_button(
                label=f"📥 Xuất excel ({doi_tac})",
                data=output_dt,
                file_name=f"BaoCao_{doi_tac}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"btn_excel_{doi_tac}",
                use_container_width=True
            )
    else:
      st.info("Chưa có dữ liệu đối tác để phân chia thẻ thống kê.")

    st.markdown("---")
    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống")
    if st.button("🔄 Làm mới dữ liệu"):
      st.cache_data.clear()
      st.rerun()
    st.dataframe(df_data, use_container_width=True)
