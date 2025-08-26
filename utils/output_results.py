import numpy as np
import pandas as pd
import os
import json

# excelへの出力関係
from openpyxl.styles import Font
import unicodedata

# 設定ファイルを読み込み
with open("./config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def excel_display_width(text):
    """Excelでの表示幅をざっくり計算（全角:2, 半角:1）"""
    if text is None:
        return 0
    width = 0
    for ch in str(text):
        # 東アジアの全角/半角幅判定
        if unicodedata.east_asian_width(ch) in ['F', 'W', 'A']:  
            width += 2
        else:
            width += 1
    return width

def set_excel_style(workbook):    
    for sheetname in workbook.sheetnames:
        sheet = workbook[sheetname]

        # フォント設定（例: Meiryo UI、サイズ10）
        font = Font(name='Meiryo UI', size=10)
        for row_cells in sheet.iter_rows():
            for cell in row_cells:
                cell.font = font
                
        # 列幅自動調整（全角考慮版）
        for col in sheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                max_length = max(max_length, excel_display_width(cell.value))
            # 全角幅をExcelの列幅に変換
            adjusted_width = (max_length + 2) / 1.1  # 1.1は微調整用
            sheet.column_dimensions[col_letter].width = adjusted_width

def output_results_excel(results, logics, columns, reception_num):
    output_dir = config['recommendation']['output_dir']
    os.makedirs(os.path.join(output_dir , 'まとめ'), exist_ok=True)
    file = os.path.join(output_dir , f'まとめ/【{reception_num}】レコメンド結果.xlsx')
    with pd.ExcelWriter(file, engine="openpyxl") as writer:
        for logic in logics.keys():
            results[(reception_num, logic)][columns].to_excel(writer, sheet_name=logic, index=False)
            
        # writer.book で openpyxl Workbook
        workbook = writer.book

        # エクセルの体裁と整理
        set_excel_style(workbook)

def output_summary_excel(df_summary):
    output_dir = config['recommendation']['output_dir']
    file = os.path.join(output_dir , 'レコメンド結果サマリ.xlsx')
    with pd.ExcelWriter(file, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name='サマリ', index=False)
        
        # writer.book で openpyxl Workbook にアクセス
        workbook = writer.book
        
        # エクセルの体裁と整理
        set_excel_style(workbook)