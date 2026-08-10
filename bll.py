from dal import DataAccessLayer
import pandas as pd
import streamlit as st


class BusinessLogicLayer:

  def __init__(self):
    self.dal = DataAccessLayer()

  def get_raw_data(self):
    return self.dal.fetch_data()

  def get_partners(self, df):
    col_dt = "ĐỐI TÁC" if "ĐỐI TÁC" in df.columns else df.columns[5]
    if col_dt in df.columns:
      return ["Tất cả"] + list(df[col_dt].dropna().unique())
    return ["Tất cả"]

  def filter_stations(self, df, partner, keyword):
    if df.empty:
      return df
    col_dt = "ĐỐI TÁC" if "ĐỐI TÁC" in df.columns else df.columns[5]
    df_filtered = df.copy()

    if partner != "Tất cả" and col_dt in df_filtered.columns:
      df_filtered = df_filtered[df_filtered[col_dt] == partner]

    if keyword:
      df_filtered = df_filtered[
          df_filtered["Matram"]
          .astype(str)
          .str.contains(keyword, case=False, na=False)
      ]

    return df_filtered

  def process_partner_summary(self, df):
    col_dt = "ĐỐI TÁC" if "ĐỐI TÁC" in df.columns else df.columns[5]
    if col_dt not in df.columns or "Lắp TB 5G" not in df.columns:
      return pd.DataFrame()

    df_dt = df[
        df[col_dt].notna()
        & (df[col_dt].astype(str).str.strip() != "")
        & (df[col_dt].astype(str).str.lower() != "nan")
    ]
    if df_dt.empty:
      return pd.DataFrame()

    summary_df = (
        df_dt.groupby(col_dt)
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

    return summary_df.rename(
        columns={
            col_dt: "Tên Đối Tác",
            "Tong_Giao": "Tổng Trạm Được Giao",
            "Da_Lap_Dat": "Đã Lắp Đặt 5G",
            "Ti_Le_Hien_Thi": "Tỷ Lệ Hoàn Thành",
        }
    )

  def save_progress(self, tram_chon, chk_nhan, chk_rai, chk_lap, ngay):
    col_indices = []
    if chk_nhan:
      col_indices.append(11)  # Cột K
    if chk_rai:
      col_indices.append(12)  # Cột L
    if chk_lap:
      col_indices.append(13)  # Cột M

    if not col_indices:
      return False, "Vui lòng chọn ít nhất một mốc tiến độ cần cập nhật."

    success = self.dal.update_station_progress(
        tram_chon, col_indices, ngay
    )
    if success:
      st.cache_data.clear()
      return True, f"Đã cập nhật thành công ngày {ngay} cho trạm {tram_chon}!"
    return False, "Không tìm thấy mã trạm hoặc lỗi cập nhật."
    # Thêm vào trong class BusinessLogicLayer (file bll.py)

 
# Thêm vào class BusinessLogicLayer trong file bll.py


def save_lich_du_kien(self, matram, ngay, so_doi):
  if not matram:
    return False, "Vui lòng chọn mã trạm."
  success = self.dal.update_du_kien(matram, ngay, so_doi)
  if success:
    st.cache_data.clear()
    return (
        True,
        f"Đã cập nhật lịch dự kiến cho trạm {matram} (Ngày: {ngay}, Số đội:"
        f" {so_doi})!",
    )
  return False, "Không tìm thấy mã trạm tương ứng trong Google Sheets."
