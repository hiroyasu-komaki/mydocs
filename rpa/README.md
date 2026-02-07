# 請求書OCR処理システム

## 概要

このシステムは、請求書PDFから自動的にデータを抽出し、構造化されたJSONファイルとして出力します。OCR処理、データバリデーション、二重払い防止チェック機能を統合し、日英両言語に対応しています。

### 主な機能

- **自動OCR処理**: PDFからテキスト/画像を自動認識してデータ抽出
- **日英両言語対応**: 日本語・英語フォーマットの両方に対応
- **データバリデーション**: 必須項目チェックとデータ型検証
- **処理ステータス管理**: 良好/要確認の判定とエラー詳細の記録
- **二重払い防止**: 履歴データとの重複チェック機能
- **過去実績エクスポート**: 履歴データをCSV形式で一括出力

## インストール

### 前提条件

- Python 3.7以上
- Tesseract OCR（日本語データ含む）

### Tesseract OCRのインストール

**Mac OS:**
```bash
brew install tesseract
brew install tesseract-lang  # 日本語データ
```

**Windows:**
1. [Tesseract公式サイト](https://github.com/UB-Mannheim/tesseract/wiki)からインストーラーをダウンロード
2. インストール時に「Japanese」を選択

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-jpn
```

### 仮想環境の作成
```bash
python3 -m venv venv

# Mac OSの場合: 
source venv/bin/activate

# Windowsの場合: 
venv\Scripts\activate
```

### 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
PyMuPDF>=1.23.0
Pillow>=10.0.0
pytesseract>=0.3.10
pandas>=2.0.0
PyYAML>=6.0
```

## システム構造

```
プロジェクト/
├── main.py                          # メインエントリポイント
├── modules/
│   ├── ocr_processor.py            # OCR処理エンジン
│   ├── data_validator.py             # データバリデーター
│   ├── duplicate_checker.py          # 二重払い防止チェッカー
│   ├── history_exporter.py           # 過去実績CSVエクスポーター
│   └── datetime_utils.py             # 日時ユーティリティ
├── config/
│   ├── fields.yaml                   # フィールド定義（正規表現パターン）
│   └── invoice_validation.json       # 請求書バリデーション設定
├── pdf/                              # 入力PDFフォルダ（請求書PDFを配置）
├── history/                          # 過去の請求書履歴（二重払い防止用）
│   ├── 2025/                         # 年別フォルダ（任意の構成でOK）
│   └── 2026/
├── output/                           # 出力JSONフォルダ
│   ├── invoice_data.json             # 抽出された請求書データ
│   └── duplicate.errors.json         # 重複チェックエラー情報
└── csv/                              # CSV出力フォルダ
    └── invoice_history_*.csv         # 過去実績CSVファイル
```

## 使い方

### 1. PDFファイルの配置

処理したい請求書PDFファイルを`pdf/`フォルダに配置します。

### 2. プログラムの実行

```bash
python main.py
```

### 3. 処理モードの選択

プログラム起動時に、以下のメニューが表示されます：

```
処理モードを選択してください:
  1. 請求書OCR処理を実行
  2. 過去実績をCSVで出力

選択 (1/2):
```

- **1を選択**: 請求書OCR処理を実行（PDF読み取りから重複チェックまで）
- **2を選択**: 履歴データをCSV形式で一括出力

### 4. OCR処理のフロー（モード1を選択した場合）

1. **OCR処理**: PDFからテキスト抽出・フィールド認識
2. **JSON出力**: 抽出データをJSON形式で保存
3. **バリデーション**: 必須項目とデータ型をチェック
4. **二重払い防止チェック**: 履歴データとの重複確認
5. **ステータス更新**: 処理結果（良好/要確認）をJSONに記録、重複エラーは別ファイルに出力

### 5. 過去実績エクスポート（モード2を選択した場合）

- `history`フォルダ内の全請求書JSONファイルを読み込み
- 処理日時の順番にソート
- CSV形式で`csv`フォルダに出力（ファイル名: `invoice_history_YYYYMMDD_HHMMSS.csv`）

### 6. 結果の確認

#### OCR処理結果（`output/invoice_data.json`）

```json
{
  "document_type": "invoice",
  "processed_at": "2026-02-07 10:30",
  "total_documents": 3,
  "documents": [
    {
      "請求日": "2026年1月15日",
      "請求書番号": "INV-2026-001",
      "登録番号": "T1234567890123",
      "宛先会社名": "株式会社サンプル",
      "請求金額": "¥100,000",
      "合計": "¥110,000",
      "_metadata": {
        "ファイル名": "invoice_001.pdf",
        "ファイルパス": "pdf/invoice_001.pdf",
        "処理日時": "2026-02-07 10:30",
        "処理ステータス": "良好"
      }
    }
  ]
}
```

**処理日時の形式**: JST（日本標準時）で`YYYY-MM-DD HH:MM`形式で出力されます。

#### 重複チェックエラー情報（`output/duplicate.errors.json`）

重複が検出された場合、詳細情報が別ファイルに出力されます：

```json
{
  "generated_at": "2026-02-07 10:35",
  "source_file": "output/invoice_data.json",
  "total_documents": 3,
  "error_count": 1,
  "alert_count": 1,
  "errors": [
    {
      "index": 0,
      "ファイル名": "invoice_002.pdf",
      "請求書番号": "INV-2026-001",
      "重複理由": "同一請求書番号が履歴に存在",
      "重複詳細": [...]
    }
  ],
  "alerts": [
    {
      "index": 1,
      "ファイル名": "invoice_003.pdf",
      "重複理由": "発行者名・請求日・請求金額が一致",
      "類似詳細": [...]
    }
  ]
}
```

**重複チェック結果の見方:**

- **エラー**: 同一請求書番号を検出、二重払いの可能性大（要確認）
- **アラート**: 類似する請求書を検出、念のため確認推奨

#### 過去実績CSV（`csv/invoice_history_YYYYMMDD_HHMMSS.csv`）

履歴データをCSV形式で一括出力します。処理日時の順番にソートされ、すべてのフィールドとメタデータが含まれます。

## 主要コンポーネント

### 1. **OCRProcessor** (`ocr_processor.py`)

PDFからデータを抽出するコアエンジン：

- **テキスト抽出優先**: PDFに埋め込みテキストがあれば直接抽出
- **OCRフォールバック**: テキストが少ない場合は画像OCR（300dpi）
- **正規表現マッチング**: fields.yamlのパターンでフィールド抽出
- **文字化け対応**: 私用領域文字（U+E000-U+F8FF）のクリーンアップ

### 2. **DataValidator** (`data_validator.py`)

抽出データの品質を検証：

- **必須項目チェック**: 未入力・空文字のフィールドを検出
- **データ型検証**: string/number/date/email形式をチェック
- **柔軟な数値処理**: カンマ区切り、通貨記号付き数値に対応
- **エラー詳細記録**: バリデーションエラーをJSONメタデータに保存

### 3. **DuplicateChecker** (`duplicate_checker.py`)

請求書の二重払いを防止：

- **完全一致検出**: 同一請求書番号の重複を自動検出（エラー）
- **類似検出**: 発行者名・請求日・請求金額が一致する請求書を警告（アラート）
- **履歴管理**: `history`フォルダ内の全JSONファイルと自動比較
- **柔軟な構成**: 履歴フォルダの階層構造やファイル名は自由
- **エラー分離**: 重複エラー情報は`duplicate.errors.json`に出力（`invoice_data.json`は汚さない）

### 4. **HistoryExporter** (`history_exporter.py`)

過去実績をCSV形式でエクスポート：

- **履歴データ収集**: `history`フォルダ内の全請求書JSONを再帰的に探索
- **時系列ソート**: 処理日時の順番に自動ソート
- **CSV出力**: すべてのフィールドとメタデータを含むCSVファイルを生成
- **エスケープ処理**: シングルクォート、カンマ、改行を含む値は適切にエスケープ

### 5. **設定ファイル**

#### fields.yaml - フィールド定義

請求書の抽出パターンを正規表現で定義：

```yaml
invoice:
  fields:
    - name: "請求日"
      pattern: "(?:請求日|Invoice Date)[:：]?\\s*(\\d{4}[年/-]\\d{1,2}[月/-]\\d{1,2})"
    - name: "請求書番号"
      pattern: "(?:請求書番号|Invoice No\\.)[:：]?\\s*([A-Z0-9\\-]+)"
```

#### invoice_validation.json - バリデーション設定

必須項目とデータ型を定義：

```json
{
  "required_fields": ["請求日", "請求書番号", "登録番号"],
  "field_types": {
    "請求日": "string",
    "請求書番号": "string",
    "請求金額": "string"
  }
}
```

## 抽出される主な項目

### 請求書 (Invoice)
- 請求日、請求書番号、登録番号
- 宛先会社名、請求金額
- 小計、消費税、合計
- 振込期日、発行者名
- 電話番号、メールアドレス

## トラブルシューティング

### Tesseractエラー

```
TesseractNotFoundError: tesseract is not installed
```

**解決方法**: Tesseract OCRをインストールしてください（上記「インストール」参照）

### 日本語OCRエラー

```
警告: 日本語データ(jpn)が見つかりません
```

**解決方法**: 
- Mac: `brew install tesseract-lang`
- Windows: Tesseractインストール時に日本語を選択
- Linux: `sudo apt-get install tesseract-ocr-jpn`

### PDFフォルダが見つからない

```
エラー: PDFフォルダが見つかりません: pdf
```

**解決方法**: プロジェクトルートに`pdf`フォルダを作成してください

### 抽出精度が低い

**対策**:
1. PDF品質を確認（スキャン解像度を300dpi以上に）
2. fields.yamlの正規表現パターンを調整
3. OCR言語設定を確認（`lang='jpn+eng'`）

## カスタマイズ

### 新しいフィールドの追加

`config/fields.yaml`に追加：

```yaml
invoice:
  fields:
    - name: "新しいフィールド名"
      pattern: "正規表現パターン"
```

### バリデーションルールの変更

`config/invoice_validation.json`を編集：

```json
{
  "required_fields": ["必須項目1", "必須項目2"],
  "field_types": {
    "項目名": "データ型"
  }
}
```

## 技術スタック

- **PyMuPDF (fitz)**: PDF解析・テキスト抽出
- **Tesseract OCR**: 光学文字認識（日英対応）
- **Pillow**: 画像処理・変換
- **PyYAML**: YAML設定ファイル読み込み
- **pandas**: データフレーム操作

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

### 使用ライブラリのライセンス

#### PyMuPDF (fitz)
- **ライセンス**: AGPL v3.0 / 商用ライセンス（デュアルライセンス）
- **本プロジェクトでの利用**: 社内専用ツールとして使用（外部配布なし）
- **注意事項**: AGPLライセンスは内部利用のみの場合、ソースコード公開義務はありません。ただし、本システムを外部に配布したり、Webサービスとして公開する場合は、ソースコード公開またはArtifex社からの商用ライセンス取得が必要になります。

#### Tesseract OCR
- **ライセンス**: Apache License 2.0
- **利用条件**: 商用利用を含め、自由に使用・改変・再配布が可能
- **注意事項**: ライセンス文の明記が推奨されます
