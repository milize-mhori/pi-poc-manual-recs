from utils.read_data import *
from utils.output_results import *
from utils.recommendation import *
from utils.create_summary import *

if __name__ == "__main__":
    # データ読み込み
    data = read_data()
    
    # レコメンド実行
    results = recommend_service_providers(data)
    
    # レコメンド結果サマリ作成
    create_summary(data['依頼データ'])