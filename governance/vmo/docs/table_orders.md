# テーブル定義書：orders

| 項目 | 内容 |
|------|------|
| テーブル名 | orders |
| 説明 | 発注実績の個別トランザクション |
| 主キー | order_id |
| 外部キー | contract_id → contracts.contract_id, vendor_id → vendors.vendor_id |
| バージョン | 1.0 |
| 最終更新日 | 2026-01-24 |

## カラム定義

| No. | カラム名 | データ型 | 必須 | 説明 | 制約・備考 |
|-----|----------|----------|------|------|------------|
| 1 | order_id | string | ○ | 発注ID（一意識別子） | 形式: O{0:07d}、例: O0000001 |
| 2 | contract_id | string | ○ | 契約ID | FK: contracts.contract_id |
| 3 | vendor_id | string | ○ | ベンダーID | FK: vendors.vendor_id |
| 4 | vendor_name | string | ○ | ベンダー名（参照用） | 最大長: 200文字 |
| 5 | order_date | date | ○ | 発注日 | 形式: YYYY-MM-DD |
| 6 | order_number | string | ○ | 発注番号 | 最大長: 50文字 |
| 7 | order_amount | integer | ○ | 発注金額 | 単位: 円 |
| 8 | paid_amount | integer | - | 支払済金額 | 単位: 円 |
| 9 | payment_due_date | date | - | 支払予定日 | 形式: YYYY-MM-DD |
| 10 | order_status | string | ○ | 発注ステータス | 発注中, 納品済, 検収済, 支払済, キャンセル |
| 11 | ordering_department | string | ○ | 発注部門 | 最大長: 100文字 |
| 12 | ordering_person | string | ○ | 発注担当者 | 最大長: 100文字 |
| 13 | service_category | string | ○ | サービスカテゴリ | ITシステム開発, ITシステム保守・運用, ITインフラ, 業務委託（IT以外）, コンサルティング, マーケティング支援, 人材派遣, その他 |
| 14 | service_subcategory | string | - | サービスサブカテゴリ | 最大長: 100文字 |
| 15 | work_description | string | - | 業務内容概要 | 最大長: 500文字 |
| 16 | deliverables | string | - | 成果物 | 最大長: 300文字 |
| 17 | notes | string | - | 備考 | 最大長: 500文字 |
