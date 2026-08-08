from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# 1. Cấu hình quyền và xác thực từ st.secrets
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


# 2. Kết nối và mở Google Sheets
try:
  client = connect_to_gsheets()
  # Thay "Tên_Google_Sheet_Của_Bạn" bằng tên chính xác file Google Sheets của bạn
  spreadsheet_name = "Mẫu Báo Cáo Tiến Độ T..."
  sheet = client.open(spreadsheet_name).sheet1
except Exception as e:
  st.error(
      f"Lỗi kết nối Google Sheets: {e}. Hãy kiểm tra lại tên file hoặc quyền chia"
      f" sẻ cho email: {st.secrets['gcp_service_account']['client_email']}"
  )

# 3. Giao diện nhập liệu ví dụ
st.title("Hệ thống Quản lý Tiến độ 5G")

with st.form("baocao_form"):
  station_name = st.text_input("Tên trạm / Vị trí")
  progress = st.slider("Tiến độ hoàn thành (%)", 0, 100, 0)
  note = st.text_area("Ghi chú công việc")
  submit_button = st.form_submit_button(label="Gửi báo cáo lên Google Sheets")

  if submit_button:
    if station_name:
      # Dữ liệu muốn đẩy lên hàng mới trong Google Sheets
      row_data = [station_name, f"{progress}%", note]
      sheet.append_row(row_data)
      st.success(f"Đã lưu thành công báo cáo cho trạm: {station_name}!")
    else:
      st.warning("Vui lòng nhập tên trạm trước khi gửi!")
