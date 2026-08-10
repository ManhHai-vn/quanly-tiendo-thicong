import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st


class BusinessLogicLayer:

  def __init__(self):
    self.scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
      creds_dict = dict(st.secrets["gcp_service_account"])
      self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
          creds_dict, self.scope
      )
      self.client = gspread.authorize(self.creds)
      self.sheet = self.client.open("thi cong 5G-2026").sheet1
    except Exception as e:
      st.error(f"Lỗi kết nối Google Sheets: {e}")
      self.sheet = None

  def get_raw_data(self):
    if not self.sheet:
      return pd.DataFrame()
    data = self.sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

  def process_partner_summary(self, df):
    if df.empty:
      return pd.DataFrame()

    col_dt = None
    for c in ["ĐỐI TÁC", "Đối tác", "doi_tac"]:
      if c in df.columns:
        col_dt = c
        break
    if not col_dt and len(df.columns) > 5:
      col_dt = df.columns[5]

    if not col_dt or col_dt not in df.columns:
      return pd.DataFrame()

    # Chỉ lấy các dòng có tên đối tác thực tế (ví dụ: VCC, VTK, loại bỏ giá trị rỗng/nan/chưa giao)
    df_clean = df[
        df[col_dt].notna()
        & (df[col_dt].astype(str).str.strip() != "")
        & (df[col_dt].astype(str).str.lower() != "nan")
        & (df[col_dt].astype(str).str.lower() != "none")
    ].copy()

    summary_list = []
    doi_tacs = df_clean[col_dt].dropna().unique()

    total_giao = 0
    total_lap = 0

    for dt in doi_tacs:
      df_dt = df_clean[
          df_clean[col_dt].astype(str).str.strip().str.upper()
          == str(dt).upper()
      ]
      tong_giao = len(df_dt)

      lap_tb = 0
      if "Lắp TB 5G" in df_dt.columns:
        s = df_dt["Lắp TB 5G"].astype(str).str.strip()
        lap_tb = len(
            df_dt[
                (s != "")
                & (s.str.lower() != "nan")
                & (s.str.lower() != "none")
            ]
        )

      ty_le = round((lap_tb / tong_giao * 100), 1) if tong_giao > 0 else 0.0

      total_giao += tong_giao
      total_lap += lap_tb

      summary_list.append({
          "Tên Đối Tác": dt,
          "Tổng Trạm Được Giao": tong_giao,
          "Đã Lắp Đặt 5G": lap_tb,
          "Tỷ_Lệ_%": ty_le,
          "Tỷ Lệ Hoàn Thành": f"{ty_le}%",
      })

    summary_df = pd.DataFrame(summary_list)

    # Thêm dòng Tổng vào cuối bảng với tổng số trạm đã giao của các đối tác
    if not summary_df.empty:
      tong_ty_le = (
          round((total_lap / total_giao * 100), 1) if total_giao > 0 else 0.0
      )
      tong_row = pd.DataFrame([{
          "Tên Đối Tác": "Tổng",
          "Tổng Trạm Được Giao": total_giao,
          "Đã Lắp Đặt 5G": total_lap,
          "Tỷ_Lệ_%": tong_ty_le,
          "Tỷ Lệ Hoàn Thành": f"{tong_ty_le}%",
      }])
      summary_df = pd.concat([summary_df, tong_row], ignore_index=True)

    return summary_df

  def save_progress(
      self, tram_chon, chk_nhan_vt, chk_rai_vt, chk_lap_5g, ngay_thuc_hien
  ):
    if not self.sheet:
      return False, "Không kết nối được Google Sheets"
    try:
      cell = self.sheet.find(str(tram_chon))
      if cell:
        row = cell.row
        headers = self.sheet.row_values(1)

        if "Nhận VT" in headers:
          col_nhan = headers.index("Nhận VT") + 1
          self.sheet.update_cell(
              row, col_nhan, ngay_thuc_hien if chk_nhan_vt else ""
          )

        if "Rải TB" in headers:
          col_rai = headers.index("Rải TB") + 1
          self.sheet.update_cell(
              row, col_rai, ngay_thuc_hien if chk_rai_vt else ""
          )

        if "Lắp TB 5G" in headers:
          col_lap = headers.index("Lắp TB 5G") + 1
          self.sheet.update_cell(
              row, col_lap, ngay_thuc_hien if chk_lap_5g else ""
          )

        return True, "Cập nhật tiến độ thành công!"
      return False, "Không tìm thấy mã trạm."
    except Exception as e:
      return False, f"Lỗi: {e}"

  def save_lich_du_kien(self, tram_chon, ngay_du_kien, so_doi):
    if not self.sheet:
      return False, "Không kết nối được Google Sheets"
    try:
      cell = self.sheet.find(str(tram_chon))
      if cell:
        row = cell.row
        headers = self.sheet.row_values(1)
        for idx, h in enumerate(headers):
          if "Ngày dự kiến" in h or "Ngày dự" in h:
            self.sheet.update_cell(row, idx + 1, ngay_du_kien)
          if "SoDoi" in h or "Số đội" in h:
            self.sheet.update_cell(row, idx + 1, so_doi)
        return True, "Cập nhật lịch thành công!"
      return False, "Không tìm thấy trạm."
    except Exception as e:
      return False, f"Lỗi: {e}"
