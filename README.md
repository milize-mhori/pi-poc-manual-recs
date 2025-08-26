# レコメンドAPI システム

## 概要
このプログラムは、依頼データに基づいて協力会社（サービスプロバイダー）のレコメンドを行うシステムです。
複数のロジックを使用して、最適な協力会社を提案し、結果をExcel形式で出力します。

## ファイル構成
```
.
├── main.py                  # メインプログラム
├── requirements.txt         # 依存関係定義ファイル
├── .gitignore              # Git除外設定
├── config/
│   ├── config.json.sample  # 設定ファイルテンプレート
│   └── config.json         # 設定ファイル（要作成・機密情報含む）
├── data/                   # 入力データディレクトリ
├── utils/                  # ユーティリティモジュール
├── result/                 # 出力結果ディレクトリ
└── レコメンド結果/          # レコメンド結果出力ディレクトリ
```

## 使い方

### 1. 環境構築

#### 前提条件
- Python 3.8以上がインストールされていること
- uvがインストールされていること（推奨）

#### uvによる仮想環境の構築（推奨）
```powershell
# uvがインストールされていない場合
pip install uv

# 仮想環境の作成
uv venv

# 仮想環境の有効化（PowerShell）
.venv\Scripts\Activate.ps1

# 依存関係のインストール
uv pip install -r requirements.txt
```

#### 従来の方法（venv使用）
```powershell
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化（PowerShell）
.venv\Scripts\Activate.ps1

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. データファイルの準備
- 依頼データファイル（Excel形式）が `data/` ディレクトリに配置されていること
- 協力会社関連データ、スキルデータ等のpklファイルが `分析用データセット/` ディレクトリに配置されていること

### 3. 設定ファイルの準備
設定ファイルをテンプレートから作成し、APIキーを設定します：

```powershell
# 設定ファイルをサンプルからコピー
Copy-Item config/config.json.sample config/config.json
```

その後、`config/config.json` ファイルで以下の設定を行います：
- **google_map.api_key**: Google Maps APIキーを設定
- **openrouteservice.api_key**: OpenRouteService APIキーを設定
- **data**: 入力データファイルのパス（必要に応じて修正）
- **recommendation**: レコメンドロジックの設定、出力件数、受付番号リスト等

#### APIキーの取得方法
- **Google Maps API**: [Google Cloud Console](https://console.cloud.google.com/) でDirections APIを有効化してキーを取得
- **OpenRouteService API**: [OpenRouteService](https://openrouteservice.org/) でアカウント作成してキーを取得

### 4. 実行方法
仮想環境が有効化されていることを確認してから、以下のコマンドを実行：

```powershell
python main.py
```

### 5. 処理フロー
1. **データ読み込み**: 設定ファイルに基づいて依頼データ、協力会社データ、スキルデータを読み込み
2. **レコメンド実行**: 複数のロジックを使用して協力会社のレコメンドを実行
3. **結果出力**: レコメンド結果をExcel形式で出力
4. **サマリ作成**: レコメンド結果のサマリを作成

### 6. 出力結果
実行が完了すると、以下のファイルが生成されます：
- `レコメンド結果/` ディレクトリ内に受付番号別のレコメンド結果Excelファイル
- レコメンド結果サマリExcelファイル
- 各種CSV形式の詳細データ

### 7. レコメンドロジック
以下のロジックが利用可能です：
- PI様現行版ロジック（業者詳細区分ランク + 直線距離）
- 経路距離のみ
- 到着時間のみ  
- 提案手法（スコアベース：0, 1, 2）

### 8. 注意事項
- APIキーは適切に設定してください
- 依頼データのExcelファイルは指定された形式に従ってください
- PowerShellを使用する場合、&&演算子は使用できません

## トラブルシューティング
- ファイルパスエラー: `config.json` 内のパス設定を確認してください
- APIエラー: Google Maps APIキーの有効性を確認してください
- データ形式エラー: 入力データの形式が要求仕様に合致していることを確認してください
