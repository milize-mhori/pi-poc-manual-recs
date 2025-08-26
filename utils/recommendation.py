import numpy as np
import pandas as pd
import datetime
import glob
import os
import json

# Haversineの公式
from haversine import haversine

# utilsファイルインポート
from utils.get_distance_duration import *
from utils.calc_scores import *
from utils.output_results import *

# 設定ファイルを読み込み
with open("./config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def recommend_service_providers(data):
    
    # 各ロジック毎のソートキー
    logics = config['recommendation']['logics']
    
    # 出力するカラム
    columns = config['recommendation']['columns']
    
    # レコメンドされる協力会社の数
    recommend_num = config['recommendation']['recommend_num']
    
    # 受付番号のリスト
    reception_numbers = config['recommendation']['reception_numbers']
    
    # データ展開
    df_request = data['依頼データ']
    df_sp = data['協力会社関連データ']
    df_skill = data['スキルデータ']
    df_gps = data['GPSデータ']
    df_paas = data['Paa-S対応表']
    
    # 依頼データの絞込み (該当の受付番号)
    df_request_tmp = df_request[df_request['受付番号'].isin(reception_numbers)].copy()    
    df_request_tmp['出動'] = '〇'
    
    results = {}
    for index, row in df_request_tmp.iterrows():
        print(row['受付番号'])
        df_sp_tmp = df_sp.copy()
        df_gps_tmp = df_gps.copy()
        
        # 車両種別・スキルによる協力会社の絞込み
        df_skill_tmp = df_skill[(df_skill['車両種別'] == row['車両種別']) & (df_skill['手配種別'] == row['スキル_カンマ区切り'])]
        
        print('車両種別 :', row['車両種別'], ', 手配種別 : ', row['スキル_カンマ区切り'])
        
        # 拠点の協力会社の絞込み
        print('拠点の協力会社の絞込み')
        print('絞込み前 :', len(df_sp_tmp))
        df_sp_tmp2 = df_skill_tmp[['業者CD']].merge(df_sp_tmp, on = '業者CD', how = 'left')
        
        print('絞込み後 :', len(df_sp_tmp2))
        
        # Paa-S端末を持つ車両の絞込み
        print('Paa-S端末を持つ車両の絞込み')
        df_paas_tmp = df_paas[(df_paas['車両種別'] == row['車両種別']) & (df_paas['スキル'] == row['スキル_カンマ区切り'])]
        
        print('絞込み前 :', len(df_gps_tmp))
        car_cat = df_paas_tmp['車両区分'].to_list()
        # 車両区分、時間 : 受付時間から受付時間の2分後まで (入電してから2分程話すことを想定)
        start = row['入電日時']
        end = row['入電日時'] + datetime.timedelta(minutes = 2)
        df_gps_tmp2 = df_gps_tmp[(df_gps_tmp['車両区分'].isin(car_cat)) 
                               & (start <= df_gps['登録時間']) & (df_gps['登録時間'] < end)].copy()
        
        # df_sp_tmpとマージ
        col_indicators = ['業者CD', '業者名称', '業者住所', '業者詳細区分', '業者詳細区分ランク', 
                          '合計出動率', 'Paa-S使用率', '遠方出動比率', '夜間出動比率', 'PI料金了承']
        df_gps_tmp2 = df_gps_tmp2.merge(df_sp_tmp[col_indicators], on = '業者CD', how = 'left')
        
        # 欠損の場合の補完
        # 業者名称、業者詳細区分 : 不明
        # 業者詳細区分ランク : 5
        # 合計出動率、Paa-S使用率、遠方出動比率、夜間出動比率 : 0
        # PI料金了承 : 不明
        for col in col_indicators:
            if col in ['業者名称', '業者住所', '業者詳細区分', 'PI料金了承']:
                df_gps_tmp2[col] = df_gps_tmp2[col].fillna('不明')
            elif col in ['業者詳細区分ランク']:
                df_gps_tmp2[col] = df_gps_tmp2[col].fillna(5)
            elif col in ['合計出動率', 'Paa-S使用率', '遠方出動比率', '夜間出動比率']:
                df_gps_tmp2[col] = df_gps_tmp2[col].fillna(0)
                
        print('Paa-S端末絞込み後 :', len(df_gps_tmp2))
        
        # データ連結 (拠点のデータとPaa-S端末の車両データ)
        print(f'拠点データ件数: {len(df_sp_tmp2)}')
        print(f'Paa-S端末データ件数: {len(df_gps_tmp2)}')
        df_tmp = pd.concat([df_sp_tmp2, df_gps_tmp2])
        print(f'結合後データ件数: {len(df_tmp)}')
                
        point = (row['トラブル場所緯度'], row['トラブル場所経度'])
        df_tmp['直線距離'] = df_tmp.apply(lambda row2 : haversine(point, (row2['緯度'], row2['経度'])), axis = 1)
        
        # 直線距離が近い協力会社の絞り込み
        print(f'recommend_num設定値: {recommend_num}')
        df_tmp = df_tmp.sort_values('直線距離').head(recommend_num).copy()
        print(f'直線距離絞込み後データ件数: {len(df_tmp)}')        
        
        # openrouteserviceを用いて経路距離を算出
        print(f"経路距離・到着時間を計算中... (対象件数: {len(df_tmp)}件)")
        print("※APIレート制限により、1件あたり約2.5秒かかります")
        
        # df_tmp['経路距離'] = df_tmp.apply(lambda row2 : get_route_distance2(point, (row2['緯度'], row2['経度'])), axis = 1)
        results_list = []
        for idx, row2 in df_tmp.iterrows():
            print(f"進捗: {len(results_list) + 1}/{len(df_tmp)}")
            result = get_route_distance2(point, (row2['緯度'], row2['経度']))
            results_list.append(result)
        
        df_tmp[['経路距離', '到着時間']] = pd.DataFrame(results_list, index=df_tmp.index)
        
        # 平均値・標準偏差の計算 & スコアの計算
        df_tmp = calc_scores(df_tmp)
        
        # print(df_tmp.info())
        
        # 出動結果のマージ
        df_request_tmp2 = df_request_tmp[df_request_tmp['受付番号'] == row['受付番号']].copy()
        df_tmp = df_tmp.merge(df_request_tmp2[['業者CD', '出動']], on = '業者CD', how = 'left')
        
        # 結果の格納と出力
        for logic in logics.keys():
            print(f'<ロジック : {logic}>')
            # ソート
            df_tmp2 = df_tmp.sort_values(logics[logic]).copy()     
            
            # 結果の格納
            results[(row['受付番号'], logic)] = df_tmp2
            
            # 結果の出力
            output_dir = config['recommendation']['output_dir']
            os.makedirs(os.path.join(output_dir , 'まとめ/csv'), exist_ok=True)
            file = os.path.join(output_dir, f'まとめ/csv/【{row["受付番号"]}】レコメンド結果_{logic}.csv') 
            df_tmp2[columns].to_csv(file, encoding = 'utf-8-sig', index = False)
        
        # エクセルファイルに出力
        output_results_excel(results, logics, columns, row["受付番号"])
            
    return results