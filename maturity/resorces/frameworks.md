# 製造業の事業会社のIT部門マチュリティ

製造業の事業会社のIT部門マチュリティを測るのであれば、「IT全般のケイパビリティ」をビジネス寄りの言葉で分解して評価できるフレームとして、
- IT-CMF（IT Capability Maturity Framework）
- COBIT系のマチュリティモデル
をベースに、自社向けの尺度を組み合わせて設計するのが実務的です。 [cioindex](https://cioindex.com/topic/it-governance-maturity-models/)

<br>

## 使える代表的なフレーム

- **IT-CMF（IT Capability Maturity Framework）**  
  - ITからビジネス価値を生み出すことを目的に設計された成熟度フレームで、37の「クリティカル・ケイパビリティ」（IT戦略、ポートフォリオ管理、イノベーション管理、ベンダー管理など）を、それぞれ1〜5段階で評価できます。 [ivi](https://ivi.ie/it-capability-maturity-framework/)
  - プロファイルと改善ロードマップがビジネス言語で用意されており、「単なるIT効率」ではなく「ビジネス価値への寄与度」で語りやすいのが特徴です。 [ivi](https://ivi.ie/it-capability-maturity-framework/)

- **COBIT系 ITガバナンス・マチュリティモデル**  
  - COBITのマチュリティモデルは、ガバナンス・マネジメントプロセスを0〜5段階（Non-existent〜Optimized）で評価する枠組みで、戦略、リスク、パフォーマンス測定などの領域ごとに自己評価できます。 [n-able](https://www.n-able.com/es/blog/cobit-framework-overview)
  - 「リスク管理がレベル3＝定義済み、しかしプロアクティブさはまだ弱い」といった形で、改善余地を示すのに向いています。 [cioindex](https://cioindex.com/topic/it-governance-maturity-models/)

- **CMMI／一般的なケイパビリティ・マチュリティモデル**  
  - CMMIや一般的なCMMは、1〜5段階（Initial, Managed, Defined, Quantitatively Managed, Optimizing）でプロセス成熟度を評価する考え方を提供します。 [vti.com](https://vti.com.vn/capability-maturity-model-guide)
  - ITサービスにも適用でき、レベル4以降では統計的・定量的な管理によって、品質やパフォーマンスを予測しながら改善していくことを求めます。 [en.wikipedia](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration)

- **スマートマニュファクチャリング向けマチュリティモデル**  
  - 製造業では、工場ITやOT（制御系）との連携も対象にした「スマートマニュファクチャリング・マチュリティモデル」があり、既存システムの統合から予測的・最適化段階までのステップを定義しています。 [osti](https://www.osti.gov/servlets/purl/1987786)
  - 初期ステップでは基幹システムや制御系の統合・通信の確立、後期ステップでは継続的改善と予測能力の獲得を指標にします。 [osti](https://www.osti.gov/servlets/purl/1987786)

<br>

## 「途中の階段」をどう設計するか

「指示待ちIT → ビジネス価値を共創するIT」「単なる発注窓口 → ベンダー・先進技術との共創ハブ」というゴールに対しては、上記フレームをそのまま使うより、以下のような観点で「自社版マチュリティ項目」を切り出すのが現実的です（IT-CMFのケイパビリティ名を参考にできます）。 [ivi](https://ivi.ie/it-capability-maturity-framework/)

例として、製造業のIT部門に対して次のような軸を設定します：

1. ビジネス連携・価値創造軸  
   - レベル1: 依頼に応じてシステムを個別構築・運用しているが、IT側からの提案はほぼない。  
   - レベル2: 主要部門（製造、物流など）の課題ヒアリングを行い、個別案件ベースで改善提案を出す。  
   - レベル3: 中期事業計画と整合したITロードマップを持ち、部門横断テーマ（生産性、在庫削減、リードタイム短縮）で共通KPIを設定している。  
   - レベル4: IT投資ポートフォリオをROI・KPIでモニタリングし、達成度に応じて優先順位を見直す運用が回っている（IT-CMFのポートフォリオ管理・価値管理の発想）。 [ivi](https://ivi.ie/it-capability-maturity-framework/)
   - レベル5: 新事業・新ビジネスモデル（サービス化、データビジネス等）の企画段階からITが共同責任者として参画し、継続的に価値創出を検証・改善している。

2. ベンダー・外部機関との共創軸  
   - レベル1: 価格と納期を基準にした発注窓口として機能しているだけ（COBITのSupplier Agreement Managementがレベル2程度の状態に相当）。 [en.wikipedia](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration)
   - レベル2: SLAや成果物基準が整備され、主要ベンダーの評価・レビューを定期的に実施している。  
   - レベル3: 戦略パートナーとして位置づけられたベンダーとは中期ロードマップを共有し、PoCや技術検証を共に進めている。  
   - レベル4: 大学・スタートアップ・機械メーカーなども含めた「エコシステム」として、複数社共創のテーマ（スマートファクトリー、予知保全など）を運用している（IT-CMFのイノベーション管理に近い観点）。 [ivi](https://ivi.ie/it-capability-maturity-framework/)
   - レベル5: ビジネス側と一体となってオープンイノベーション・コンソーシアムへの参画や、新規サービスの共同開発・共同知財化まで行っている。

3. ITガバナンス・プロセス軸  
   - COBITマチュリティ（0〜5）やCMMIの1〜5レベルを引用しつつ、「プロセスが存在しない／属人」「標準化」「定量管理」「継続的最適化」という段階を設定できます。 [n-able](https://www.n-able.com/es/blog/cobit-framework-overview)
   - 例えば「変更管理」「需要管理」「投資評価」「セキュリティ・OTセキュリティ」など、製造業に重要なプロセスを個別に評価します。 [cioindex](https://cioindex.com/topic/it-governance-maturity-models/)

4. デジタル／スマートマニュファクチャリング軸  
   - 生産設備・MES・ERP・物流システムなどがどの程度統合され、データ駆動で最適化されているかを、スマートマニュファクチャリング・マチュリティモデルのステップを参考に段階化できます。 [osti](https://www.osti.gov/servlets/purl/1987786)
   - 「システムがバラバラ」「工場内は連携しているが本社と弱い」「エンドツーエンドで可視化」「予測・最適化」といった階段です。 [osti](https://www.osti.gov/servlets/purl/1987786)

<br>

## 実務での進め方（イメージ）

1. ベースフレームの選定  
   - 「ITからのビジネス価値」を中心に置くならIT-CMFを骨格にし。 [ivi](https://ivi.ie/it-capability-maturity-framework/)
   - ガバナンス・内部統制を重視するならCOBITマチュリティモデルを補助的に使うのが良いです。 [n-able](https://www.n-able.com/es/blog/cobit-framework-overview)

2. 製造業向けに観点をカスタマイズ  
   - 研究開発・製造・物流・品質管理・販売チャネル（卸）のバリューチェーンを並べ、それぞれにIT／デジタルがどの程度組み込まれているかを見る観点を追加します。  
   - あわせて、スマートマニュファクチャリングの成熟度ステップを、工場IT・OT統合の軸として入れると「現場側からも納得しやすい」マップになります。 [osti](https://www.osti.gov/servlets/purl/1987786)

3. 自社版マチュリティマップの作成  
   - 各軸を1〜5レベルで文章化し、「今は2〜3」「3から4に上げるには何が必要か」を議論できる状態にします。  
   - IT-CMFのように、各レベルに対して改善ロードマップ（次にやるべきプラクティス）を明確にしておくと、途中の階段が見えるようになります。 [ivi](https://ivi.ie/it-capability-maturity-framework/)

4. KPI・事例の紐づけ  
   - 例えば「ビジネス連携レベル3→4」への移行には、「IT投資案件のうちビジネス側でKPIを持つ案件比率」「投資後1年以内の効果検証率」など、具体的KPIをひも付けます。  
   - 共創軸では、「共創PoC件数」「既存製品・プロセスの改善に結びついた共創案件比率」などが考えられます。

***
