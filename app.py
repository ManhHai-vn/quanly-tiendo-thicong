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
  # Lấy thông tin phân quyền từ session khi đã đăng nhập thành công
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

  # Cấu hình menu theo phân quyền người dùng
  if current_role == "admin":
    menu_options = [
        "🛠️ 1. Cổng Báo cáo Tiến độ",
        "📊 2. Trang Quản lý & Dashboard",
        "📅 3. Lịch Dự Kiến Thi Công",
    ]
  else:
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

      col_dt = (
          "ĐỐI TÁC" if "ĐỐI TÁC" in df_hien_thi.columns else df_hien_thi.columns[5]
      )

      if current_role == "partner":
        st.info(
            f"🔒 Tài khoản thuộc nhà thầu **{current_partner}**: Chỉ hiển thị"
            " các trạm thuộc quyền quản lý."
        )
        if col_dt in df_hien_thi.columns:
          df_hien_thi = df_hien_thi[
              df_hien_thi[col_dt].astype(str).str.strip().str.upper()
              == current_partner.upper()
          ]
      else:
        ds_doi_tac = ["Tất cả"] + list(df_hien_thi[col_dt].dropna().unique())
        chon_dt = st.selectbox(
            "🏢 Lọc theo tên Đối tác (Admin):", ds_doi_tac
        )
        if chon_dt != "Tất cả" and col_dt in df_hien_thi.columns:
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
            placeholder=(
                "-- Nhấp vào đây để chọn hoặc gõ tìm kiếm mã trạm thuộc quyền --"
            ),
        )

        if tram_chon_full:
          tram_chon = tram_chon_full.split(" — ")[0]
          phuong_hien_tai = tram_chon_full.split(" — ")[1]

          row_hien_tai = df_hien_thi[
              df_hien_thi["Matram"].astype(str) == str(tram_chon)
          ].iloc[0]

          def check_da_lam(ten_cot):
            if ten_cot in row_hien_tai:
              val = str(row_hien_tai[ten_cot]).strip()
              return val != "" and val.lower() != "nan" and val != "None"
            return False

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
        else:
          st.warning("Vui lòng chọn hoặc gõ tìm mã trạm để tiếp tục.")
      else:
        st.warning("Không tìm thấy trạm nào thuộc quyền quản lý của bạn.")
    else:
      st.warning("Đang tải dữ liệu từ Google Sheets.")

  elif page == "📊 2. Trang Quản lý & Dashboard" and current_role == "admin":
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

  elif page == "📅 3. Lịch Dự Kiến Thi Công":
    st.title("📅 QUẢN LÝ & LẬP LỊCH DỰ KIẾN THI CÔNG")
    st.markdown("---")

    with st.form("form_lap_lich"):
      st.markdown("### 📝 Thêm lịch dự kiến mới:")
      col1, col2, col3 = st.columns(3)

      with col1:
        ngay_du_kien = st.date_input("Chọn ngày dự kiến:")
      with col2:
        # Nếu là nhà thầu, chỉ hiện danh sách trạm của nhà thầu đó
        if current_role == "partner":
          df_Cua_Partner = df_data[
              df_data[col_dt].astype(str).str.strip().str.upper()
              == current_partner.upper()
          ]
          list_ma_tram = (
              df_Cua_Partner["Matram"].dropna().tolist()
              if not df_Cua_Partner.empty
              else []
          )
        else:
          list_ma_tram = (
              df_data["Matram"].dropna().tolist() if not df_data.empty else []
          )

        tram_du_kien = st.selectbox("Chọn trạm dự kiến:", list_ma_tram)
      with col3:
        so_doi_thi_cong = st.number_input(
            "Số đội thi công:", min_value=1, max_value=20, value=1
        )

      submit_lich = st.form_submit_button("🚀 Lưu Lịch Dự Kiến")

      if submit_lich:
        ngay_str = ngay_du_kien.strftime("%d/%m/%Y")
        status, msg = bll.tao_lich_du_kien(
            ngay_str,
            tram_du_kien,
            so_doi_thi_cong,
            st.session_state["username"],
        )
        if status:
          st.success(f"🎉 {msg}")
          st.rerun()
        else:
          st.error(msg)

    st.markdown("---")
    st.markdown("### 📋 Danh sách lịch dự kiến đã đăng ký")
    df_lich = bll.get_lich_du_kien()
    if not df_lich.empty:
      # Nếu là partner thì chỉ lọc xem lịch của nhà thầu đó (nếu có thông tin)
      st.dataframe(df_lich, use_container_width=True, hide_index=True)
    else:
      st.info("Chưa có lịch dự kiến nào được tạo.")
