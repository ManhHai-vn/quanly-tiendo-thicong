def save_progress(
      self,
      tram_chon,
      chk_nhan_vt,
      chk_rai_vt,
      chk_lap_5g,
      ngay_thuc_hien,
      chk_ps_test=False,
      chk_ps_chinh=False,
      chk_bbnt_lap=False,
  ):
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
          old_val = get_val("Nhận VT")
          if chk_nhan_vt and not old_val:
            self.sheet.update_cell(row, col_nhan, ngay_thuc_hien)

        if "Rải TB" in headers:
          col_rai = headers.index("Rải TB") + 1
          old_val = get_val("Rải TB")
          if chk_rai_vt and not old_val:
            self.sheet.update_cell(row, col_rai, ngay_thuc_hien)

        if "Lắp TB 5G" in headers:
          col_lap = headers.index("Lắp TB 5G") + 1
          old_val = get_val("Lắp TB 5G")
          if chk_lap_5g and not old_val:
            self.sheet.update_cell(row, col_lap, ngay_thuc_hien)

        if "BBNT Lắp đặt" in headers:
          col_bbnt = headers.index("BBNT Lắp đặt") + 1
          old_val = get_val("BBNT Lắp đặt")
          if chk_bbnt_lap and not old_val:
            self.sheet.update_cell(row, col_bbnt, ngay_thuc_hien)

        if "Phát sóng Test" in headers:
          col_ps_test_idx = headers.index("Phát sóng Test") + 1
          old_val = get_val("Phát sóng Test")
          if chk_ps_test and not old_val:
            self.sheet.update_cell(row, col_ps_test_idx, ngay_thuc_hien)

        if "Phát sóng chính thức" in headers:
          col_ps_chinh_idx = headers.index("Phát sóng chính thức") + 1
          old_val = get_val("Phát sóng chính thức")
          if chk_ps_chinh and not old_val:
            self.sheet.update_cell(row, col_ps_chinh_idx, ngay_thuc_hien)

        return True, "Cập nhật tiến độ thành công!"
      return False, "Không tìm thấy mã trạm."
    except Exception as e:
      return False, f"Lỗi: {e}"
