if tram_chon_full:
          tram_chon = tram_chon_full.split(" — ")[0]
          phuong_hien_tai = tram_chon_full.split(" — ")[1]

          # Lấy dòng dữ liệu hiện tại của trạm này từ DataFrame
          row_hien_tai = df_hien_thi[
              df_hien_thi["Matram"].astype(str) == str(tram_chon)
          ].iloc[0]

          # Kiểm tra các mốc đã hoàn thành từ Google Sheets (ví dụ: cột K, L, M hoặc theo tên cột thực tế của bạn)
          # Giả định dữ liệu cũ nếu có giá trị (không rỗng/không phải nan) nghĩa là đã hoàn thành
          def check_da_lam(ten_cot):
            if ten_cot in row_hien_tai:
              val = str(row_hien_tai[ten_cot]).strip()
              return val != "" and val.lower() != "nan" and val != "None"
            return False

          # Thay thế bằng tên cột thực tế trong Google Sheets của bạn cho 3 mốc:
          # Ví dụ: Nhận vật tư, Rải thiết bị, Lắp TB 5G
          da_nhan = check_da_lam(
              "Nhận VT" if "Nhận VT" in df_hien_thi.columns else df_hien_thi.columns[10]
          )
          da_rai = check_da_lam(
              "Rải TB" if "Rải TB" in df_hien_thi.columns else df_hien_thi.columns[11]
          )
          da_lap = check_da_lam(
              "Lắp TB 5G"
              if "Lắp TB 5G" in df_hien_thi.columns
              else df_hien_thi.columns[12]
          )

          # Thông báo ngày lắp đặt xong nếu đã có
          ngay_lap_dat_cu = (
              str(row_hien_tai["Lắp TB 5G"])
              if da_lap and "Lắp TB 5G" in row_hien_tai
              else ""
          )

          st.info(
              f"📍 Đang thao tác cho Trạm: **{tram_chon}** — Phường/Xã:"
              f" **{phuong_hien_tai}**"
          )
          if da_lap and ngay_lap_dat_cu:
            st.success(
                f"⚡ Trạm này đã hoàn thành lắp đặt thiết bị 5G vào ngày:"
                f" **{ngay_lap_dat_cu}**"
            )

          with st.form("form_bao_cao_doi_tac"):
            st.markdown(
                "### Tích chọn hoặc cập nhật các mốc tiến độ hoàn thành:"
            )

            # Gán trạng thái checked sẵn nếu dữ liệu cũ đã có
            chk_nhan_vt = st.checkbox("📦 Đối tác đã nhận vật tư", value=da_nhan)
            chk_rai_vt = st.checkbox(
                "🚚 Đã rải thiết bị đến trạm", value=da_rai
            )
            chk_lap_5g = st.checkbox(
                "⚡ Đã lắp đặt xong thiết bị 5G", value=da_lap
            )

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
