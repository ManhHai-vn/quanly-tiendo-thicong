from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st


class DataAccessLayer:

  def __init__(self, spreadsheet_name="thi cong 5G-2026"):
    self.spreadsheet_name = spreadsheet_name
    self.scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

  def _get_client(self):
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=self.scope)
    return gspread.authorize(creds)

  def fetch_data(self):
    try:
      client = self._get_client()
      sheet = client.open(self.spreadsheet_name).sheet1
      data = sheet.get_all_values()
      if not data or len(data) <= 1:
        return pd.DataFrame()
      return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
      st.error(f"Lỗi kết nối dữ liệu: {e}")
      return pd.DataFrame()

  def update_station_progress(self, tram_chon, col_indices, ngay_thuc_hien):
    try:
      client = self._get_client()
      sheet = client.open(self.spreadsheet_name).sheet1
      all_values = sheet.get_all_values()

      row_to_update = None
      for i, row in enumerate(all_values[1:], start=2):
        if len(row) > 1 and str(row[1]).strip() == str(tram_chon).strip():
          row_to_update = i
          break

      if row_to_update:
        for col_idx in col_indices:
          sheet.update_cell(row_to_update, col_idx, ngay_thuc_hien)
        return True
      return False
    except Exception as e:
      st.error(f"Lỗi ghi dữ liệu: {e}")
      return False
      # Thêm vào trong class DataAccessLayer (file dal.py)

    def fetch_du_kien(self):
      try:
        client = self._get_client()
        sheet = client.open(self.spreadsheet_name).worksheet(
            "DuKienThiCong"
        )  # Gọi sheet riêng
        data = sheet.get_all_values()
        if not data or len(data) <= 1:
          return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
      except Exception as e:
        # Nếu chưa có sheet DuKienThiCong thì trả về DataFrame trống tránh lỗi crash app
        return pd.DataFrame()

    def save_du_kien(self, ngay, matram, so_doi, nguoi_tao):
      try:
        client = self._get_client()
        sheet = client.open(self.spreadsheet_name).worksheet("DuKienThiCong")
        sheet.append_row([ngay, matram, so_doi, nguoi_tao])
        return True
      except Exception as e:
        st.error(f"Lỗi lưu lịch dự kiến: {e}")
        return False
