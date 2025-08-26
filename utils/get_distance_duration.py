import requests
import json

# 設定ファイルを読み込む
with open("./config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 経路距離と到着時間を取得する関数 (Google directions API)
def get_distance_duration_google(origin, destination):
    """
    Distance Matrix API を使って、2点間の距離と時間を取得する関数
    
    Parameters:
        api_key (str): Google API Key
        origin (str): 出発地 (例: "Tokyo,Japan" または "35.6895,139.6917")
        destination (str): 到着地
        mode (str): 移動手段 ("driving", "walking", "bicycling", "transit")
    
    Returns:
        list: 距離と時間を含むリスト
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "language": "ja",   # 日本語で返す
        "key": "xxxxxxxxxxxxxxxxxx"
    }

    response = requests.get(url, params=params)
    data = response.json()

    route = data["routes"][0]["legs"][0]

    distance_km = round(route["distance"]["value"] / 1000, 2)    # キロメートル単位
    duration_min = round(route["duration"]["value"] / 60, 2)   # 分単位

    # return route
    return [distance_km, duration_min]

# 経路距離と到着時間を取得する関数 (openrouteservice)
# 実行回数の制限 (1min : 40回, 1day : 2,000回)
def get_route_distance2(point1, point2, retry_count=0, max_retries=3):
    
    import time
    import openrouteservice
    from branca.element import Figure
    from openrouteservice import convert    
    
    try:
        # APIキー
        # key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjRhNGNiZjVkYzNmYjRjMWViMjIwNDFiNTc4YmUzYzE2IiwiaCI6Im11cm11cjY0In0="
        key = config['openrouteservice']['api_key']
        client = openrouteservice.Client(key=key, timeout=30)  # 30秒タイムアウト
        
        point1r = tuple(reversed(point1))
        point2r = tuple(reversed(point2))
        
        print(f"API呼び出し中... ({point1} -> {point2})")
        
        routedict = client.directions((point1r, point2r),
                                      profile='driving-car',
                                      preference='fastest',
                                      instructions=False,
                                      units='km')
        
        # 1分間で40回という実行制限があるため、実行後2.5秒スリープ
        time.sleep(2.5)
        
        distance_km = round(routedict['routes'][0]['summary']['distance'], 2)  # km
        duration_sec = routedict['routes'][0]['summary']['duration']  # 秒
        duration_min = round(duration_sec / 60, 2)  # 分に変換

        print(f"完了: 距離={distance_km}km, 時間={duration_min}分")
        return [distance_km, duration_min]
        
    except Exception as e:
        print(f"API呼び出しエラー: {e}")
        
        if retry_count < max_retries:
            print(f"リトライ中... ({retry_count + 1}/{max_retries})")
            time.sleep(5)  # 5秒待機してリトライ
            return get_route_distance2(point1, point2, retry_count + 1, max_retries)
        else:
            print("最大リトライ回数に達しました。直線距離で代用します。")
            # エラーの場合は直線距離で代用
            from haversine import haversine
            distance_km = haversine(point1, point2)
            duration_min = distance_km * 2  # 仮の時間計算（時速30kmと仮定）
            return [distance_km, duration_min]