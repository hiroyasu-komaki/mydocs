"""
データ分析モジュール - ITガバナンス実態調査対応版

前処理済みデータから以下の分析を実行:
- 基本集計（選択率、部門別集計）
- セキュリティ成熟度スコアリング
- 困りごと分析
- 部門別プロファイル
- 5つの可視化のためのデータ準備
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
from modules.util import load_yaml, save_json


class ITGovernanceAnalyser:
    """ITガバナンス実態調査データ分析クラス"""
    
    def __init__(self, 
                 config_path='config/config.yaml',
                 questions_path='config/survey_questions.yaml'):
        """初期化"""
        self.config = load_yaml(config_path)
        self.questions = load_yaml(questions_path)
        self.data = None
        self.raw_data = None
        self.analysis_results = {}
    
    def load_data(self, 
                  preprocessed_path=None,
                  raw_path=None):
        """
        データを読み込む
        
        Args:
            preprocessed_path: 前処理済みデータのパス
            raw_path: 生データのパス（オプション、一部の分析で使用）
        """
        if preprocessed_path is None:
            preprocessed_path = self.config['paths']['preprocessed_data']
        
        print(f"\n前処理済みデータを読み込み中: {preprocessed_path}")
        self.data = pd.read_csv(preprocessed_path, encoding='utf-8-sig')
        print(f"✓ 読み込み完了: {self.data.shape[0]}行 × {self.data.shape[1]}列")
        
        # 生データも読み込み（テキスト項目の分析用）
        if raw_path is None:
            raw_path = self.config['paths']['raw_data']
        
        try:
            print(f"\n生データを読み込み中: {raw_path}")
            self.raw_data = pd.read_csv(raw_path, encoding='utf-8-sig')
            print(f"✓ 読み込み完了: {self.raw_data.shape[0]}行 × {self.raw_data.shape[1]}列")
        except FileNotFoundError:
            print("⚠️ 生データが見つかりません（一部の分析は制限されます）")
            self.raw_data = None
    
    # ==========================================
    # 1. 基本集計
    # ==========================================
    
    def calculate_selection_rates(self):
        """
        複数選択質問の選択率を計算
        
        Returns:
            dict: セクション別・質問別の選択率
        """
        print("\n[1/7] 選択率の計算中...")
        
        selection_rates = {}
        
        sections = {
            'section1': 'section1_tech_adoption',
            'section2': 'section2_security',
            'section3': 'section3_data_handling',
            'section4': 'section4_change_trouble',
            'section5': 'section5_budget',
            'section6': 'section6_vendor',
            'section7': 'section7_others'
        }
        
        for section_key, section_name in sections.items():
            if section_name not in self.questions:
                continue
            
            selection_rates[section_key] = {}
            
            for q in self.questions[section_name]:
                if q['type'] not in ['multiple_choice', 'single_choice']:
                    continue
                
                question = q['question']
                options = q['options']
                q_id = q['id']
                
                # 各選択肢の選択率を計算
                rates = {}
                for opt in options:
                    col_name = f'{question}_{opt}'
                    if col_name in self.data.columns:
                        selection_count = self.data[col_name].sum()
                        selection_rate = (selection_count / len(self.data)) * 100
                        rates[opt] = {
                            'count': int(selection_count),
                            'rate': float(selection_rate)
                        }
                
                selection_rates[section_key][q_id] = {
                    'question': question,
                    'type': q['type'],
                    'rates': rates
                }
        
        print(f"  ✓ {len(selection_rates)}セクションの選択率を計算")
        return selection_rates
    
    def calculate_department_breakdown(self):
        """
        部門別の回答分布を計算
        
        Returns:
            dict: 部門別の基本情報
        """
        print("\n[2/7] 部門別回答分布の計算中...")
        
        if self.raw_data is None:
            print("  ⚠️ 生データがないため、部門別分析をスキップします")
            return {}
        
        breakdown = {}
        
        # 地域別
        if '地域' in self.raw_data.columns:
            region_counts = self.raw_data['地域'].value_counts()
            breakdown['by_region'] = {
                region: {
                    'count': int(count),
                    'percentage': float((count / len(self.raw_data)) * 100)
                }
                for region, count in region_counts.items()
            }
        
        # 所属部門別
        if '所属部門' in self.raw_data.columns:
            dept_counts = self.raw_data['所属部門'].value_counts()
            breakdown['by_department'] = {
                dept: {
                    'count': int(count),
                    'percentage': float((count / len(self.raw_data)) * 100)
                }
                for dept, count in dept_counts.items()
            }
        
        # IT予算規模別
        if '昨年度IT予算執行額' in self.raw_data.columns:
            budget_col = self.raw_data['昨年度IT予算執行額']
            budget_ranges = {
                '100万円未満': (0, 100),
                '100-500万円': (100, 500),
                '500-1000万円': (500, 1000),
                '1000-5000万円': (1000, 5000),
                '5000万円以上': (5000, 100000)
            }
            
            budget_breakdown = {}
            for range_name, (min_val, max_val) in budget_ranges.items():
                count = ((budget_col >= min_val) & (budget_col < max_val)).sum()
                budget_breakdown[range_name] = {
                    'count': int(count),
                    'percentage': float((count / len(budget_col)) * 100)
                }
            
            breakdown['by_budget'] = budget_breakdown
        
        print(f"  ✓ 部門別分布を計算")
        return breakdown
    
    # ==========================================
    # 2. セキュリティ成熟度分析
    # ==========================================
    
    def calculate_security_maturity(self):
        """
        セキュリティ成熟度スコアを計算
        
        Returns:
            dict: 全体および部門別のセキュリティ成熟度
        """
        print("\n[3/7] セキュリティ成熟度の計算中...")
        
        # セキュリティ関連の質問項目を定義
        security_items = {
            # セクション2の質問
            'セキュリティ設計': 'システムの設計・検討段階で、セキュリティをどのように考慮していますか？',
            'MFA利用': 'ID・アクセス管理 - 認証方法',
            '権限管理': 'ID・アクセス管理 - 権限管理',
            'データ保護': 'データの保護設計はどうなっていますか？',
            'リリース前検証': 'リリース前の検証・評価はどうしていますか？'
        }
        
        # スコアリング基準
        positive_keywords = [
            '企画段階でセキュリティ要件',
            'MFA',
            '役割ベース',
            '暗号化',
            '脆弱性診断'
        ]
        
        negative_keywords = [
            '特に明文化された設計プロセスはない',
            '単一パスワード',
            '共通アカウント',
            'システム任せ',
            '特になし'
        ]
        
        # 全体スコアを計算
        total_score = 0
        max_score = 0
        item_scores = {}
        
        for item_name, question in security_items.items():
            # 該当する列を探す
            item_cols = [col for col in self.data.columns if question in col and col != '回答者ID']
            
            if not item_cols:
                continue
            
            # 各項目のスコアを計算
            item_score = 0
            item_max = len(item_cols)
            
            for col in item_cols:
                # ポジティブな項目が選択されているかチェック
                is_positive = any(kw in col for kw in positive_keywords)
                is_negative = any(kw in col for kw in negative_keywords)
                
                if is_positive:
                    item_score += self.data[col].sum()
                elif is_negative:
                    # ネガティブ項目は減点
                    item_score -= self.data[col].sum() * 0.5
            
            item_scores[item_name] = {
                'score': float(item_score),
                'max_score': item_max * len(self.data),
                'percentage': float((item_score / (item_max * len(self.data))) * 100) if item_max > 0 else 0
            }
            
            total_score += item_score
            max_score += item_max * len(self.data)
        
        overall_maturity = {
            'total_score': float(total_score),
            'max_score': float(max_score),
            'percentage': float((total_score / max_score) * 100) if max_score > 0 else 0,
            'maturity_level': self._classify_maturity_level((total_score / max_score) * 100 if max_score > 0 else 0),
            'item_scores': item_scores
        }
        
        # 部門別のスコアリング（生データがある場合）
        department_maturity = {}
        if self.raw_data is not None and '所属部門' in self.raw_data.columns:
            for dept in self.raw_data['所属部門'].unique():
                dept_indices = self.raw_data[self.raw_data['所属部門'] == dept].index
                dept_data = self.data.iloc[dept_indices]
                
                dept_score = 0
                dept_max = 0
                
                for item_name, question in security_items.items():
                    item_cols = [col for col in dept_data.columns if question in col and col != '回答者ID']
                    
                    for col in item_cols:
                        is_positive = any(kw in col for kw in positive_keywords)
                        is_negative = any(kw in col for kw in negative_keywords)
                        
                        if is_positive:
                            dept_score += dept_data[col].sum()
                        elif is_negative:
                            dept_score -= dept_data[col].sum() * 0.5
                    
                    dept_max += len(item_cols) * len(dept_data)
                
                department_maturity[dept] = {
                    'score': float(dept_score),
                    'max_score': float(dept_max),
                    'percentage': float((dept_score / dept_max) * 100) if dept_max > 0 else 0,
                    'maturity_level': self._classify_maturity_level((dept_score / dept_max) * 100 if dept_max > 0 else 0),
                    'respondent_count': int(len(dept_data))
                }
        
        print(f"  ✓ セキュリティ成熟度を計算（全体: {overall_maturity['maturity_level']}）")
        
        return {
            'overall': overall_maturity,
            'by_department': department_maturity
        }
    
    def _classify_maturity_level(self, percentage):
        """成熟度レベルを分類"""
        if percentage >= 80:
            return '高'
        elif percentage >= 50:
            return '中'
        else:
            return '低'
    
    # ==========================================
    # 3. 困りごと分析
    # ==========================================
    
    def analyze_pain_points(self):
        """
        困りごと（課題）を分析
        
        Returns:
            dict: 困りごとの頻出ランキングと分類
        """
        print("\n[4/7] 困りごと分析中...")
        
        # 困りごと系の質問を抽出
        pain_point_questions = []
        
        sections = [
            'section1_tech_adoption',
            'section2_security',
            'section3_data_handling',
            'section4_change_trouble',
            'section5_budget',
            'section6_vendor',
            'section7_others'
        ]
        
        for section_name in sections:
            if section_name not in self.questions:
                continue
            
            for q in self.questions[section_name]:
                # 「困ること」「課題」を含む質問を抽出
                if '困る' in q['question'] or '課題' in q['question'] or '困っている' in q['question']:
                    pain_point_questions.append({
                        'section': section_name,
                        'question': q['question'],
                        'options': q['options'],
                        'q_id': q['id']
                    })
        
        # 各困りごとの選択数を集計
        all_pain_points = []
        
        for pq in pain_point_questions:
            question = pq['question']
            options = pq['options']
            
            for opt in options:
                if '特に困っていない' in opt or 'その他' in opt:
                    continue
                
                col_name = f'{question}_{opt}'
                if col_name in self.data.columns:
                    count = self.data[col_name].sum()
                    if count > 0:
                        all_pain_points.append({
                            'section': pq['section'].replace('section', 'セクション').replace('_', ' '),
                            'category': self._categorize_pain_point(opt),
                            'pain_point': opt,
                            'count': int(count),
                            'rate': float((count / len(self.data)) * 100)
                        })
        
        # 頻出順にソート
        all_pain_points.sort(key=lambda x: x['count'], reverse=True)
        
        # カテゴリ別に集計
        category_summary = {}
        for pp in all_pain_points:
            cat = pp['category']
            if cat not in category_summary:
                category_summary[cat] = {
                    'count': 0,
                    'items': []
                }
            category_summary[cat]['count'] += pp['count']
            category_summary[cat]['items'].append(pp['pain_point'])
        
        print(f"  ✓ {len(all_pain_points)}個の困りごとを分析")
        
        return {
            'top_pain_points': all_pain_points[:20],  # 上位20個
            'all_pain_points': all_pain_points,
            'category_summary': category_summary
        }
    
    def _categorize_pain_point(self, pain_point):
        """困りごとをカテゴリ分類"""
        if '承認' in pain_point or '手続き' in pain_point or 'プロセス' in pain_point:
            return 'プロセス・承認'
        elif 'セキュリティ' in pain_point or '基準' in pain_point:
            return 'セキュリティ・基準'
        elif '時間' in pain_point or 'スピード' in pain_point:
            return 'スピード'
        elif '人材' in pain_point or 'スキル' in pain_point or '評価' in pain_point:
            return '人材・スキル'
        elif '予算' in pain_point or 'コスト' in pain_point:
            return '予算・コスト'
        elif '連絡' in pain_point or '窓口' in pain_point or '調整' in pain_point:
            return '連携・調整'
        else:
            return 'その他'
    
    # ==========================================
    # 4. 必要な支援分析
    # ==========================================
    
    def analyze_support_needs(self):
        """
        必要な支援を分析
        
        Returns:
            dict: 必要な支援のランキング
        """
        print("\n[5/7] 必要な支援の分析中...")
        
        # セクション7 Q3: 理想の支援
        support_question = 'どんな基準や支援があれば、もっと迅速に判断・活動できますか？'
        
        support_needs = []
        
        # 該当する列を探す
        support_cols = [col for col in self.data.columns if support_question in col and col != '回答者ID']
        
        for col in support_cols:
            support_item = col.replace(support_question + '_', '')
            count = self.data[col].sum()
            
            if count > 0 and 'その他' not in support_item:
                support_needs.append({
                    'support': support_item,
                    'count': int(count),
                    'rate': float((count / len(self.data)) * 100)
                })
        
        # 頻出順にソート
        support_needs.sort(key=lambda x: x['count'], reverse=True)
        
        # セクション6 Q7: ベンダー管理で必要な支援
        vendor_support_question = 'どんな支援があれば役立ちますか？'
        vendor_support_cols = [col for col in self.data.columns if vendor_support_question in col and col != '回答者ID']
        
        vendor_support_needs = []
        for col in vendor_support_cols:
            support_item = col.replace(vendor_support_question + '_', '')
            count = self.data[col].sum()
            
            if count > 0 and 'その他' not in support_item:
                vendor_support_needs.append({
                    'support': support_item,
                    'count': int(count),
                    'rate': float((count / len(self.data)) * 100)
                })
        
        vendor_support_needs.sort(key=lambda x: x['count'], reverse=True)
        
        print(f"  ✓ {len(support_needs)}個の支援ニーズを分析")
        
        return {
            'general_support': support_needs,
            'vendor_support': vendor_support_needs,
            'combined': sorted(support_needs + vendor_support_needs, key=lambda x: x['count'], reverse=True)
        }
    
    # ==========================================
    # 5. 部門別プロファイル
    # ==========================================
    
    def create_department_profiles(self):
        """
        部門別プロファイルを作成
        
        Returns:
            dict: 各部門の特徴をまとめたプロファイル
        """
        print("\n[6/7] 部門別プロファイルの作成中...")
        
        if self.raw_data is None or '所属部門' not in self.raw_data.columns:
            print("  ⚠️ 生データがないため、部門別プロファイルをスキップします")
            return {}
        
        profiles = {}
        
        for dept in self.raw_data['所属部門'].unique():
            dept_indices = self.raw_data[self.raw_data['所属部門'] == dept].index
            dept_data = self.data.iloc[dept_indices]
            dept_raw_data = self.raw_data.iloc[dept_indices]
            
            # 基本情報
            profile = {
                'respondent_count': int(len(dept_data)),
                'average_budget': float(dept_raw_data['昨年度IT予算執行額'].mean()) if '昨年度IT予算執行額' in dept_raw_data.columns else 0
            }
            
            # 変更管理の実施状況
            change_mgmt_question = '本番システムに変更を加える時、どうしていますか？'
            change_cols = [col for col in dept_data.columns if change_mgmt_question in col]
            change_practices = []
            for col in change_cols:
                if dept_data[col].sum() > 0:
                    practice = col.replace(change_mgmt_question + '_', '')
                    rate = (dept_data[col].sum() / len(dept_data)) * 100
                    change_practices.append({
                        'practice': practice,
                        'rate': float(rate)
                    })
            
            profile['change_management'] = sorted(change_practices, key=lambda x: x['rate'], reverse=True)[:5]
            
            # 主な困りごと（上位3つ）
            dept_pain_points = []
            for col in dept_data.columns:
                if '困る' in col or '困っている' in col:
                    count = dept_data[col].sum()
                    if count > 0:
                        dept_pain_points.append({
                            'issue': col.split('_')[-1] if '_' in col else col,
                            'count': int(count)
                        })
            
            profile['top_issues'] = sorted(dept_pain_points, key=lambda x: x['count'], reverse=True)[:3]
            
            profiles[dept] = profile
        
        print(f"  ✓ {len(profiles)}部門のプロファイルを作成")
        
        return profiles
    
    # ==========================================
    # 6. 分析パイプライン
    # ==========================================
    
    def run_analysis_pipeline(self):
        """
        全分析を実行
        
        Returns:
            dict: 全分析結果
        """
        print("\n" + "=" * 80)
        print("  ITガバナンス実態調査 - 分析パイプライン")
        print("=" * 80)
        
        results = {
            'metadata': {
                'total_respondents': int(len(self.data)),
                'total_columns': int(len(self.data.columns))
            }
        }
        
        # 1. 選択率の計算
        results['selection_rates'] = self.calculate_selection_rates()
        
        # 2. 部門別分布
        results['department_breakdown'] = self.calculate_department_breakdown()
        
        # 3. セキュリティ成熟度
        results['security_maturity'] = self.calculate_security_maturity()
        
        # 4. 困りごと分析
        results['pain_points'] = self.analyze_pain_points()
        
        # 5. 必要な支援
        results['support_needs'] = self.analyze_support_needs()
        
        # 6. 部門別プロファイル
        results['department_profiles'] = self.create_department_profiles()
        
        # 7. 可視化用データの準備
        print("\n[7/7] 可視化用データの準備中...")
        results['visualization_data'] = self._prepare_visualization_data(results)
        print("  ✓ 可視化用データを準備")
        
        print("\n" + "=" * 80)
        print("  分析完了！")
        print("=" * 80)
        
        self.analysis_results = results
        return results
    
    def _prepare_visualization_data(self, results):
        """5つの可視化のためのデータを準備"""
        viz_data = {
            'A_vendor_map': self._prepare_vendor_map_data(),
            'B_decision_process': self._prepare_decision_process_data(),
            'C_security_maturity': results['security_maturity'],
            'D_pain_points': results['pain_points'],
            'E_department_profile': results['department_profiles']
        }
        return viz_data
    
    def _prepare_vendor_map_data(self):
        """可視化A: ベンダーマップ用データ"""
        # 簡易版（実際のベンダー情報は生データから取得が必要）
        return {
            'note': 'ベンダー情報は生データのQ1から抽出が必要',
            'placeholder': True
        }
    
    def _prepare_decision_process_data(self):
        """可視化B: 意思決定プロセス用データ"""
        decision_cols = [col for col in self.data.columns if '新しいツールやシステムを導入する時' in col]
        
        process_data = {}
        for col in decision_cols:
            process = col.split('_')[-1]
            count = self.data[col].sum()
            process_data[process] = {
                'count': int(count),
                'rate': float((count / len(self.data)) * 100)
            }
        
        return process_data
    
    def save_results(self, output_path=None):
        """
        分析結果を保存
        
        Args:
            output_path: 保存先パス
        """
        if output_path is None:
            output_path = self.config['paths']['analysis_results']
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        save_json(self.analysis_results, output_path)
        print(f"\n✓ 分析結果を保存しました: {output_path}")
    
    def print_summary(self):
        """分析結果のサマリーを表示"""
        if not self.analysis_results:
            print("分析結果がありません")
            return
        
        print("\n" + "=" * 80)
        print("  分析結果サマリー")
        print("=" * 80)
        
        # 基本情報
        print(f"\n【基本情報】")
        print(f"  総回答数: {self.analysis_results['metadata']['total_respondents']}件")
        
        # セキュリティ成熟度
        if 'security_maturity' in self.analysis_results:
            sm = self.analysis_results['security_maturity']['overall']
            print(f"\n【セキュリティ成熟度】")
            print(f"  全体: {sm['maturity_level']} ({sm['percentage']:.1f}%)")
        
        # 困りごとトップ5
        if 'pain_points' in self.analysis_results:
            print(f"\n【困りごとトップ5】")
            for i, pp in enumerate(self.analysis_results['pain_points']['top_pain_points'][:5], 1):
                print(f"  {i}. {pp['pain_point']}: {pp['count']}件 ({pp['rate']:.1f}%)")
        
        # 必要な支援トップ5
        if 'support_needs' in self.analysis_results:
            print(f"\n【必要な支援トップ5】")
            for i, sn in enumerate(self.analysis_results['support_needs']['combined'][:5], 1):
                print(f"  {i}. {sn['support']}: {sn['count']}件 ({sn['rate']:.1f}%)")


def main():
    """メイン関数（テスト用）"""
    from modules.util import print_section
    
    print_section("ITガバナンス実態調査 - データ分析")
    
    # 分析器を初期化
    analyser = ITGovernanceAnalyser()
    
    # データ読み込み
    analyser.load_data()
    
    # 分析実行
    results = analyser.run_analysis_pipeline()
    
    # 結果保存
    analyser.save_results()
    
    # サマリー表示
    analyser.print_summary()


if __name__ == '__main__':
    main()
