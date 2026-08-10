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

        if "BBNT Lắp đặt" in headers:
          col_bbnt = headers.index("BBNT Lắp đặt") + 1
          self.sheet.update_cell(
              row, col_bbnt, ngay_thuc_hien if chk_bbnt_lap else ""
          )

        if "Phát sóng Test" in headers:
          col_ps_test = headers.index("Phát sóng Test") + 1
          self.sheet.update_cell(
              row, col_ps_test, ngay_thuc_hien if chk_ps_test else ""
          )

        if "Phát sóng chính thức" in headers:
          col_ps_chinh = headers.index("Phát sóng chính thức") + 1
          self.sheet.update_cell(
              row, col_ps_chinh, ngay_thuc_hien if chk_ps_chinh else ""
          )

        return True, "Cập nhật tiến độ thành công!"
      return False, "Không tìm thấy mã trạm."
    except Exception as e:
      return False, f"Lỗi: {e}"
