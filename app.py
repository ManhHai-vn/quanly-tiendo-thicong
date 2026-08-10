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
      tong_giao = int(len(df_dt))

      lap_tb = 0
      if "Lắp TB 5G" in df_dt.columns:
        s = df_dt["Lắp TB 5G"].astype(str).str.strip()
        lap_tb = int(
            len(
                df_dt[
                    (s != "")
                    & (s.str.lower() != "nan")
                    & (s.str.lower() != "none")
                ]
            )
        )

      ty_le = round((lap_tb / tong_giao * 100), 1) if tong_giao > 0 else 0.0

      total_giao += tong_giao
      total_lap += lap_tb

      summary_list.append({
          "Tên Đối Tác": str(dt),
          "Tổng Trạm Được Giao": tong_giao,
          "Đã Lắp Đặt 5G": lap_tb,
          "Tỷ_Lệ_%": float(ty_le),
          "Tỷ Lệ Hoàn Thành": f"{ty_le}%",
      })

    summary_df = pd.DataFrame(summary_list)

    if not summary_df.empty:
      tong_ty_le = (
          round((total_lap / total_giao * 100), 1) if total_giao > 0 else 0.0
      )
      tong_row = {
          "Tên Đối Tác": "Tổng",
          "Tổng Trạm Được Giao": int(total_giao),
          "Đã Lắp Đặt 5G": int(total_lap),
          "Tỷ_Lệ_%": float(tong_ty_le),
          "Tỷ Lệ Hoàn Thành": f"{tong_ty_le}%",
      }
      summary_df = pd.concat(
          [summary_df, pd.DataFrame([tong_row])], ignore_index=True
      )

    return summary_df

  def save_progress(self, *args, **kwargs):
    # Xử lý tham số cực kỳ linh hoạt, chống mọi lỗi TypeError bất kể truyền thiếu hay thừa
    tram_chon = kwargs.get("tram_chon") or (args[0] if len(args) > 0 else None)
    chk_nhan_vt = kwargs.get(
        "chk_nhan_vt", args[1] if len(args) > 1 else False
    )
    chk_rai_vt = kwargs.get("chk_rai_vt", args[2] if len(args) > 2 else False)
    chk_lap_5g = kwargs.get("chk_lap_5g", args[3] if len(args) > 3 else False)
    ngay_thuc_hien = kwargs.get("ngay_thuc_hien") or (
        args[4]
        if len(args) > 4
        else pd.Timestamp.now().strftime("%d/%m/%Y")
    )
    chk_ps_test = kwargs.get("chk_ps_test", args[5] if len(args) > 5 else False)
    chk_ps_chinh = kwargs.get(
        "chk_ps_chinh", args[6] if len(args) > 6 else False
    )
    chk_bbnt_lap = kwargs.get(
        "chk_bbnt_lap", args[7] if len(args) > 7 else False
    )

    if not self.sheet:
      return False, "Không kết nối được Google Sheets"
    try:
      cell = self.sheet.find(str(tram_chon))
      if cell:
        row = cell.row
        headers = self.sheet.row_values(1)
        row_vals = self.sheet.row_values(row)

        def get_val(col_name):
          if col_name in headers:
            idx = headers.index(col_name)
            return row_vals[idx] if idx < len(row_vals) else ""
          return ""

        if "Nhận VT" in headers:
          col_nhan = headers.index("Nhận VT") + 1
          if chk_nhan_vt and not get_val("Nhận VT"):
            self.sheet.update_cell(row, col_nhan, ngay_thuc_hien)

        if "Rải TB" in headers:
          col_rai = headers.index("Rải TB") + 1
          if chk_rai_vt and not get_val("Rải TB"):
            self.sheet.update_cell(row, col_rai, ngay_thuc_hien)

        if "Lắp TB 5G" in headers:
          col_lap = headers.index("Lắp TB 5G") + 1
          if chk_lap_5g and not get_val("Lắp TB 5G"):
            self.sheet.update_cell(row, col_lap, ngay_thuc_hien)

        if "BBNT Lắp đặt" in headers:
          col_bbnt = headers.index("BBNT Lắp đặt") + 1
          if chk_bbnt_lap and not get_val("BBNT Lắp đặt"):
            self.sheet.update_cell(row, col_bbnt, ngay_thuc_hien)

        if "Phát sóng Test" in headers:
          col_ps_test_idx = headers.index("Phát sóng Test") + 1
          if chk_ps_test and not get_val("Phát sóng Test"):
            self.sheet.update_cell(row, col_ps_test_idx, ngay_thuc_hien)

        if "Phát sóng chính thức" in headers:
          col_ps_chinh_idx = headers.index("Phát sóng chính thức") + 1
          if chk_ps_chinh and not get_val("Phát sóng chính thức"):
            self.sheet.update_cell(row, col_ps_chinh_idx, ngay_thuc_hien)

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
