from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G", layout="wide")

# Cấu hình kết nối Google Sheets qua gspread và st.secrets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def connect_to_gsheets():
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


@st.cache_data(ttl=5)
def load_data():
  try:
    client = connect_to_gsheets()
    spreadsheet_name = "thi cong 5G-2026"  # Tên file Google Sheets của bạn
    sheet = client.open(spreadsheet_name).sheet1
    data = sheet.get_all_values()
    if not data or len(data) <= 1:
      return pd.DataFrame()

    df = pd.DataFrame(data[1:], columns=data[0])
    cols_chuan = [
        "STT",
        "Matram",
        "Ma5G",
        "KhuVuc",
        "GiaoTrienKhai",
        "DoiTac",
        "TrangThai",
        "MaCongTrinh",
        "Network",
        "VietPhieu",
        "DoiTac_NhanVT",
        "RaiVT",
        "LapTB_5G",
    ]
    if len(df.columns) >= len(cols_chuan):
      df.columns = cols_chuan + list(df.columns[len(cols_chuan) :])
    return df
  except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
    return pd.DataFrame()


df_data = load_data()

# --- MENU ĐIỀU HƯỚNG ---
st.sidebar.title("📌 HỆ THỐNG 5G")
page = st.sidebar.radio(
    "Chọn trang:",
    ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"],
)

# ==========================================
# TRANG 1: DÀNH CHO ĐỐI TÁC BÁO CÁO TIẾN ĐỘ
# ==========================================
if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
  st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
  st.markdown(
      "Kỹ sư/Đối tác chọn trạm và cập nhật tình hình thực hiện hiện trường."
  )
  st.markdown("---")

  if not df_data.empty and "Matram" in df_data.columns:
    ds_doi_tac = (
        ["Tất cả"] + list(df_data["DoiTac"].dropna().unique())
        if "DoiTac" in df_data.columns
        else ["Tất cả"]
    )
    chon_dt = st.selectbox("🏢 Chọn tên Đối tác của bạn:", ds_doi_tac)

    df_hien_thi = df_data.copy()
    if chon_dt != "Tất cả":
      df_hien_thi = df_hien_thi[df_hien_thi["DoiTac"] == chon_dt]

    tu_khoa = st.text_input("🔍 Nhập mã trạm cần tìm (VD: AGG0002):")
    if tu_khoa:
      df_hien_thi = df_hien_thi[
          df_hien_thi["Matram"]
          .astype(str)
          .str.contains(tu_khoa, case=False, na=False)
      ]

    if not df_hien_thi.empty:
      list_tram = df_hien_thi["Matram"].tolist()
      tram_chon = st.selectbox("📌 Chọn chính xác Mã trạm:", list_tram)

      thong_tin_tram = df_data[df_data["Matram"] == tram_chon].iloc[0]
      st.info(
          f"Đang thao tác cho Trạm: **{tram_chon}** | Khu vực:"
          f" {thong_tin_tram.get('KhuVuc', 'N/A')}"
      )

      with st.form("form_bao_cao_doi_tac"):
        st.markdown("### Tích chọn các mốc đã hoàn thành:")

        val_nhan_vt = pd.notna(
            thong_tin_tram.get("DoiTac_NhanVT")
        ) and str(thong_tin_tram.get("DoiTac_NhanVT")) != ""
        val_rai_vt = pd.notna(thong_tin_tram.get("RaiVT")) and str(
            thong_tin_tram.get("RaiVT")
        ) != ""
        val_lap_5g = pd.notna(thong_tin_tram.get("LapTB_5G")) and str(
            thong_tin_tram.get("LapTB_5G")
        ) != ""

        chk_nhan_vt = st.checkbox(
            "📦 Đối tác đã nhận vật tư", value=val_nhan_vt
        )
        chk_rai_vt = st.checkbox("🚚 Đã rải thiết bị đến trạm", value=val_rai_vt)
        chk_lap_5g = st.checkbox(
            "⚡ Đã lắp đặt xong thiết bị 5G", value=val_lap_5g
        )

        ghi_chu_ngay = st.text_input(
            "Nhập ngày thực hiện (DD/MM/YYYY):",
            value=pd.Timestamp.now().strftime("%d/%m/%Y"),
        )

        submit_bao_cao = st.form_submit_button("🚀 Gửi Báo Cáo Tiến Độ")

        if submit_bao_cao:
          try:
            client = connect_to_gsheets()
            sheet = client.open("thi cong 5G-2026").sheet1
            all_values = sheet.get_all_values()
            header = all_values[0]

            # Xác định vị trí cột
            idx_matram = header.index("Matram") if "Matram" in header else 1
            idx_nhanvt = (
                header.index("DoiTac_NhanVT")
                if "DoiTac_NhanVT" in header
                else None
            )
            idx_raitv = header.index("RaiVT") if "RaiVT" in header else None
            idx_laptb = header.index("LapTB_5G") if "LapTB_5G" in header else None

            # Tìm dòng chứa mã trạm
            row_to_update = None
            for i, row in enumerate(all_values[1:], start=2):
              if len(row) > idx_matram and row[idx_matram] == tram_chon:
                row_to_update = i
                break

            if row_to_update:
              if idx_nhanvt is not None:
                sheet.update_cell(
                    row_to_update,
                    idx_nhanvt + 1,
                    f"Đã nhận ({ghi_chu_ngay})" if chk_nhan_vt else "",
                )
              if idx_raitv is not None:
                sheet.update_cell(
                    row_to_update,
                    idx_raitv + 1,
                    f"Đã rải ({ghi_chu_ngay})" if chk_rai_vt else "",
                )
              if idx_laptb is not None:
                sheet.update_cell(
                    row_to_update,
                    idx_laptb + 1,
                    f"Đã lắp ({ghi_chu_ngay})" if chk_lap_5g else "",
                )

              st.cache_data.clear()
              st.success(
                  f"🎉 Đã cập nhật thành công trực tiếp lên Google Sheets cho"
                  f" trạm {tram_chon}!"
              )
            else:
              st.error("Không tìm thấy dòng trạm này trong file Google Sheets.")
          except Exception as e:
            st.error(f"Lỗi khi ghi dữ liệu lên Google Sheets: {e}")
    else:
      st.warning("Không tìm thấy trạm phù hợp.")
  else:
    st.warning("Đang tải hoặc chưa có dữ liệu từ Google Sheets.")

# ==========================================
# TRANG 2: DÀNH CHO QUẢN LÝ DỮ LIỆU & DASHBOARD
# ==========================================
elif page == "📊 2. Trang Quản lý & Dashboard":
  st.title("📊 TRANG QUẢN LÝ DỮ LIỆU & ĐIỀU HÀNH DỰ ÁN")
  st.markdown(
      "Dành cho Chỉ huy trưởng/Quản lý theo dõi tổng quan tiến độ toàn dự án."
  )
  st.markdown("---")

  if not df_data.empty:
    tong_tram = len(df_data)
    col1, col2 = st.columns(2)
    with col1:
      st.metric(label="Tổng số trạm trong dự án", value=tong_tram)

    st.markdown("### 📈 Báo cáo Lắp đặt theo từng Đối tác")
    if "DoiTac" in df_data.columns and "LapTB_5G" in df_data.columns:
      df_dt = df_data[
          df_data["DoiTac"].notna()
          & (df_data["DoiTac"].astype(str).str.strip() != "")
      ]
      summary_df = (
          df_dt.groupby("DoiTac")
          .agg(
              Tong_Giao=("Matram", "count"),
              Da_Lap_Dat=(
                  "LapTB_5G",
                  lambda x: x.dropna()
                  .loc[x.astype(str).str.strip() != ""]
                  .count(),
              ),
          )
          .reset_index()
      )

      summary_df["Ty_Le_%"] = (
          summary_df["Da_Lap_Dat"] / summary_df["Tong_Giao"] * 100
      ).round(1)
      summary_df["Ti_Le_Hien_Thi"] = summary_df["Ty_Le_%"].astype(str) + "%"

      summary_df = summary_df.rename(
          columns={
              "DoiTac": "Tên Đối Tác",
              "Tong_Giao": "Tổng Trạm Đã Giao",
              "Da_Lap_Dat": "Đã Lắp Đặt",
              "Ti_Le_Hien_Thi": "Tỷ Lệ Hoàn Thành",
          }
      )

      st.dataframe(
          summary_df[
              [
                  "Tên Đối Tác",
                  "Tổng Trạm Đã Giao",
                  "Đã Lắp Đặt",
                  "Tỷ Lệ Hoàn Thành",
              ]
          ],
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.warning("Chưa xác định được cột 'DoiTac' hoặc 'LapTB_5G' để tổng hợp.")

    st.markdown("---")
    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống (Đồng bộ từ Google Sheets)")
    if st.button("🔄 Làm mới dữ liệu"):
      st.cache_data.clear()
      st.rerun()
    st.dataframe(df_data, use_container_width=True)
  else:
    st.warning("Chưa có dữ liệu hoặc không thể kết nối tới Google Sheets.")
