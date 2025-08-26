import numpy as np
import pandas as pd
import json

# 設定ファイルを読み込み
with open("./config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def read_data():
    
    # 依頼データ
    df_request = pd.read_excel(config['data']['依頼データ'], sheet_name = 'Sheet1', dtype = {'業者ID' : str})
    # カラム名変更
    df_request.rename(columns = {'業者ID' : '業者CD'}, inplace = True)
    
    # 協力会社関連データ (sp = service provider)
    df_sp = pd.read_pickle(config['data']['協力会社関連データ'])
    
    # スキルデータ
    df_skill = pd.read_pickle(config['data']['スキルデータ'])
    
    # GPSデータ
    df_gps = pd.read_pickle(config['data']['GPSデータ'])
    # 「端末ステータス」が「待機中」のレコードのみ抽出
    df_gps = df_gps[df_gps['端末ステータス'] == '待機中'].copy()
        
    # Paa-S対応表
    df_paas = pd.read_pickle(config['data']['Paa-S対応表'])
    
    return {
            '依頼データ' : df_request,
            '協力会社関連データ' : df_sp,
            'スキルデータ' : df_skill,
            'GPSデータ' : df_gps,
            'Paa-S対応表' : df_paas, 
    }