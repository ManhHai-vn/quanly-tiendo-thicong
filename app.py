from datetime import datetime
import io
from bll import BusinessLogicLayer
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ thống Quản lý Tiến độ 5G - Phân quyền", layout="wide"
)


@st.cache_resource
def get_bll():
  return BusinessLogicLayer()


bll = get_bll()
df_data = bll.get_raw_data()

col_dt = None
if not df_data.empty:
  for c in ["ĐỐI TÁC", "Đối tác", "doi_tac"]:
    if c in df_data.columns:
      col_dt = c
      break
  if not col_dt and len(df_data.columns) > 5:
    col_dt = df_data.columns[5]

# =====================================================================
# HỆ THỐNG XÁC THỰC VÀ PHÂN QUYỀN (LOGIN & RBAC)
# =====================================================================
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False
  st.session_state["username"] = ""
  st.session_state["role"] = ""
  st.session_state["partner_name"] = ""


def login_screen():
  st.title("🔐 ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ 5G")
  st.markdown("---")
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    with st.form("login_form"):
      st.markdown("### Vui lòng đăng nhập để tiếp tục")
      username = st.text_input("Tên đăng nhập (Username):")
      password = st.text_input("Mật khẩu (Password):", type="password")
      submit = st.form_submit_button("Đăng Nhập", use_container_width=True)

      if submit:
        users_db = {
            "admin_agg": {
                "pass": "admin123",
                "role": "admin",
                "partner": "Tất cả",
            },
            "vtk": {"pass": "vtk123", "role": "partner", "partner": "VTK"},
            "vcc": {"pass": "vcc123", "role": "partner", "partner": "VCC"},
        }

        if username in users_db and users_db[username]["pass"] == password:
          st.session_state["authenticated"] = True
          st.session_state["username"] = username
          st.session_state["role"] = users_db[username]["role"]
          st.session_state["partner_name"] = users_db[username]["partner"]
          st.success("Đăng nhập thành công!")
          st.rerun()
        else:
          st.error("Sai tên đăng nhập hoặc mật khẩu!")


if not st.session_state["authenticated"]:
  login_screen()
else:
  current_role = st.session_state["role"]
  current_partner = st.session_state["partner_name"]

  st.sidebar.title("📌 HỆ THỐNG 5G (BETA)")
  st.sidebar.info(
      f"👤 Đang đăng nhập: **{st.session_state['username'].upper()}**\n\n"
      f"🏢 Quyền hạn: **{'Admin Hệ thống' if current_role == 'admin' else 'Nhà thầu ' + current_partner}**"
  )

  if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["partner_name"] = ""
    st.rerun()

  menu_options = [
      "🛠️ 1. Cổng Báo cáo Tiến độ",
      "📊 2. Trang Quản lý & Dashboard",
      "📅 3. Lịch Dự Kiến Thi Công",
  ]
  if current_role != "admin":
    menu_options = [
        "🛠️ 1. Cổng Báo cáo Tiến độ",
        "📅 3. Lịch Dự Kiến Thi Công",
    ]

  page = st.sidebar.radio("Chọn trang:", menu_options)

  if page == "🛠️ 1. Cổng Báo cáo Tiến độ":
    st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG")
    st.markdown("---")

    if not df_data.empty and "Matram" in df_data.columns:
      df_hien_thi = df_data.copy()
      df_hien_thi = df_hien_thi[
          df_hien_thi["Matram"].notna()
          & (df_hien_thi["Matram"].astype(str).str.strip() != "")
          & (df_hien_thi["Matram"].astype(str).str.lower() != "nan")
      ]

      if current_role == "partner":
        st.info(
            f"🔒 Tài khoản thuộc nhà thầu **{current_partner}**: Chỉ hiển thị"
            " các trạm thuộc quyền quản lý."
        )
        if col_dt and col_dt in df_hien_thi.columns:
          df_hien_thi = df_hien_thi[
              df_hien_thi[col_dt].astype(str).str.strip().str.upper()
              == current_partner.upper()
          ]
      else:
        ds_doi_tac = (
            ["Tất cả"] + list(df_hien_thi[col_dt].dropna().unique())
            if col_dt and col_dt in df_hien_thi.columns
            else ["Tất cả"]
        )
        chon_dt = st.selectbox(
            "🏢 Lọc theo tên Đối tác (Admin):", ds_doi_tac
        )
        if chon_dt != "Tất cả" and col_dt and col_dt in df_hien_thi.columns:
          df_hien_thi = df_hien_thi[df_hien_thi[col_dt] == chon_dt]

      st.markdown("### 📌 Chọn Mã Trạm cần báo cáo:")
      if not df_hien_thi.empty:
        col_phuong = (
            "Phường xã"
            if "Phường xã" in df_hien_thi.columns
            else df_hien_thi.columns[3]
        )
        phuong_xa_vals = df_hien_thi[col_phuong].fillna("").astype(str)

        df_hien_thi["Hien_Thi_Tram"] = (
            df_hien_thi["Matram"].astype(str) + " — " + phuong_xa_vals
        )
        list_hien_thi = df_hien_thi["Hien_Thi_Tram"].tolist()

        tram_chon_full = st.selectbox(
            "🔍 Gõ hoặc chọn Mã trạm:",
            options=list_hien_thi,
            index=None,
            placeholder="-- Nhấp vào đây để chọn hoặc gõ tìm kiếm mã trạm --",
        )

        if tram_chon_full:
          tram_chon = tram_chon_full.split(" — ")[0]
          row_hien_tai = df_hien_thi[
              df_hien_thi["Matram"].astype(str) == str(tram_chon)
          ].iloc[0]

          def check_da_lam(ten_col):
            if ten_col in row_hien_tai:
              val = str(row_hien_tai[ten_col]).strip()
              return val != "" and val.lower() != "nan" and val != "None"
            return False

          da_nhan = check_da_lam(
              "Nhận VT" if "Nhận VT" in df_hien_thi.columns else ""
          )
          da_rai = check_da_lam(
              "Rải TB" if "Rải TB" in df_hien_thi.columns else ""
          )
          da_lap = check_da_lam(
              "Lắp TB 5G" if "Lắp TB 5G" in df_hien_thi.columns else ""
          )
          da_bbnt_lap = check_da_lam(
              "BBNT Lắp đặt" if "BBNT Lắp đặt" in df_hien_thi.columns else ""
          )
          da_ps_test = check_da_lam(
              "Phát sóng Test" if "Phát sóng Test" in df_hien_thi.columns else ""
          )
          da_ps_chinh = check_da_lam(
              "Phát sóng chính thức"
              if "Phát sóng chính thức" in df_hien_thi.columns
              else ""
          )

          with st.form("form_bao_cao_doi_tac"):
            st.markdown(
                "### Tích chọn hoặc cập nhật các mốc tiến độ hoàn thành:"
            )
            chk_nhan_vt = st.checkbox(
                "📦 Đối tác đã nhận vật tư", value=da_nhan
            )
            chk_rai_vt = st.checkbox(
                "🚚 Đã rải thiết bị đến trạm", value=da_rai
            )
            chk_lap_5g = st.checkbox(
                "⚡ Đã lắp đặt xong thiết bị 5G", value=da_lap
            )

            # Các mục bổ sung riêng cho Admin
            chk_bbnt_lap = False
            chk_ps_test = False
            chk_ps_chinh = False
            if current_role == "admin":
              chk_bbnt_lap = st.checkbox(
                  "📝 Đã ký BBNT lắp đặt", value=da_bbnt_lap
              )
              chk_ps_test = st.checkbox(
                  "📡 Phát sóng test", value=da_ps_test
              )
              chk_ps_chinh = st.checkbox(
                  "🚀 Phát sóng chính thức", value=da_ps_chinh
              )

            ghi_chu_ngay = st.text_input(
                "Nhập ngày thực hiện (DD/MM/YYYY):",
                value=pd.Timestamp.now().strftime("%d/%m/%Y"),
            )
            submit_bao_cao = st.form_submit_button("🚀 Gửi Báo Cáo Tiến Độ")

            if submit_bao_cao:
              if current_role == "admin":
                status, msg = bll.save_progress(
                    tram_chon,
                    chk_nhan_vt,
                    chk_rai_vt,
                    chk_lap_5g,
                    ghi_chu_ngay,
                    chk_ps_test,
                    chk_ps_chinh,
                    chk_bbnt_lap,
                )
              else:
                status, msg = bll.save_progress(
                    tram_chon, chk_nhan_vt, chk_rai_vt, chk_lap_5g, ghi_chu_ngay
                )

              if status:
                st.success(f"🎉 {msg}")
                st.rerun()
              else:
                st.error(msg)
        else:
          st.warning("Vui lòng chọn hoặc gõ tìm mã trạm để tiếp tục.")
      else:
        st.warning("Không tìm thấy trạm nào thuộc quyền quản lý.")
    else:
      st.warning("Đang tải dữ liệu từ Google Sheets.")

  elif page == "📊 2. Trang Quản lý & Dashboard" and current_role == "admin":
    st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
    st.markdown("---")

    if not df_data.empty:
      summary_df = bll.process_partner_summary(df_data)

      tong_tram_giao_thuc_te = (
          summary_df.loc[
              summary_df["Tên Đối Tác"] != "Tổng", "Tổng Trạm Được Giao"
          ].sum()
          if not summary_df.empty
          else 0
      )

      st.metric(
          label="📊 Tổng số trạm đã giao (VCC + VTK)",
          value=tong_tram_giao_thuc_te,
      )

      st.markdown("---")
      st.markdown("### 📈 BÁO CÁO TIẾN ĐỘ LẮP ĐẶT THEO TỪNG ĐỐI TÁC")

      if not summary_df.empty:
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

      st.markdown("---")

      col_btn_tong, _ = st.columns([2, 8])
      with col_btn_tong:
        output_tong = io.BytesIO()
        with pd.ExcelWriter(output_tong) as writer:
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

      ds_doi_tac_thuc_te = []
      if col_dt and col_dt in df_data.columns:
        ds_doi_tac_thuc_te = [
            x for x in df_data[col_dt].dropna().unique() if str(x).strip() != ""
        ]

      if ds_doi_tac_thuc_te:
        cols = st.columns(2)
        for idx, doi_tac in enumerate(ds_doi_tac_thuc_te):
          with cols[idx % 2]:
            df_dt = df_data[
                df_data[col_dt].astype(str).str.strip().str.upper()
                == str(doi_tac).upper()
            ]

            tong_giao = len(df_dt)

            def count_done(col_name):
              if col_name in df_dt.columns:
                s = df_dt[col_name].astype(str).str.strip()
                return len(
                    df_dt[
                        (s != "")
                        & (s.str.lower() != "nan")
                        & (s.str.lower() != "none")
                    ]
                )
              return 0

            nhan_tb = count_done("Nhận VT" if "Nhận VT" in df_dt.columns else "")
            lap_tb = count_done(
                "Lắp TB 5G" if "Lắp TB 5G" in df_dt.columns else ""
            )
            bbnt_lap = count_done(
                "BBNT Lắp đặt" if "BBNT Lắp đặt" in df_dt.columns else ""
            )
            phat_song_test = count_done(
                "Phát sóng Test" if "Phát sóng Test" in df_dt.columns else ""
            )
            phat_song_chinh = count_done(
                "Phát sóng chính thức"
                if "Phát sóng chính thức" in df_dt.columns
                else ""
            )

            tram_chua_lap = max(0, tong_giao - lap_tb)
            ngay_hien_tai = datetime.now().strftime("%d/%m/%Y")

            with st.container(border=True):
              st.markdown(f"#### **Đối tác: {doi_tac}**")

              sub_col1, sub_col2 = st.columns([1.1, 0.9])

              with sub_col1:
                st.markdown(f"📅 **Ngày:** {ngay_hien_tai}")
                st.markdown(f"📋 **Tổng trạm đã giao:** {tong_giao}")
                st.markdown(f"📦 **Nhận thiết bị:** {nhan_tb}/{tong_giao}")
                st.markdown(f"⚡ **Lắp đặt thiết bị:** {lap_tb}/{tong_giao}")
                st.markdown(
                    f"⏳ **Trạm còn phải lắp:** {tram_chua_lap}/{tong_giao}"
                )

              with sub_col2:
                st.markdown(
                    f"📝 **Đã ký BBNT lắp đặt:**<br>`{bbnt_lap}/{lap_tb}`",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"📡 **Phát sóng test:**<br>`{phat_song_test}/{lap_tb}`",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"🚀 **Phát sóng chính thức:**<br>`{phat_song_chinh}`",
                    unsafe_allow_html=True,
                )

              st.markdown("<br>", unsafe_allow_html=True)

              output_dt = io.BytesIO()
              with pd.ExcelWriter(output_dt) as writer:
                df_dt.to_excel(writer, index=False, sheet_name=str(doi_tac))
              output_dt.seek(0)

              st.download_button(
                  label=f"📥 Xuất excel ({doi_tac})",
                  data=output_dt,
                  file_name=f"BaoCao_{doi_tac}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                  mime=(
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                  ),
                  key=f"btn_excel_{doi_tac}",
                  use_container_width=True,
              )
      else:
        st.info("Chưa có dữ liệu đối tác để phân chia thẻ thống kê.")

      st.markdown("---")
      st.markdown("### 📋 Toàn bộ dữ liệu hệ thống")
      if st.button("🔄 Làm mới dữ liệu"):
        st.cache_data.clear()
        st.rerun()
      st.dataframe(df_data, use_container_width=True)

  elif page == "📅 3. Lịch Dự Kiến Thi Công":
    st.title("📅 QUẢN LÝ & LẬP LỊCH DỰ KIẾN THI CÔNG")
    st.markdown("---")

    with st.form("form_lap_lich"):
      st.markdown("### 📝 Cập nhật lịch dự kiến cho trạm:")
      col1, col2, col3 = st.columns(3)

      with col1:
        ngay_du_kien = st.date_input("Chọn ngày dự kiến:")
      with col2:
        if current_role == "partner" and col_dt and col_dt in df_data.columns:
          df_Cua_Partner = df_data[
              df_data[col_dt].astype(str).str.strip().str.upper()
              == current_partner.upper()
          ]
          list_ma_tram = (
              df_Cua_Partner["Matram"].dropna().tolist()
              if not df_Cua_Partner.empty and "Matram" in df_Cua_Partner.columns
              else []
          )
        else:
          list_ma_tram = (
              df_data["Matram"].dropna().tolist()
              if not df_data.empty and "Matram" in df_data.columns
              else []
          )

        tram_du_kien = st.selectbox("Chọn trạm dự kiến:", list_ma_tram)
      with col3:
        so_doi_thi_cong = st.number_input(
            "Số đội thi công:", min_value=1, max_value=20, value=1
        )

      submit_lich = st.form_submit_button("🚀 Lưu Lịch Dự Kiến")

      if submit_lich:
        ngay_str = ngay_du_kien.strftime("%d/%m/%Y")
        status, msg = bll.save_lich_du_kien(
            tram_du_kien, ngay_str, so_doi_thi_cong
        )
        if status:
          st.success(f"🎉 {msg}")
          st.rerun()
        else:
          st.error(msg)

    st.markdown("---")
    st.markdown("### 📋 Danh sách trạm và lịch dự kiến hiện tại")
    if not df_data.empty:
      cols_hien_thi = [
          c
          for c in [
              "Matram",
              "Mã 5G",
              "Phường xã",
              col_dt,
              "Ngày dự kiến t...",
              "SoDoi",
          ]
          if c and c in df_data.columns
      ]
      st.dataframe(
          df_data[cols_hien_thi] if cols_hien_thi else df_data,
          use_container_width=True,
          hide_index=True,
      )
