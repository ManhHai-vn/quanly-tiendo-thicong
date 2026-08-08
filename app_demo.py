from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# 1. Cấu hình quyền và kết nối Google Sheets
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
  st.error(
      f"Lỗi kết nối Google Sheets: {e}. Hãy kiểm tra lại tên file hoặc quyền chia"
      f" sẻ cho email: {st.secrets['gcp_service_account']['client_email']}"
  )

# 2. Tiêu đề ứng dụng
st.title("Hệ thống Quản lý Tiến độ 5G")

# 3. Tạo 2 Tab chính
tab_quanly, tab_baocaongay = st.tabs(["📊 Quản lý", "📅 Báo cáo ngày"])

# --- TAB 1: QUẢN LÝ (Nhập liệu) ---
with tab_quanly:
  st.subheader("Nhập thông tin tiến độ trạm")

  with st.form("baocao_form"):
    station_name = st.text_input("Tên trạm / Vị trí (VD: KGG0250)")
    progress = st.slider("Tiến độ hoàn thành (%)", 0, 100, 0)
    note = st.text_area("Ghi chú công việc")
    submit_button = st.form_submit_button(label="Gửi báo cáo lên Google Sheets")

    if submit_button:
      if station_name:
        row_data = [station_name, f"{progress}%", note]
        sheet.append_row(row_data)
        st.success(f"Đã lưu thành công báo cáo cho trạm: {station_name}!")
      else:
        st.warning("Vui lòng nhập tên trạm trước khi gửi!")

# --- TAB 2: BÁO CÁO NGÀY (Xem dữ liệu từ Google Sheets) ---
with tab_baocaongay:
  st.subheader("Dữ liệu báo cáo hiện tại trên Google Sheets")

  if st.button("Tải lại dữ liệu"):
    st.cache_data.clear()

  try:
    # Lấy toàn bộ dữ liệu từ Sheet
    data = sheet.get_all_records()
    if data:
      st.dataframe(data, use_container_width=True)
    else:
      st.info("Hiện tại chưa có dữ liệu nào trong bảng.")
  except Exception as e:
    # Trường hợp sheet chưa có tiêu đề cột dạng chuẩn, lấy dạng danh sách thuần
    try:
      raw_data = sheet.get_all_values()
      if raw_data:
        import pandas as pd

        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        st.dataframe(df, use_container_width=True)
      else:
        st.info("Bảng dữ liệu trống.")
    except Exception as ex:
      st.error(f"Không thể đọc dữ liệu từ bảng: {ex}")
