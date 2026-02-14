"""
レポート生成モジュール - ITガバナンス実態調査対応版

分析結果を可視化し、レポートを生成します。
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import warnings

# UserWarning抑制
warnings.filterwarnings('ignore', category=UserWarning)

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from matplotlib import font_manager
from modules.util import load_yaml

# 日本語フォントの設定を確実に行う
def setup_japanese_font():
    """日本語フォントを設定"""
    # 利用可能なフォントを確認
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    # 優先順位付きフォントリスト
    preferred_fonts = [
        'Hiragino Kaku Gothic ProN',  # Mac標準
        'Hiragino Sans',              # Mac (新しいバージョン)
        'Yu Gothic',                  # Windows
        'Meiryo',                     # Windows
        'IPAexGothic',                # Linux
        'IPAPGothic',                 # Linux
        'Noto Sans CJK JP',           # Linux
        'Takao Gothic',               # Linux
        'DejaVu Sans'                 # フォールバック
    ]
    
    # 利用可能なフォントを選択
    selected_font = None
    for font in preferred_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        matplotlib.rcParams['font.sans-serif'] = [selected_font]
    else:
        # デフォルトのフォールバック
        matplotlib.rcParams['font.sans-serif'] = preferred_fonts
    
    matplotlib.rcParams['axes.unicode_minus'] = False

# フォント設定を実行
setup_japanese_font()


class ITGovernanceReportGenerator:
    """ITガバナンス実態調査レポート生成クラス"""
    
    def __init__(self, 
                 analysis_results_path=None,
                 config_path='config/config.yaml'):
        """
        初期化
        
        Args:
            analysis_results_path: 分析結果JSONのパス
            config_path: 設定ファイルのパス
        """
        self.config = load_yaml(config_path)
        
        # 分析結果の読み込み
        if analysis_results_path is None:
            analysis_results_path = self.config['paths']['analysis_results']
        
        with open(analysis_results_path, 'r', encoding='utf-8') as f:
            self.analysis_results = json.load(f)
        
        # グラフスタイルの設定
        self._setup_plot_style()
        
        # 出力ディレクトリの作成
        self.graph_dir = Path('reports/graphs')
        self.graph_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_plot_style(self):
        """グラフスタイルの設定"""
        sns.set_style("whitegrid")
        
        # seabornがフォント設定を上書きするため、再設定
        setup_japanese_font()
        
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
    
    # ==========================================
    # 可視化A: 導入ツール・ベンダーマップ
    # ==========================================
    
    def create_vendor_map(self):
        """
        可視化A: 導入ツール・ベンダーマップ
        
        現状では簡易版（プレースホルダー）
        実際のベンダー情報は生データから抽出が必要
        """
        print("\n[可視化A] 導入ツール・ベンダーマップ（プレースホルダー）")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # プレースホルダーテキスト
        ax.text(0.5, 0.5, 
                '導入ツール・ベンダーマップ\n\n'
                '※実際のベンダー情報は生データから\n'
                '　個別に抽出する必要があります',
                ha='center', va='center',
                fontsize=14,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        plt.tight_layout()
        output_path = self.graph_dir / 'visualization_A_vendor_map.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # 可視化B: 意思決定プロセスの実態
    # ==========================================
    
    def create_decision_process_chart(self):
        """
        可視化B: 意思決定プロセスの実態
        
        セクション1の「新しいツール・システム導入時の決定方法」を可視化
        """
        print("\n[可視化B] 意思決定プロセスの実態")
        
        # セクション1 Q2のデータを取得
        s1_data = self.analysis_results['selection_rates'].get('section1', {})
        s1_q2_data = s1_data.get('s1_q2', {})
        
        if not s1_q2_data or 'rates' not in s1_q2_data:
            print("  ⚠️ データが見つかりません")
            return None
        
        rates = s1_q2_data['rates']
        
        # データを整形
        processes = []
        percentages = []
        
        for process, data in sorted(rates.items(), key=lambda x: x[1]['rate'], reverse=True):
            if 'その他' not in process:
                processes.append(process)
                percentages.append(data['rate'])
        
        # 横棒グラフを作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colors = sns.color_palette("RdYlGn_r", len(processes))
        bars = ax.barh(processes, percentages, color=colors)
        
        ax.set_xlabel('選択率 (%)', fontsize=12)
        ax.set_title('新しいツール・システム導入時の意思決定プロセス', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # パーセント表示
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            ax.text(pct + 2, bar.get_y() + bar.get_height()/2, 
                   f'{pct:.1f}%',
                   va='center', fontsize=9)
        
        ax.set_xlim(0, max(percentages) * 1.15)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.graph_dir / 'visualization_B_decision_process.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # 可視化C: セキュリティ成熟度マップ
    # ==========================================
    
    def create_security_maturity_map(self):
        """
        可視化C: セキュリティ成熟度マップ
        
        部門別のセキュリティ成熟度を可視化
        """
        print("\n[可視化C] セキュリティ成熟度マップ")
        
        security_data = self.analysis_results.get('security_maturity', {})
        dept_data = security_data.get('by_department', {})
        
        if not dept_data:
            print("  ⚠️ 部門別データが見つかりません")
            return None
        
        # データを整形
        departments = []
        percentages = []
        levels = []
        
        for dept, data in sorted(dept_data.items(), key=lambda x: x[1]['percentage'], reverse=True):
            departments.append(dept)
            percentages.append(data['percentage'])
            levels.append(data['maturity_level'])
        
        # 色を成熟度レベルに応じて設定
        colors = []
        for level in levels:
            if level == '高':
                colors.append('#4CAF50')  # 緑
            elif level == '中':
                colors.append('#FFC107')  # 黄
            else:
                colors.append('#F44336')  # 赤
        
        # 横棒グラフを作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(departments, percentages, color=colors)
        
        ax.set_xlabel('セキュリティ成熟度スコア (%)', fontsize=12)
        ax.set_title('部門別セキュリティ成熟度', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # スコアとレベルを表示
        for i, (bar, pct, level) in enumerate(zip(bars, percentages, levels)):
            ax.text(pct + 2, bar.get_y() + bar.get_height()/2, 
                   f'{pct:.1f}% ({level})',
                   va='center', fontsize=9)
        
        # 全体平均線を追加
        overall_pct = security_data.get('overall', {}).get('percentage', 0)
        ax.axvline(overall_pct, color='blue', linestyle='--', 
                  linewidth=2, label=f'全体平均: {overall_pct:.1f}%', alpha=0.7)
        
        ax.set_xlim(0, max(percentages) * 1.2)
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.graph_dir / 'visualization_C_security_maturity.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # 可視化D: 困りごと・ニーズ分析
    # ==========================================
    
    def create_pain_points_chart(self):
        """
        可視化D: 困りごと・ニーズ分析
        
        困りごとトップ15と必要な支援トップ10を並べて表示
        """
        print("\n[可視化D] 困りごと・ニーズ分析")
        
        pain_data = self.analysis_results.get('pain_points', {})
        support_data = self.analysis_results.get('support_needs', {})
        
        top_pains = pain_data.get('top_pain_points', [])[:15]
        top_supports = support_data.get('combined', [])[:10]
        
        # 2つのサブプロットを作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
        
        # 左: 困りごとトップ15
        if top_pains:
            pains = [p['pain_point'][:40] + '...' if len(p['pain_point']) > 40 else p['pain_point'] 
                    for p in top_pains]
            pain_rates = [p['rate'] for p in top_pains]
            
            colors1 = sns.color_palette("Reds_r", len(pains))
            bars1 = ax1.barh(pains, pain_rates, color=colors1)
            
            ax1.set_xlabel('選択率 (%)', fontsize=11)
            ax1.set_title('困りごとトップ15', fontsize=13, fontweight='bold', pad=15)
            
            for bar, rate in zip(bars1, pain_rates):
                ax1.text(rate + 1, bar.get_y() + bar.get_height()/2, 
                        f'{rate:.1f}%',
                        va='center', fontsize=8)
            
            ax1.set_xlim(0, max(pain_rates) * 1.15)
            ax1.grid(axis='x', alpha=0.3)
            ax1.invert_yaxis()
        
        # 右: 必要な支援トップ10
        if top_supports:
            supports = [s['support'][:40] + '...' if len(s['support']) > 40 else s['support'] 
                       for s in top_supports]
            support_rates = [s['rate'] for s in top_supports]
            
            colors2 = sns.color_palette("Greens_r", len(supports))
            bars2 = ax2.barh(supports, support_rates, color=colors2)
            
            ax2.set_xlabel('選択率 (%)', fontsize=11)
            ax2.set_title('必要な支援トップ10', fontsize=13, fontweight='bold', pad=15)
            
            for bar, rate in zip(bars2, support_rates):
                ax2.text(rate + 1, bar.get_y() + bar.get_height()/2, 
                        f'{rate:.1f}%',
                        va='center', fontsize=8)
            
            ax2.set_xlim(0, max(support_rates) * 1.15)
            ax2.grid(axis='x', alpha=0.3)
            ax2.invert_yaxis()
        
        plt.suptitle('ITガバナンス実態調査: 困りごと・ニーズ分析', 
                    fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        output_path = self.graph_dir / 'visualization_D_pain_points_needs.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # 可視化E: 部門別プロファイル
    # ==========================================
    
    def create_department_profile_chart(self):
        """
        可視化E: 部門別プロファイル
        
        各部門の特徴を一覧表示
        """
        print("\n[可視化E] 部門別プロファイル")
        
        profiles = self.analysis_results.get('department_profiles', {})
        
        if not profiles:
            print("  ⚠️ 部門別プロファイルが見つかりません")
            return None
        
        # 部門数
        n_depts = len(profiles)
        
        # サブプロット作成
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # 上: 回答者数とIT予算
        departments = list(profiles.keys())
        respondent_counts = [profiles[d]['respondent_count'] for d in departments]
        avg_budgets = [profiles[d]['average_budget'] / 10000 for d in departments]  # 万円→億円
        
        x = np.arange(len(departments))
        width = 0.35
        
        ax1 = axes[0]
        bars1 = ax1.bar(x - width/2, respondent_counts, width, label='回答者数', color='#2196F3')
        
        ax1.set_ylabel('回答者数', fontsize=11)
        ax1.set_title('部門別プロファイル: 回答者数とIT予算', 
                     fontsize=13, fontweight='bold', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(departments, rotation=45, ha='right')
        ax1.legend(loc='upper left')
        ax1.grid(axis='y', alpha=0.3)
        
        # 値表示
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
        
        # 予算を右軸に追加
        ax1_right = ax1.twinx()
        bars2 = ax1_right.bar(x + width/2, avg_budgets, width, label='平均IT予算', color='#4CAF50')
        ax1_right.set_ylabel('平均IT予算 (億円)', fontsize=11)
        ax1_right.legend(loc='upper right')
        
        for bar in bars2:
            height = bar.get_height()
            ax1_right.text(bar.get_x() + bar.get_width()/2, height,
                          f'{height:.2f}',
                          ha='center', va='bottom', fontsize=8)
        
        # 下: 主な困りごと
        ax2 = axes[1]
        ax2.axis('off')
        
        # 表形式でプロファイル表示
        table_data = []
        headers = ['部門', '回答者数', '平均予算\n(万円)', '主な困りごと']
        
        for dept in departments:
            profile = profiles[dept]
            top_issues = profile.get('top_issues', [])[:2]  # 上位2つ
            issues_text = '\n'.join([f"• {issue['issue'][:20]}" for issue in top_issues])
            
            table_data.append([
                dept,
                f"{profile['respondent_count']}名",
                f"{profile['average_budget']:.0f}",
                issues_text if issues_text else '（なし）'
            ])
        
        table = ax2.table(cellText=table_data, colLabels=headers,
                         cellLoc='left', loc='center',
                         colWidths=[0.15, 0.12, 0.15, 0.58])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # ヘッダーのスタイル
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#E3F2FD')
            table[(0, i)].set_text_props(weight='bold')
        
        plt.suptitle('部門別プロファイル', fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        output_path = self.graph_dir / 'visualization_E_department_profile.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # 追加の可視化
    # ==========================================
    
    def create_category_summary_chart(self):
        """困りごとのカテゴリ別サマリー"""
        print("\n[追加] 困りごとカテゴリ別サマリー")
        
        pain_data = self.analysis_results.get('pain_points', {})
        category_summary = pain_data.get('category_summary', {})
        
        if not category_summary:
            print("  ⚠️ カテゴリサマリーが見つかりません")
            return None
        
        categories = list(category_summary.keys())
        counts = [category_summary[c]['count'] for c in categories]
        
        # 円グラフを作成
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = sns.color_palette("Set3", len(categories))
        wedges, texts, autotexts = ax.pie(counts, labels=categories, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        
        # パーセント表示を見やすく
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('困りごとカテゴリ別分布', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        output_path = self.graph_dir / 'additional_category_summary.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_path}")
        return str(output_path)
    
    # ==========================================
    # レポート生成パイプライン
    # ==========================================
    
    def generate_all_visualizations(self):
        """全ての可視化を生成"""
        print("\n" + "=" * 80)
        print("  可視化生成パイプライン")
        print("=" * 80)
        
        generated_files = {}
        
        # 可視化A: ベンダーマップ
        generated_files['A_vendor_map'] = self.create_vendor_map()
        
        # 可視化B: 意思決定プロセス
        generated_files['B_decision_process'] = self.create_decision_process_chart()
        
        # 可視化C: セキュリティ成熟度
        generated_files['C_security_maturity'] = self.create_security_maturity_map()
        
        # 可視化D: 困りごと・ニーズ
        generated_files['D_pain_points'] = self.create_pain_points_chart()
        
        # 可視化E: 部門別プロファイル
        generated_files['E_department_profile'] = self.create_department_profile_chart()
        
        # 追加の可視化
        generated_files['category_summary'] = self.create_category_summary_chart()
        
        print("\n" + "=" * 80)
        print("  可視化完了！")
        print("=" * 80)
        
        return generated_files
    
    def generate_detailed_report(self, output_path='reports/report.md'):
        """
        分析レポートを生成
        
        Args:
            output_path: 出力先パス
        """
        print("\n" + "=" * 80)
        print("  分析レポート生成")
        print("=" * 80)
        
        # レポート本文を作成
        report = self._build_detailed_report_content()
        
        # ファイルに保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ 分析レポートを保存: {output_path}")
        return str(output_path)
    
    def _build_detailed_report_content(self):
        """詳細レポートの内容を構築"""
        now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        md = f"""# ITガバナンス実態調査 分析レポート

**生成日時**: {now}

---

## 目次

1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)
2. [セキュリティ成熟度分析](#2-セキュリティ成熟度分析)
3. [意思決定プロセス分析](#3-意思決定プロセス分析)
4. [困りごと分析](#4-困りごと分析)
5. [必要な支援分析](#5-必要な支援分析)
6. [部門別プロファイル](#6-部門別プロファイル)
7. [グラフ一覧](#7-グラフ一覧)

---

## 1. エグゼクティブサマリー

### 調査概要

- **総回答数**: {self.analysis_results['metadata']['total_respondents']}件
- **調査項目**: 全7セクション・37問

### セキュリティ成熟度スコア

"""
        
        # セキュリティ成熟度
        sm = self.analysis_results.get('security_maturity', {}).get('overall', {})
        md += f"- **全体スコア**: {sm.get('percentage', 0):.1f}% ({sm.get('maturity_level', '不明')})\n\n"
        
        # グラフ
        md += "![セキュリティ成熟度](graphs/visualization_C_security_maturity.png)\n\n"
        
        # 困りごとトップ10
        md += "### 困りごとトップ10\n\n"
        md += "| 順位 | 困りごと | 選択率 | 件数 |\n"
        md += "|------|---------|--------|------|\n"
        
        top_pains = self.analysis_results.get('pain_points', {}).get('top_pain_points', [])[:10]
        for i, pp in enumerate(top_pains, 1):
            md += f"| {i} | {pp['pain_point']} | {pp['rate']:.1f}% | {pp['count']}件 |\n"
        
        md += "\n### 必要な支援トップ10\n\n"
        md += "| 順位 | 支援内容 | 選択率 | 件数 |\n"
        md += "|------|---------|--------|------|\n"
        
        top_supports = self.analysis_results.get('support_needs', {}).get('combined', [])[:10]
        for i, sn in enumerate(top_supports, 1):
            md += f"| {i} | {sn['support']} | {sn['rate']:.1f}% | {sn['count']}件 |\n"
        
        md += "\n![困りごと・ニーズ](graphs/visualization_D_pain_points_needs.png)\n\n"
        md += "---\n\n"
        
        # セキュリティ成熟度分析
        md += "## 2. セキュリティ成熟度分析\n\n"
        md += "### 全体スコア\n\n"
        md += f"- **スコア**: {sm.get('percentage', 0):.1f}%\n"
        md += f"- **成熟度レベル**: {sm.get('maturity_level', '不明')}\n"
        md += f"- **最大スコア**: {sm.get('max_score', 0):.0f}点中 {sm.get('total_score', 0):.0f}点\n\n"
        
        md += "### 項目別スコア\n\n"
        md += "| 項目 | スコア | 達成率 |\n"
        md += "|------|--------|--------|\n"
        
        item_scores = sm.get('item_scores', {})
        for item_name, scores in item_scores.items():
            md += f"| {item_name} | {scores['score']:.1f}点 | {scores['percentage']:.1f}% |\n"
        
        md += "\n### 部門別成熟度\n\n"
        md += "| 部門 | スコア | レベル | 回答者数 |\n"
        md += "|------|--------|--------|----------|\n"
        
        dept_maturity = self.analysis_results.get('security_maturity', {}).get('by_department', {})
        for dept, data in sorted(dept_maturity.items(), key=lambda x: x[1]['percentage'], reverse=True):
            md += f"| {dept} | {data['percentage']:.1f}% | {data['maturity_level']} | {data['respondent_count']}名 |\n"
        
        md += "\n![部門別セキュリティ成熟度](graphs/visualization_C_security_maturity.png)\n\n"
        md += "---\n\n"
        
        # 意思決定プロセス分析
        md += "## 3. 意思決定プロセス分析\n\n"
        
        s1_data = self.analysis_results['selection_rates'].get('section1', {})
        s1_q2_data = s1_data.get('s1_q2', {})
        
        if s1_q2_data and 'rates' in s1_q2_data:
            md += "### 導入時の意思決定方法\n\n"
            md += "| 方法 | 選択率 | 件数 |\n"
            md += "|------|--------|------|\n"
            
            for process, data in sorted(s1_q2_data['rates'].items(), key=lambda x: x[1]['rate'], reverse=True):
                if 'その他' not in process:
                    md += f"| {process} | {data['rate']:.1f}% | {data['count']}件 |\n"
        
        md += "\n![意思決定プロセス](graphs/visualization_B_decision_process.png)\n\n"
        md += "---\n\n"
        
        # 困りごと分析
        md += "## 4. 困りごと分析\n\n"
        md += "### カテゴリ別サマリー\n\n"
        md += "| カテゴリ | 件数 | 構成比 |\n"
        md += "|---------|------|--------|\n"
        
        category_summary = self.analysis_results.get('pain_points', {}).get('category_summary', {})
        total_count = sum(data['count'] for data in category_summary.values())
        
        for cat, data in sorted(category_summary.items(), key=lambda x: x[1]['count'], reverse=True):
            percentage = (data['count'] / total_count * 100) if total_count > 0 else 0
            md += f"| {cat} | {data['count']}件 | {percentage:.1f}% |\n"
        
        md += "\n![カテゴリ別分布](graphs/additional_category_summary.png)\n\n"
        
        md += "### 詳細リスト（全困りごと）\n\n"
        md += "| 順位 | カテゴリ | 困りごと | 選択率 | 件数 |\n"
        md += "|------|---------|---------|--------|------|\n"
        
        all_pains = self.analysis_results.get('pain_points', {}).get('all_pain_points', [])
        for i, pp in enumerate(all_pains[:30], 1):  # 上位30個
            md += f"| {i} | {pp['category']} | {pp['pain_point']} | {pp['rate']:.1f}% | {pp['count']}件 |\n"
        
        md += "\n---\n\n"
        
        # 必要な支援分析
        md += "## 5. 必要な支援分析\n\n"
        md += "### 全体的な支援ニーズ\n\n"
        md += "| 順位 | 支援内容 | 選択率 | 件数 |\n"
        md += "|------|---------|--------|------|\n"
        
        general_support = self.analysis_results.get('support_needs', {}).get('general_support', [])
        for i, sn in enumerate(general_support, 1):
            md += f"| {i} | {sn['support']} | {sn['rate']:.1f}% | {sn['count']}件 |\n"
        
        md += "\n### ベンダー管理での支援ニーズ\n\n"
        md += "| 順位 | 支援内容 | 選択率 | 件数 |\n"
        md += "|------|---------|--------|------|\n"
        
        vendor_support = self.analysis_results.get('support_needs', {}).get('vendor_support', [])
        for i, sn in enumerate(vendor_support, 1):
            md += f"| {i} | {sn['support']} | {sn['rate']:.1f}% | {sn['count']}件 |\n"
        
        md += "\n---\n\n"
        
        # 部門別プロファイル
        md += "## 6. 部門別プロファイル\n\n"
        
        profiles = self.analysis_results.get('department_profiles', {})
        
        for dept in sorted(profiles.keys()):
            profile = profiles[dept]
            md += f"### {dept}\n\n"
            md += f"- **回答者数**: {profile['respondent_count']}名\n"
            md += f"- **平均IT予算**: {profile['average_budget']:.0f}万円\n\n"
            
            if profile.get('change_management'):
                md += "**変更管理の実施状況（上位5つ）**:\n\n"
                for i, practice in enumerate(profile['change_management'][:5], 1):
                    md += f"{i}. {practice['practice']} ({practice['rate']:.1f}%)\n"
                md += "\n"
            
            if profile.get('top_issues'):
                md += "**主な困りごと**:\n\n"
                for issue in profile['top_issues']:
                    md += f"- {issue['issue']}\n"
                md += "\n"
        
        md += "![部門別プロファイル](graphs/visualization_E_department_profile.png)\n\n"
        md += "---\n\n"
        
        # グラフ一覧
        md += "## 7. グラフ一覧\n\n"
        md += "### 5つの主要可視化\n\n"
        md += "1. [導入ツール・ベンダーマップ](graphs/visualization_A_vendor_map.png)\n"
        md += "2. [意思決定プロセスの実態](graphs/visualization_B_decision_process.png)\n"
        md += "3. [セキュリティ成熟度マップ](graphs/visualization_C_security_maturity.png)\n"
        md += "4. [困りごと・ニーズ分析](graphs/visualization_D_pain_points_needs.png)\n"
        md += "5. [部門別プロファイル](graphs/visualization_E_department_profile.png)\n\n"
        
        md += "### 追加の可視化\n\n"
        md += "- [困りごとカテゴリ別サマリー](graphs/additional_category_summary.png)\n\n"
        
        md += "---\n\n"
        md += "**レポート生成完了**\n"
        
        return md
    
    def generate_full_report(self):
        """
        完全なレポートを生成
        
        Returns:
            生成されたファイルのパス一覧
        """
        print("\n" + "=" * 80)
        print("  ITガバナンス実態調査 - 完全レポート生成")
        print("=" * 80)
        
        results = {}
        
        # 1. 全ての可視化を生成
        results['visualizations'] = self.generate_all_visualizations()
        
        # 2. 詳細レポートを生成（統合版）
        results['report'] = self.generate_detailed_report()
        
        print("\n" + "=" * 80)
        print("  レポート生成完了！")
        print("=" * 80)
        print("\n生成されたファイル:")
        print(f"  ✓ レポート: {results['report']}")
        print(f"  ✓ 可視化: {len([v for v in results['visualizations'].values() if v])}個")
        
        return results


def main():
    """メイン関数（テスト用）"""
    from modules.util import print_section
    
    print_section("ITガバナンス実態調査 - レポート生成")
    
    # レポート生成器を初期化
    generator = ITGovernanceReportGenerator()
    
    # 完全レポートを生成
    results = generator.generate_full_report()
    
    print("\n✓ レポート生成完了")


if __name__ == '__main__':
    main()
