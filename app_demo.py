from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hệ thống Quản lý Tiến độ 5G", layout="wide")

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
    sheet = client.open("thi cong 5G-2026").sheet1
    data = sheet.get_all_values()
    if not data or len(data) <= 1:
      return pd.DataFrame()

    df = pd.DataFrame(data[1:], columns=data[0])
    return df
  except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
    return pd.DataFrame()


df_data = load_data()

st.sidebar.title("📌 HỆ THỐNG 5G")
page = st.sidebar.radio(
    "Chọn trang:",
    ["🛠️ 1. Cổng Báo cáo của Đối tác", "📊 2. Trang Quản lý & Dashboard"],
)

if page == "🛠️ 1. Cổng Báo cáo của Đối tác":
  st.title("🛠️ CỔNG BÁO CÁO TIẾN ĐỘ THI CÔNG - DÀNH CHO ĐỐI TÁC")
  st.markdown("---")

  if not df_data.empty and "Matram" in df_data.columns:
    col_doitac = "ĐỐI TÁC" if "ĐỐI TÁC" in df_data.columns else df_data.columns[5]
    ds_doi_tac = (
        ["Tất cả"] + list(df_data[col_doitac].dropna().unique())
        if col_doitac in df_data.columns
        else ["Tất cả"]
    )
    chon_dt = st.selectbox("🏢 Chọn tên Đối tác của bạn:", ds_doi_tac)

    df_hien_thi = df_data.copy()
    if chon_dt != "Tất cả":
      df_hien_thi = df_hien_thi[df_hien_thi[col_doitac] == chon_dt]

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
          try:
            client = connect_to_gsheets()
            sheet = client.open("thi cong 5G-2026").sheet1
            all_values = sheet.get_all_values()

            row_to_update = None
            for i, row in enumerate(all_values[1:], start=2):
              if len(row) > 1 and str(row[1]).strip() == str(tram_chon).strip():
                row_to_update = i
                break

            if row_to_update:
              if chk_nhan_vt:
                sheet.update_cell(row_to_update, 11, ghi_chu_ngay)
              if chk_rai_vt:
                sheet.update_cell(row_to_update, 12, ghi_chu_ngay)
              if chk_lap_5g:
                sheet.update_cell(row_to_update, 13, ghi_chu_ngay)

              st.cache_data.clear()
              st.success(
                  f"🎉 Đã cập nhật ngày {ghi_chu_ngay} lên Google Sheets cho"
                  f" trạm {tram_chon}!"
              )
            else:
              st.error(
                  f"Không tìm thấy mã trạm '{tram_chon}' trong file Google Sheets."
              )
          except Exception as e:
            st.error(f"Lỗi khi ghi dữ liệu: {e}")
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

    # Xác định chính xác tên cột đối tác
    col_dt_name = (
        "ĐỐI TÁC" if "ĐỐI TÁC" in df_data.columns else df_data.columns[5]
    )

    if col_dt_name in df_data.columns and "Lắp TB 5G" in df_data.columns:
      # Lọc các dòng có tên đối tác hợp lệ
      df_dt = df_data[
          df_data[col_dt_name].notna()
          & (df_data[col_dt_name].astype(str).str.strip() != "")
          & (df_data[col_dt_name].astype(str).str.lower() != "nan")
      ]

      if not df_dt.empty:
        summary_df = (
            df_dt.groupby(col_dt_name)
            .agg(
                Tong_Giao=("Matram", "count"),
                Da_Lap_Dat=(
                    "Lắp TB 5G",
                    lambda x: x.dropna()
                    .loc[
                        (x.astype(str).str.strip() != "")
                        & (x.astype(str).str.lower() != "nan")
                    ]
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
                col_dt_name: "Tên Đối Tác",
                "Tong_Giao": "Tổng Trạm Được Giao",
                "Da_Lap_Dat": "Đã Lắp Đặt 5G",
                "Ti_Le_Hien_Thi": "Tỷ Lệ Hoàn Thành",
            }
        )

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
        st.info("Chưa có dữ liệu đối tác được phân bổ chi tiết.")
    else:
      st.warning("Không tìm thấy cột đối tác hoặc cột Lắp TB 5G.")

    st.markdown("---")
    st.markdown("### 📋 Toàn bộ dữ liệu hệ thống (Đồng bộ từ Google Sheets)")
    if st.button("🔄 Làm mới dữ liệu"):
      st.cache_data.clear()
      st.rerun()
    st.dataframe(df_data, use_container_width=True)
  else:
    st.warning("Chưa có dữ liệu.")
