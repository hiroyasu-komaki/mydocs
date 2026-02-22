# テーブル定義書：services

| 項目 | 内容 |
|------|------|
| テーブル名 | services |
| 説明 | 提供されるサービスの詳細情報 |
| 主キー | service_id |
| 外部キー | contract_id → contracts.contract_id, vendor_id → vendors.vendor_id |
| バージョン | 1.0 |
| 最終更新日 | 2026-01-24 |

## カラム定義

| No. | カラム名 | データ型 | 必須 | 説明 | 制約・備考 |
|-----|----------|----------|------|------|------------|
| 1 | service_id | string | ○ | サービスID（一意識別子） | 形式: S{0:06d}、例: S000001 |
| 2 | contract_id | string | ○ | 契約ID | FK: contracts.contract_id |
| 3 | vendor_id | string | ○ | ベンダーID | FK: vendors.vendor_id |
| 4 | service_name | string | ○ | サービス名 | 最大長: 200文字 |
| 5 | service_category | string | ○ | サービスカテゴリ | ITシステム開発, ITシステム保守・運用, ITインフラ, 業務委託（IT以外）, コンサルティング, マーケティング支援, 人材派遣, その他 |
| 6 | service_subcategory | string | - | サービスサブカテゴリ | 最大長: 100文字 |
| 7 | service_description | string | - | サービス内容詳細 | 最大長: 1000文字 |
| 8 | service_scope | string | - | 提供範囲 | 最大長: 500文字 |
| 9 | deliverable_definition | string | - | 成果物定義 | 最大長: 500文字 |
| 10 | sla_items | string | - | SLA項目 | 最大長: 300文字 |
| 11 | sla_target | string | - | SLA目標値 | 最大長: 200文字 |
| 12 | kpi_items | string | - | KPI項目 | 最大長: 300文字 |
| 13 | kpi_target | string | - | KPI目標値 | 最大長: 200文字 |
| 14 | performance_rating | integer | - | 実績評価（5段階） | 1〜5 |
| 15 | usage_frequency | string | - | 利用頻度 | 日次, 週次, 月次, 四半期, 随時, 未使用 |
| 16 | actual_utilization_rate | float | - | 実稼働率（%） | 0〜100、単位: % |
| 17 | resource_count | float | - | 提供人数/工数 | 単位: 人月または時間 |
| 18 | unit_price | integer | - | 単価 | 単位: 円 |
| 19 | unit_price_type | string | - | 単価単位 | 人月, 人日, 時間, 件, 式 |
| 20 | business_criticality | string | - | 事業クリティカル度 | 高, 中, 低 |
| 21 | replaceability | string | - | 代替可能性 | 容易, 普通, 困難 |
| 22 | service_start_date | date | - | サービス開始日 | 形式: YYYY-MM-DD |
| 23 | last_used_date | date | - | 最終利用日 | 形式: YYYY-MM-DD |
| 24 | notes | string | - | 備考 | 最大長: 500文字 |
