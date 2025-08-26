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
def get_route_distance2(point1, point2):
    
    import time
    import openrouteservice
    from branca.element import Figure
    from openrouteservice import convert    
    
    # APIキー
    # key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjRhNGNiZjVkYzNmYjRjMWViMjIwNDFiNTc4YmUzYzE2IiwiaCI6Im11cm11cjY0In0="
    key = config['openrouteservice']['api_key']
    client = openrouteservice.Client(key=key)
    
    point1r = tuple(reversed(point1))
    point2r = tuple(reversed(point2))
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

    return [distance_km, duration_min]