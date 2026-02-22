"""
データ分析集計処理モジュール
ベンダー支出データを集計・分析する
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional


class DataAnalyzer:
    """ベンダーマネジメントデータの分析・集計を行うクラス"""
    
    def __init__(self, data_dir: Path):
        """
        Args:
            data_dir: CSVデータが格納されているディレクトリ
        """
        self.data_dir = data_dir
        self.vendors = None
        self.contracts = None
        self.orders = None
        self.services = None
        
    def load_data(self):
        """CSVファイルを読み込む"""
        print("📁 データファイルを読み込み中...")
        
        try:
            self.vendors = pd.read_csv(
                self.data_dir / 'vendors.csv', 
                encoding='utf-8-sig'
            )
            print(f"  ✓ ベンダーマスタ: {len(self.vendors)}件")
            
            self.contracts = pd.read_csv(
                self.data_dir / 'contracts.csv', 
                encoding='utf-8-sig'
            )
            print(f"  ✓ 契約データ: {len(self.contracts)}件")
            
            self.orders = pd.read_csv(
                self.data_dir / 'orders.csv', 
                encoding='utf-8-sig'
            )
            print(f"  ✓ 発注データ: {len(self.orders)}件")
            
            self.services = pd.read_csv(
                self.data_dir / 'services.csv', 
                encoding='utf-8-sig'
            )
            print(f"  ✓ サービス詳細: {len(self.services)}件")
            
            print()
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"データファイルが見つかりません: {e}")
        except Exception as e:
            raise Exception(f"データ読み込みエラー: {e}")
    
    def analyze_vendor_spend(self) -> pd.DataFrame:
        """
        ベンダー別支出分析
        
        Returns:
            ベンダー別集計結果のDataFrame
        """
        print("📊 ベンダー別支出を分析中...")
        
        # 有効な契約の年間支出を集計
        active_contracts = self.contracts[self.contracts['contract_status'] == '有効']
        vendor_spend = active_contracts.groupby('vendor_id').agg({
            'vendor_name': 'first',
            'annual_amount': 'sum',
            'contract_id': 'count'
        }).reset_index()
        
        vendor_spend.columns = ['vendor_id', 'vendor_name', 'total_annual_spend', 'contract_count']
        
        # ベンダー情報を結合
        vendor_spend = vendor_spend.merge(
            self.vendors[['vendor_id', 'vendor_classification', 'industry', 'vendor_rating']],
            on='vendor_id',
            how='left'
        )
        
        # 構成比を計算
        total_spend = vendor_spend['total_annual_spend'].sum()
        vendor_spend['spend_ratio'] = (vendor_spend['total_annual_spend'] / total_spend * 100).round(2)
        
        # 累積構成比を計算
        vendor_spend = vendor_spend.sort_values('total_annual_spend', ascending=False)
        vendor_spend['cumulative_ratio'] = vendor_spend['spend_ratio'].cumsum().round(2)
        
        # ランク付け
        vendor_spend['rank'] = range(1, len(vendor_spend) + 1)
        
        print(f"  ✓ {len(vendor_spend)}ベンダーの支出を集計しました")
        print(f"  ✓ 総支出額: ¥{total_spend:,.0f}")
        print()
        
        return vendor_spend[['rank', 'vendor_id', 'vendor_name', 'vendor_classification', 
                             'industry', 'vendor_rating', 'total_annual_spend', 
                             'contract_count', 'spend_ratio', 'cumulative_ratio']]
    
    def analyze_category_spend(self) -> pd.DataFrame:
        """
        サービスカテゴリ別支出分析
        
        Returns:
            カテゴリ別集計結果のDataFrame
        """
        print("📊 サービスカテゴリ別支出を分析中...")
        
        # 支払済の発注データで集計
        paid_orders = self.orders[self.orders['order_status'] == '支払済']
        category_spend = paid_orders.groupby('service_category').agg({
            'order_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        category_spend.columns = ['service_category', 'total_spend', 'order_count']
        
        # 構成比を計算
        total_spend = category_spend['total_spend'].sum()
        category_spend['spend_ratio'] = (category_spend['total_spend'] / total_spend * 100).round(2)
        
        # 平均発注額を計算
        category_spend['avg_order_amount'] = (category_spend['total_spend'] / category_spend['order_count']).round(0)
        
        # 降順ソート
        category_spend = category_spend.sort_values('total_spend', ascending=False)
        category_spend['rank'] = range(1, len(category_spend) + 1)
        
        print(f"  ✓ {len(category_spend)}カテゴリの支出を集計しました")
        print(f"  ✓ 総支出額: ¥{total_spend:,.0f}")
        print()
        
        return category_spend[['rank', 'service_category', 'total_spend', 
                               'order_count', 'avg_order_amount', 'spend_ratio']]
    
    def analyze_contract_type_spend(self) -> pd.DataFrame:
        """
        契約形態別支出分析
        
        Returns:
            契約形態別集計結果のDataFrame
        """
        print("📊 契約形態別支出を分析中...")
        
        # 有効な契約で集計
        active_contracts = self.contracts[self.contracts['contract_status'] == '有効']
        contract_type_spend = active_contracts.groupby('contract_type').agg({
            'annual_amount': 'sum',
            'contract_id': 'count',
            'monthly_amount': 'mean'
        }).reset_index()
        
        contract_type_spend.columns = ['contract_type', 'total_annual_spend', 
                                        'contract_count', 'avg_monthly_amount']
        
        # 構成比を計算
        total_spend = contract_type_spend['total_annual_spend'].sum()
        contract_type_spend['spend_ratio'] = (contract_type_spend['total_annual_spend'] / total_spend * 100).round(2)
        
        # 降順ソート
        contract_type_spend = contract_type_spend.sort_values('total_annual_spend', ascending=False)
        contract_type_spend['rank'] = range(1, len(contract_type_spend) + 1)
        
        print(f"  ✓ {len(contract_type_spend)}契約形態の支出を集計しました")
        print(f"  ✓ 総支出額: ¥{total_spend:,.0f}")
        print()
        
        return contract_type_spend[['rank', 'contract_type', 'total_annual_spend', 
                                     'contract_count', 'avg_monthly_amount', 'spend_ratio']]
    
    def analyze_unit_price_variance(self) -> tuple:
        """
        契約単価・単価レンジのばらつき分析
        
        Returns:
            Tuple[カテゴリ別単価分析DataFrame, 単価詳細DataFrame]
        """
        print("📊 契約単価のばらつきを分析中...")
        
        # 有効な契約のみを対象
        active_contracts = self.contracts[self.contracts['contract_status'] == '有効'].copy()
        
        # 月額単価が存在する契約のみ
        contracts_with_price = active_contracts[active_contracts['monthly_amount'] > 0].copy()
        
        # 契約データにカテゴリ情報を付与（ordersから取得）
        # 各契約の主要カテゴリを特定
        order_categories = self.orders.groupby('contract_id')['service_category'].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
        ).reset_index()
        order_categories.columns = ['contract_id', 'primary_category']
        
        contracts_with_price = contracts_with_price.merge(
            order_categories,
            on='contract_id',
            how='left'
        )
        
        # カテゴリ別に単価を分析
        category_stats = contracts_with_price.groupby('primary_category')['monthly_amount'].agg([
            ('contract_count', 'count'),
            ('avg_price', 'mean'),
            ('median_price', 'median'),
            ('min_price', 'min'),
            ('max_price', 'max'),
            ('std_price', 'std')
        ]).reset_index()
        
        # ばらつき係数（変動係数）を計算
        category_stats['cv'] = (category_stats['std_price'] / category_stats['avg_price'] * 100).round(2)
        
        # 価格レンジを計算
        category_stats['price_range'] = category_stats['max_price'] - category_stats['min_price']
        category_stats['range_ratio'] = (category_stats['price_range'] / category_stats['avg_price'] * 100).round(2)
        
        # NaN値を処理（契約が1件のみの場合など）
        category_stats['cv'] = category_stats['cv'].fillna(0)
        category_stats['std_price'] = category_stats['std_price'].fillna(0)
        
        # 全カテゴリを対象（1件のカテゴリも含む）
        category_stats_filtered = category_stats.copy()
        
        # ばらつきが大きい順にソート
        category_stats_filtered = category_stats_filtered.sort_values('cv', ascending=False)
        category_stats_filtered['rank'] = range(1, len(category_stats_filtered) + 1)
        
        print(f"  ✓ {len(category_stats_filtered)}カテゴリの単価を分析しました")
        
        
        # ばらつきが大きいカテゴリを警告（2件以上のみ）
        high_variance = category_stats_filtered[(category_stats_filtered['cv'] > 30) & 
                                                 (category_stats_filtered['contract_count'] >= 2)]
        if len(high_variance) > 0:
            print(f"  ⚠️  単価ばらつきが大きいカテゴリ: {len(high_variance)}件（CV > 30%）")
        
        # 1件のみのカテゴリを表示
        single_contract = category_stats_filtered[category_stats_filtered['contract_count'] == 1]
        if len(single_contract) > 0:
            print(f"  📌 契約1件のみのカテゴリ: {len(single_contract)}件（ばらつき分析対象外）")
        
        print()
        # 詳細データ：カテゴリ別・ベンダー別の単価リスト
        unit_price_details = contracts_with_price[['contract_id', 'vendor_id', 'vendor_name', 
                                                     'primary_category', 'contract_type', 
                                                     'monthly_amount']].copy()
        unit_price_details = unit_price_details.sort_values(['primary_category', 'monthly_amount'], 
                                                             ascending=[True, False])
        
        return category_stats_filtered, unit_price_details
    
    def analyze_pareto(self) -> Tuple[pd.DataFrame, Dict]:
        """
        パレート分析（80/20ルール）
        
        Returns:
            Tuple[パレート分析結果のDataFrame, サマリー辞書]
        """
        print("📊 パレート分析（80/20ルール）を実行中...")
        
        # ベンダー別支出を取得
        vendor_spend = self.analyze_vendor_spend()
        
        # 累積80%に達するベンダーを特定
        vendors_80 = vendor_spend[vendor_spend['cumulative_ratio'] <= 80]
        
        # サマリー情報
        total_vendors = len(vendor_spend)
        vendors_80_count = len(vendors_80)
        vendors_80_ratio = round(vendors_80_count / total_vendors * 100, 2)
        spend_80_amount = vendors_80['total_annual_spend'].sum()
        total_spend = vendor_spend['total_annual_spend'].sum()
        
        summary = {
            'total_vendors': total_vendors,
            'vendors_for_80_percent': vendors_80_count,
            'vendor_ratio': vendors_80_ratio,
            'spend_80_amount': spend_80_amount,
            'total_spend': total_spend,
            'spend_80_ratio': round(spend_80_amount / total_spend * 100, 2)
        }
        
        print(f"  ✓ 全ベンダー数: {total_vendors}社")
        print(f"  ✓ 支出の80%を占めるベンダー: {vendors_80_count}社 ({vendors_80_ratio}%)")
        print(f"  ✓ 上位ベンダーの支出額: ¥{spend_80_amount:,.0f} ({summary['spend_80_ratio']}%)")
        print()
        
        return vendor_spend, summary
        """
        契約単価・単価レンジのばらつき分析
        
        Returns:
            Tuple[カテゴリ別単価分析DataFrame, 単価詳細DataFrame]
        """
        print("📊 契約単価のばらつきを分析中...")
        
        # 有効な契約のみを対象
        active_contracts = self.contracts[self.contracts['contract_status'] == '有効'].copy()
        
        # 月額単価が存在する契約のみ
        contracts_with_price = active_contracts[active_contracts['monthly_amount'] > 0].copy()
        
        # 契約データにカテゴリ情報を付与（ordersから取得）
        # 各契約の主要カテゴリを特定
        order_categories = self.orders.groupby('contract_id')['service_category'].agg(
            lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
        ).reset_index()
        order_categories.columns = ['contract_id', 'primary_category']
        
        contracts_with_price = contracts_with_price.merge(
            order_categories,
            on='contract_id',
            how='left'
        )
        
        # カテゴリ別に単価を分析
        category_stats = contracts_with_price.groupby('primary_category')['monthly_amount'].agg([
            ('contract_count', 'count'),
            ('avg_price', 'mean'),
            ('median_price', 'median'),
            ('min_price', 'min'),
            ('max_price', 'max'),
            ('std_price', 'std')
        ]).reset_index()
        
        # ばらつき係数（変動係数）を計算
        category_stats['cv'] = (category_stats['std_price'] / category_stats['avg_price'] * 100).round(2)
        
        # 価格レンジを計算
        category_stats['price_range'] = category_stats['max_price'] - category_stats['min_price']
        category_stats['range_ratio'] = (category_stats['price_range'] / category_stats['avg_price'] * 100).round(2)
        
        # NaN値を処理（契約が1件のみの場合など）
        category_stats['cv'] = category_stats['cv'].fillna(0)
        category_stats['std_price'] = category_stats['std_price'].fillna(0)
        
        # 契約数でフィルタ（2件以上のカテゴリのみ）
        category_stats_filtered = category_stats[category_stats['contract_count'] >= 2].copy()
        
        # ばらつきが大きい順にソート
        category_stats_filtered = category_stats_filtered.sort_values('cv', ascending=False)
        category_stats_filtered['rank'] = range(1, len(category_stats_filtered) + 1)
        
        print(f"  ✓ {len(category_stats_filtered)}カテゴリの単価を分析しました")
        
        # ばらつきが大きいカテゴリを警告
        high_variance = category_stats_filtered[category_stats_filtered['cv'] > 30]
        if len(high_variance) > 0:
            print(f"  ⚠️  単価ばらつきが大きいカテゴリ: {len(high_variance)}件（CV > 30%）")
        
        print()
        
        # 詳細データ：カテゴリ別・ベンダー別の単価リスト
        unit_price_details = contracts_with_price[['contract_id', 'vendor_id', 'vendor_name', 
                                                     'primary_category', 'contract_type', 
                                                     'monthly_amount']].copy()
        unit_price_details = unit_price_details.sort_values(['primary_category', 'monthly_amount'], 
                                                             ascending=[True, False])
        
        return category_stats_filtered, unit_price_details
    
    def analyze_auto_renewal(self) -> pd.DataFrame:
        """
        自動更新契約の分析
        
        Returns:
            自動更新契約の集計結果のDataFrame
        """
        print("📊 自動更新契約を分析中...")
        
        # 有効な契約のみを対象
        active_contracts = self.contracts[self.contracts['contract_status'] == '有効']
        
        # 自動更新フラグで集計
        auto_renewal_analysis = active_contracts.groupby('auto_renewal_flag').agg({
            'contract_id': 'count',
            'annual_amount': 'sum',
            'renewal_count': 'mean'
        }).reset_index()
        
        auto_renewal_analysis.columns = ['auto_renewal_flag', 'contract_count', 
                                          'annual_amount', 'avg_renewal_count']
        
        # 構成比を計算
        total_contracts = auto_renewal_analysis['contract_count'].sum()
        auto_renewal_analysis['contract_ratio'] = (auto_renewal_analysis['contract_count'] / total_contracts * 100).round(2)
        
        total_amount = auto_renewal_analysis['annual_amount'].sum()
        auto_renewal_analysis['amount_ratio'] = (auto_renewal_analysis['annual_amount'] / total_amount * 100).round(2)
        
        print(f"  ✓ 自動更新契約を分析しました")
        
        # 自動更新契約の詳細情報
        auto_contracts = auto_renewal_analysis[auto_renewal_analysis['auto_renewal_flag'] == True]
        if not auto_contracts.empty:
            print(f"  ✓ 自動更新契約: {auto_contracts['contract_count'].values[0]}件 ({auto_contracts['contract_ratio'].values[0]}%)")
            print(f"  ✓ 平均更新回数: {auto_contracts['avg_renewal_count'].values[0]:.1f}回")
        
        print()
        
        return auto_renewal_analysis
    
    def save_analysis_results(self, output_dir: Path):
        """
        分析結果をCSVファイルに保存
        
        Args:
            output_dir: 出力先ディレクトリ
        """
        print("💾 分析結果を保存中...\n")
        
        output_dir.mkdir(exist_ok=True)
        
        # 1. ベンダー別支出分析
        vendor_spend = self.analyze_vendor_spend()
        vendor_spend.to_csv(
            output_dir / 'vendor_spend_analysis.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ vendor_spend_analysis.csv")
        
        # 2. サービスカテゴリ別支出分析
        category_spend = self.analyze_category_spend()
        category_spend.to_csv(
            output_dir / 'category_spend_analysis.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ category_spend_analysis.csv")
        
        # 3. 契約形態別支出分析
        contract_type_spend = self.analyze_contract_type_spend()
        contract_type_spend.to_csv(
            output_dir / 'contract_type_spend_analysis.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ contract_type_spend_analysis.csv")
        
        # 4. パレート分析
        pareto_data, pareto_summary = self.analyze_pareto()
        pareto_data.to_csv(
            output_dir / 'pareto_analysis.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ pareto_analysis.csv")
        
        # パレート分析サマリー
        summary_df = pd.DataFrame([pareto_summary])
        summary_df.to_csv(
            output_dir / 'pareto_summary.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ pareto_summary.csv")
        
        # 5. 契約単価・単価レンジ分析（NEW）
        unit_price_stats, unit_price_details = self.analyze_unit_price_variance()
        unit_price_stats.to_csv(
            output_dir / 'unit_price_analysis.csv',
            index=False,
            encoding='utf-8-sig'
        )
        print(f"  ✓ unit_price_analysis.csv")
        
        unit_price_details.to_csv(
            output_dir / 'unit_price_details.csv',
            index=False,
            encoding='utf-8-sig'
        )
        print(f"  ✓ unit_price_details.csv")
        
        # 6. 自動更新契約分析
        auto_renewal = self.analyze_auto_renewal()
        auto_renewal.to_csv(
            output_dir / 'auto_renewal_analysis.csv', 
            index=False, 
            encoding='utf-8-sig'
        )
        print(f"  ✓ auto_renewal_analysis.csv")
        
        print(f"\n✅ 全ての分析結果を保存しました: {output_dir}\n")
