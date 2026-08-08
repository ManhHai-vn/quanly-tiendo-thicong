from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

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


try:
  client = connect_to_gsheets()
  spreadsheet_name = "thi cong 5G-2026"
  sheet = client.open(spreadsheet_name).sheet1
except Exception as e:
  st.error(f"Lỗi kết nối Google Sheets: {e}")

st.title("Hệ thống Quản lý Tiến độ 5G")

tab_quanly, tab_baocaongay = st.tabs(["📊 Quản lý", "📅 Báo cáo ngày"])

with tab_quanly:
  with st.form("milestone_form"):
    station_code = st.text_input("Mã trạm / Vị trí", value="KGG0250-11")

    st.markdown("### Tích chọn các mốc đã hoàn thành:")
    step1 = st.checkbox("📦 Đối tác đã nhận vật tư", value=True)
    step2 = st.checkbox("🚚 Đã rải thiết bị đến trạm", value=True)
    step3 = st.checkbox("⚡ Đã lắp đặt xong thiết bị 5G", value=True)

    default_date = datetime.now().strftime("%d/%m/%Y")
    date_str = st.text_input(
        "Nhập ngày thực hiện (DD/MM/YYYY):", value=default_date
    )

    submit_button = st.form_submit_button(label="🚀 Gửi Báo Cáo Tiến Độ")

    if submit_button:
      if station_code:
        row_data = [
            station_code,
            "Đã nhận" if step1 else "Chưa",
            "Đã rải" if step2 else "Chưa",
            "Đã lắp" if step3 else "Chưa",
            date_str,
        ]
        sheet.append_row(row_data)
        st.success(f"Đã ghi nhận báo cáo cho trạm {station_code}!")
      else:
        st.warning("Vui lòng nhập mã trạm hoặc vị trí!")

with tab_baocaongay:
  st.subheader("📅 Dữ liệu báo cáo trên Google Sheets")

  if st.button("Tải lại dữ liệu"):
    st.cache_data.clear()

  try:
    data = sheet.get_all_values()
    if data and len(data) > 0:
      df = pd.DataFrame(data[1:], columns=data[0])
      st.dataframe(df, use_container_width=True)
    else:
      st.info("Hiện tại chưa có dữ liệu nào trong bảng.")
  except Exception as e:
    st.error(f"Không thể đọc dữ liệu: {e}")
