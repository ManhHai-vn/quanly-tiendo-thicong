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
      # Sử dụng pd.concat chuẩn để thêm dòng tổng vào cuối
      summary_df = pd.concat(
          [summary_df, pd.DataFrame([tong_row])], ignore_index=True
      )

    return summary_df
