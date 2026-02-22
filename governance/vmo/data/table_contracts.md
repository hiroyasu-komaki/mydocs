# テーブル定義書：contracts

| 項目 | 内容 |
|------|------|
| テーブル名 | contracts |
| 説明 | 個別契約の基本情報と条件 |
| 主キー | contract_id |
| 外部キー | vendor_id → vendors.vendor_id |
| バージョン | 1.0 |
| 最終更新日 | 2026-01-24 |

## カラム定義

| No. | カラム名 | データ型 | 必須 | 説明 | 制約・備考 |
|-----|----------|----------|------|------|------------|
| 1 | contract_id | string | ○ | 契約ID（一意識別子） | 形式: C{0:06d}、例: C000001 |
| 2 | vendor_id | string | ○ | ベンダーID | FK: vendors.vendor_id |
| 3 | vendor_name | string | ○ | ベンダー名（参照用） | 最大長: 200文字 |
| 4 | contract_number | string | ○ | 契約番号（社内管理番号） | 最大長: 50文字 |
| 5 | contract_name | string | ○ | 契約名称 | 最大長: 200文字 |
| 6 | contract_type | string | ○ | 契約形態 | 固定金額（一括）, 固定金額（月額）, 準委任（人月）, 準委任（時間単価）, 成果報酬, その他 |
| 7 | contract_start_date | date | ○ | 契約開始日 | 形式: YYYY-MM-DD |
| 8 | contract_end_date | date | ○ | 契約終了日 | 形式: YYYY-MM-DD |
| 9 | contract_duration_months | integer | ○ | 契約期間（月数） | 単位: 月 |
| 10 | total_contract_amount | integer | ○ | 契約金額合計 | 単位: 円 |
| 11 | monthly_amount | integer | - | 月額換算金額 | 単位: 円 |
| 12 | annual_amount | integer | - | 年額換算金額 | 単位: 円 |
| 13 | auto_renewal_flag | boolean | ○ | 自動更新フラグ | - |
| 14 | renewal_count | integer | - | 更新回数 | - |
| 15 | contract_signed_date | date | - | 契約締結日 | 形式: YYYY-MM-DD |
| 16 | contract_department | string | ○ | 契約担当部門 | 最大長: 100文字 |
| 17 | contract_owner | string | ○ | 契約担当者 | 最大長: 100文字 |
| 18 | has_sla | boolean | ○ | SLA定義有無 | - |
| 19 | has_kpi | boolean | ○ | KPI定義有無 | - |
| 20 | termination_terms | string | - | 解約条件 | 最大長: 500文字 |
| 21 | payment_terms | string | ○ | 支払条件 | 月次払い, 四半期払い, 半期払い, 年次払い, 都度払い |
| 22 | contract_file_location | string | - | 契約書保管場所 | 最大長: 300文字 |
| 23 | contract_status | string | ○ | 契約ステータス | 有効, 期限切れ, 解約済, 更新予定 |
