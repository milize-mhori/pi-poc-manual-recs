import numpy as np
import pandas as pd
import json

# utilsファイルインポート
from utils.get_distance_duration import *
from utils.output_results import *

# 設定ファイルを読み込み
with open("./config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
        
def create_summary(df_request):    
    
    # 各ロジック毎のソートキー
    logics = config['recommendation']['logics']
    
    # 受付番号のリスト
    reception_numbers = config['recommendation']['reception_numbers']
    
    # データ格納用辞書初期化
    tmp_dict = {}

    tmp_dict['受付番号'] = []
    tmp_dict['Paa-S車両'] = []
    tmp_dict['経路距離'] = []
    tmp_dict['到着時間'] = []
    for key in logics.keys():
        tmp_dict[key] = []

    # データ格納
    for reception_number in reception_numbers:
        tmp_dict['受付番号'].append(reception_number)        
        
        output_dir3 = set_output_dir()
        for i, key in enumerate(logics.keys()):
            file = os.path.join(output_dir3, f'受付番号別結果/【{reception_number}】レコメンド結果.xlsx')
            df_recommend = pd.read_excel(file, sheet_name = i)
            
            mask = df_recommend['出動'] == '〇'
            if i == 0:
                # 経路距離・到着時間の取得、Paa-S車両の判定 (車両区分が空文字やNaNでないか確認)
                # if len(df_recommend[mask]) == 1:
                if len(df_recommend[mask]) >= 1:
                    tmp_dict['経路距離'].append(df_recommend.loc[mask, '経路距離'].iloc[0])
                    tmp_dict['到着時間'].append(df_recommend.loc[mask, '到着時間'].iloc[0])
                    terminal_id = df_recommend.loc[mask, '車両区分'].iloc[0]
                    if pd.notna(terminal_id) and terminal_id != '':
                        tmp_dict['Paa-S車両'].append('〇')
                    else:
                        tmp_dict['Paa-S車両'].append('')
                elif len(df_recommend[mask]) == 0:
                    tmp_dict['経路距離'].append(np.nan)
                    tmp_dict['到着時間'].append(np.nan)
                    tmp_dict['Paa-S車両'].append('')
                    
            # レコメンド結果に出動した協力会社が含まれているか確認
            # 依頼した協力会社が拠点かPaa-S車両は判別できないケースがあるためロジックを修正
            if len(df_recommend[mask]) >= 1:
                # 出動行のインデックスを取得して+1
                tmp_dict[key].append(int(df_recommend[mask].iloc[[0]].index[0]) + 1)
                
            # if len(df_recommend[mask]) == 1:
            #     # 出動行のインデックスを取得して+1
            #     tmp_dict[key].append(int(df_recommend[mask].index[0]) + 1)

            elif len(df_recommend[mask]) == 0:
                tmp_dict[key].append('存在せず')
    
    
    df_summary = df_request[df_request['受付番号'].isin(reception_numbers)].copy()
    df_summary = df_summary[['受付番号', '車両種別', 'スキル_カンマ区切り', 
                            '業者詳細区分', '業者CD', '手配業者名', '手配業者分類',
                            'トラブル場所(位置取得住所)', 'トラブル場所緯度', 'トラブル場所経度']].copy()

    # 受付番号別打診回数マージ    
    df_count = pd.read_csv(config['summary']['data']["受付番号別打診回数データ"])[['受付番号', '打診回数']]
    df_summary = df_summary.merge(df_count, on = '受付番号', how = 'left')

    # 住所データマージ、経路距離・到着時間算出
    df_address = pd.read_csv(config['summary']['data']["協力会社住所・緯度・経度データ"],
                            dtype = {'業者CD' : str, '法人CD2' : str})[['業者CD', '業者住所', '業者緯度', '業者経度']]
    df_summary = df_summary.merge(df_address, on = '業者CD', how = 'left').copy()

    # ランクデータ・マージ
    df_summary = df_summary.merge(pd.DataFrame(tmp_dict), on = '受付番号', how = 'left')

    # 特別対応 (手配業者名 : PA（㈱桝本ﾚｯｶｰ 宇都宮店（M's Tokyo）, 業者CD : 00327016）)
    # 緯度 : 36.511731, 経度 : 139.9059222
    df_summary.loc[df_summary['業者CD'] == "00327016", '業者緯度'] = 36.511731
    df_summary.loc[df_summary['業者CD'] == "00327016", '業者経度'] = 139.9059222

    func = lambda row : get_route_distance2((row['業者緯度'], row['業者経度']), (row['トラブル場所緯度'], row['トラブル場所経度']))
    df_summary[['経路距離2', '到着時間2']] = pd.DataFrame(df_summary.apply(func, axis = 1).tolist(), index=df_summary.index)

    # レコメンドに打診した協力会社が現れない場合の経路距離・到着時間の取得
    df_summary['経路距離'] = df_summary['経路距離'].fillna(df_summary['経路距離2'])
    df_summary['到着時間'] = df_summary['到着時間'].fillna(df_summary['到着時間2'])

    # ソート
    df_summary.sort_values(['車両種別', '打診回数'], inplace = True)

    # 残すカラム
    columns = ['受付番号', '車両種別', 'スキル_カンマ区切り', 'トラブル場所(位置取得住所)', 
            '業者詳細区分', '業者CD', '手配業者名', '手配業者分類', '業者住所', 
            'Paa-S車両', '経路距離', '到着時間', '打診回数'] + list(logics.keys())

    df_summary = df_summary[columns]    
    
    # サマリ出力
    output_summary_excel(df_summary, output_dir3)