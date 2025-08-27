import numpy as np
import pandas as pd

def calc_scores(df):    
    # カラム初期化
    df['スコア0_1'] = 0
    df['スコア0_2'] = 0
    df['スコア1_1'] = 0
    df['スコア1_2'] = 0
    df['RI1'] = 0
    df['RI2'] = 0
    
    # 重み
    weight = 1/5
    
    # RI1, RI2算出
    for col in ['合計出動率', 'Paa-S使用率', '遠方出動比率', '夜間出動比率']:
        df[f'(1 - {col})'] = 1 - df[col] 
        df['RI1'] += df[f'(1 - {col})']
        
        if col in ['Paa-S使用率', '遠方出動比率', '夜間出動比率']:
            df['RI2'] += weight * df[f'(1 - {col})']
        else:
            df['RI2'] += df[f'(1 - {col})']
    
    # 各種スコア算出  
    # 標準化
    col2 = '(1 - 合計出動率)'
    df[f'{col2}_zスコア'] = (df[col2] - df[col2].mean()) / df[col2].std(ddof=0)
    
    for col in ['経路距離', '到着時間', 'RI1', 'RI2']:        
        # 標準化
        df[f'{col}_zスコア'] = (df[col] - df[col].mean()) / df[col].std(ddof=0)              
                
        # スコア0_1
        if col in ['経路距離']:
            df['スコア0_1'] += df[f'{col}_zスコア']
            df['スコア0_1'] += df[f'{col2}_zスコア']
            
        # スコア0_2
        if col in ['到着時間']:
            df['スコア0_2'] += df[f'{col}_zスコア']
            df['スコア0_2'] += df[f'{col2}_zスコア']
            
        # スコア1_1
        if col in ['到着時間', 'RI1']: 
            df['スコア1_1'] += df[f'{col}_zスコア']
        
        # スコア1_2
        if col in ['到着時間', 'RI2']: 
            df['スコア1_2'] += df[f'{col}_zスコア']
            
    return df