# テーブル定義書：vendors

| 項目 | 内容 |
|------|------|
| テーブル名 | vendors |
| 説明 | ベンダーの基本情報を管理 |
| 主キー | vendor_id |
| バージョン | 1.0 |
| 最終更新日 | 2026-01-24 |

## カラム定義

| No. | カラム名 | データ型 | 必須 | 説明 | 制約・備考 |
|-----|----------|----------|------|------|------------|
| 1 | vendor_id | string | ○ | ベンダーID（一意識別子） | 形式: V{0:05d}、例: V00001 |
| 2 | vendor_name_official | string | ○ | ベンダー名（正式名称） | 最大長: 200文字 |
| 3 | vendor_name_short | string | - | ベンダー名（略称） | 最大長: 50文字 |
| 4 | vendor_classification | string | ○ | ベンダー分類 | 大手企業, 中堅企業, 中小企業, スタートアップ, 個人事業主 |
| 5 | industry | string | ○ | 業種 | IT・システム開発, コンサルティング, BPO・業務委託, マーケティング, 人材派遣, 施設管理, その他 |
| 6 | relationship_start_date | date | ○ | 取引開始日 | 形式: YYYY-MM-DD |
| 7 | years_of_business | float | - | 取引年数 | 単位: 年 |
| 8 | annual_spend | integer | - | 年間取引総額 | 単位: 円 |
| 9 | contract_count | integer | - | 契約件数 | - |
| 10 | primary_contact | string | - | 主要連絡先（担当者名） | 最大長: 100文字 |
| 11 | vendor_rating | string | - | 評価スコア | S, A, B, C, D |
| 12 | risk_level | string | - | リスクレベル | 高, 中, 低 |
| 13 | notes | string | - | 備考 | 最大長: 500文字 |
