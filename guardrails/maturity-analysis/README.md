# ITガバナンス実態調査 分析システム

## 概要

ITガバナンスに関する実態調査の**分析システム**です。  
調査票の**全7セクション・37問**を反映し、データ生成・前処理・分析・可視化・レポート生成までを一貫して実行できます。

**主な機能**
- サンプルデータの自動生成（部門・地域などは config で制御）
- データ前処理（バイナリ変換・One-Hot Encoding・優先順位付き変換）
- 統計分析（選択率、セキュリティ成熟度、困りごと、地域別・部門別集計）
- 5つの主要可視化（A〜E）＋ 地域別・部門別のグラフ
- 統合 Markdown レポート（`reports/report.md`）
- 対話型の 4 ステップワークフロー（`main.py`）

---

## フォルダ構成

```
maturity-analysis/
├── main.py                          # メインプログラム（4ステップワークフロー）
├── config/
│   ├── config.yaml                  # システム設定（サンプル数・部門分布・パス等）
│   └── survey_questions.yaml        # アンケート項目定義（全7セクション・37問）
├── modules/
│   ├── data_generator.py            # サンプルデータ生成
│   ├── data_preprocess.py           # データ前処理
│   ├── data_analyser.py             # データ分析
│   ├── report_generator.py         # レポート・可視化生成
│   └── util.py                      # ユーティリティ
├── csv/
│   ├── survey_sample_data.csv      # 生データ（サンプル or 実データ）
│   └── survey_preprocessed_data.csv # 前処理済みデータ
├── out/
│   ├── preprocessing_report.json   # 前処理レポート
│   └── analysis_results.json       # 分析結果（選択率・成熟度・困りごと・地域別等）
├── reports/
│   ├── report.md                    # 統合レポート（目次・可視化一覧・図付き）
│   └── graphs/                      # 可視化PNG（A〜E + 地域比較等）
├── doc/                             # 調査票・提案ドキュメント
├── requirements.txt
└── README.md
```

---

## セットアップ

### 前提条件
- Python 3.8 以上

### インストール

```bash
# リポジトリへ移動
cd maturity-analysis

# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

## 実行方法

### 推奨: 一括実行（対話型）

```bash
python3 main.py
```

**4ステップの流れ**

1. **サンプルデータ生成**  
   件数指定 or 既存 CSV 利用。部門は `config/config.yaml` の `population_distribution.department` に従い重み付きで割り当てられます。
2. **データ前処理**  
   バイナリ変換・One-Hot・優先順位付き変換など。`csv/survey_preprocessed_data.csv` と `out/preprocessing_report.json` を出力。
3. **データ分析**  
   選択率、セキュリティ成熟度、困りごと、必要な支援、地域別・部門別集計など。結果は `out/analysis_results.json` に保存。
4. **レポート生成**  
   全可視化を生成し、`reports/report.md` に統合レポートを出力。

### 個別モジュールの実行

```bash
# データ生成のみ
python3 -m modules.data_generator

# 前処理のみ
python3 -m modules.data_preprocess

# 分析のみ
python3 -m modules.data_analyser

# レポート・可視化のみ
python3 -m modules.report_generator
```

---

## 可視化（レポートに含まれる図）

| 可視化 | 内容 | 出力ファイル |
|--------|------|----------------|
| **A** | 導入ツール・ベンダーマップ（プレースホルダー） | `visualization_A_vendor_map.png` |
| **B** | 意思決定プロセス（地域別・部門別） | `visualization_B_decision_process_by_region.png`<br>`visualization_B_decision_process_by_department.png` |
| **C** | セキュリティ成熟度（地域別・部門別） | `visualization_C_security_maturity_by_region.png`<br>`visualization_C_security_maturity_by_department.png` |
| **D** | 困りごと・ニーズ（地域比較） | `visualization_D1_pain_points_regional_comparison.png`<br>`visualization_D2_support_needs_regional_comparison.png` |
| **E** | 部門別の強み（RAGヒートマップ） | `visualization_E_department_profile.png` |
| **追加** | 困りごとカテゴリ別サマリー | `additional_category_summary.png` |

- **地域の色**  
  日本＝赤、北米＝濃い青、EMEA＝薄い青で統一（B・C・D の地域グラフ）。
- **E のヒートマップ**  
  RAG で表示。スコア ≤20＝赤（困っている）、20〜50＝黄（中間）、>50＝緑（困っていない）。セクションは S1〜S7 に英語ラベル（Tech adoption, Security, …）を付与。

---

## 設定のカスタマイズ

### 部門名・部門分布（config で制御）

`config/config.yaml` の `population_distribution.department` を変更すると、**サンプルデータ生成時の部門**がその名前と割合で決まります。

```yaml
data_generation:
  population_distribution:
    department:
      ビジネス系IT: 0.25
      工場系IT: 0.25
      本社系IT: 0.2
      インフラ: 0.1
      セキュリティ: 0.1
      組織運営: 0.05
      その他: 0.05
```

分析・レポートの部門別集計は、**実際の CSV の「所属部門」列**に基づくため、実データを使う場合は CSV の部門名がそのまま反映されます。

### サンプル数・乱数シード

```yaml
data_generation:
  default_sample_size: 100
  random_seed: 42   # 再現用。null で毎回ランダム
```

### ファイルパス

```yaml
paths:
  raw_data: csv/survey_sample_data.csv
  preprocessed_data: csv/survey_preprocessed_data.csv
  analysis_results: out/analysis_results.json
```

レポートは `report_generator` 実行時に `reports/report.md` および `reports/graphs/*.png` に出力されます。

---

## 出力データの概要

### 生データ (csv/survey_sample_data.csv)

- **基本情報**: 所属部門、地域（日本/北米/EMEA）、管掌範囲、IT予算 など
- **セクション1〜7**: 導入時の決定方法、セキュリティ、データ取扱い、変更管理、予算、ベンダー、その他 の質問と回答

### 前処理済みデータ (csv/survey_preprocessed_data.csv)

- 複数選択 → バイナリ（0/1）列
- 単一選択（地域など）→ One-Hot
- 優先順位付き → 選択フラグ＋順位列
- 所属部門は元の文字列のまま（分析で利用）

### 分析結果 (out/analysis_results.json)

- メタデータ、選択率（セクション別）
- 意思決定プロセスの地域別・部門別（`decision_process_breakdown`）
- セキュリティ成熟度（全体・部門別・地域別）
- 困りごと・必要な支援（全体・地域別）
- 部門別プロファイル

### レポート (reports/report.md)

- 目次、エグゼクティブサマリー、可視化一覧表
- A〜E のセクションと対応する図（50% 幅で埋め込み）
- グラフ一覧（リンク付き）

---

## トラブルシューティング

### グラフの日本語が文字化けする

- `report_generator.py` では起動時に `setup_japanese_font()` で利用可能フォントを検出し、`rcParams` を設定しています。
- フォントが足りない場合は、OS に日本語フォント（macOS: Hiragino、Windows: Yu Gothic、Linux: Noto Sans CJK JP 等）を入れ、matplotlib のフォントキャッシュをクリアしてください。

### ValueError: Passing a Normalize instance simultaneously with vmin/vmax

- 可視化 E のヒートマップで `norm` を渡しているため、`imshow` には `vmin`/`vmax` を渡さないようにしています。別の箇所で同エラーが出る場合は、`norm` と `vmin`/`vmax` の併用をやめてください。

### 部門が想定と違う

- **サンプルデータ**の場合: `config/config.yaml` の `population_distribution.department` を確認し、`python3 -m modules.data_generator` で再生成。
- **実データ**の場合: CSV の「所属部門」列の値をそのまま使うため、部門名・表記を CSV 側で統一してください。

---

## ライセンス

MIT License
