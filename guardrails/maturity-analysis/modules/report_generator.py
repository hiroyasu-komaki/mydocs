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
from matplotlib.colors import BoundaryNorm, ListedColormap
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

# 地域別の色（日本=赤、北米=濃い青、EMEA=薄い青）
REGION_COLORS = {
    '日本': '#E53935',   # 赤
    '北米': '#1565C0',   # 濃い青
    'EMEA': '#64B5F6',   # 薄い青
}


class ITGovernanceReportGenerator:
    """ITガバナンス実態調査レポート生成クラス"""
    
    def __init__(self, 
                analysis_results_path=None,
                config_path='config/config.yaml'):
        """初期化"""
        self.config = load_yaml(config_path)
        
        # 分析結果の読み込み
        if analysis_results_path is None:
            analysis_results_path = self.config['paths']['analysis_results']
        
        with open(analysis_results_path, 'r', encoding='utf-8') as f:
            self.analysis_results = json.load(f)
        
        # ========== 追加部分 ==========
        # 生データと前処理済みデータの読み込み（ヒートマップ用）
        try:
            raw_data_path = self.config['paths']['raw_data']
            print(f"生データ読み込み試行: {raw_data_path}")
            self.raw_data = pd.read_csv(raw_data_path)
            print(f"  ✓ 生データ読み込み成功: {len(self.raw_data)}行")
        except Exception as e:
            print(f"  ⚠️ 生データの読み込みに失敗: {e}")
            self.raw_data = None
        
        try:
            preprocessed_data_path = self.config['paths']['preprocessed_data']
            print(f"前処理済みデータ読み込み試行: {preprocessed_data_path}")
            self.data = pd.read_csv(preprocessed_data_path)
            print(f"  ✓ 前処理済みデータ読み込み成功: {len(self.data)}行")
        except Exception as e:
            print(f"  ⚠️ 前処理済みデータの読み込みに失敗: {e}")
            self.data = None
        # ========== 追加部分終わり ==========
        
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
        
        地域別・部門別それぞれで作成
        """
        print("\n[可視化B] 意思決定プロセスの実態（地域別・部門別）")
        
        breakdown = self.analysis_results.get('decision_process_breakdown', {})
        by_region = breakdown.get('by_region', {})
        by_department = breakdown.get('by_department', {})
        
        output_paths = []
        
        # 地域別
        if by_region:
            fig = self._create_decision_process_bar_chart(
                by_region,
                '意思決定プロセス（地域別）',
                '新しいツール・システム導入時の意思決定方法'
            )
            path = self.graph_dir / 'visualization_B_decision_process_by_region.png'
            fig.savefig(path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            output_paths.append(str(path))
            print(f"  ✓ 保存: {path}")
        
        # 部門別
        if by_department:
            fig = self._create_decision_process_bar_chart(
                by_department,
                '意思決定プロセス（部門別）',
                '新しいツール・システム導入時の意思決定方法'
            )
            path = self.graph_dir / 'visualization_B_decision_process_by_department.png'
            fig.savefig(path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            output_paths.append(str(path))
            print(f"  ✓ 保存: {path}")
        
        # フォールバック: 従来の全体データ
        if not output_paths:
            s1_data = self.analysis_results.get('selection_rates', {}).get('section1', {})
            s1_q2_data = s1_data.get('s1_q2', {})
            if s1_q2_data and 'rates' in s1_q2_data:
                single_data = {'全体': {'rates': s1_q2_data['rates'], 'respondent_count': 100}}
                fig = self._create_decision_process_bar_chart(
                    single_data, '意思決定プロセス', '新しいツール・システム導入時の意思決定方法'
                )
                path = self.graph_dir / 'visualization_B_decision_process.png'
                fig.savefig(path, dpi=150, bbox_inches='tight')
                plt.close(fig)
                output_paths.append(str(path))
        
        return output_paths[0] if output_paths else None
    
    def _create_decision_process_bar_chart(self, breakdown_data, main_title, sub_title):
        """意思決定プロセスの横棒グラフ（複数グループ対応）"""
        all_processes = set()
        for group_data in breakdown_data.values():
            for p in group_data.get('rates', {}).keys():
                if 'その他' not in p:
                    all_processes.add(p)
        processes = sorted(all_processes, key=lambda p: sum(
            g.get('rates', {}).get(p, {}).get('rate', 0) for g in breakdown_data.values()
        ), reverse=True)
        
        if not processes:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, 'データがありません', ha='center', va='center')
            return fig
        
        groups = list(breakdown_data.keys())
        n_processes = len(processes)
        bar_height = 0.8 / max(1, len(groups))
        y_base = np.arange(n_processes) * 1.2
        
        fig, ax = plt.subplots(figsize=(12, max(8, n_processes * 0.9)))
        # 地域の場合は統一色（日本=赤、北米=濃い青、EMEA=薄い青）、それ以外はhusl
        if all(g in REGION_COLORS for g in groups):
            colors = [REGION_COLORS[g] for g in groups]
        else:
            colors = sns.color_palette("husl", len(groups))
        
        for i, group in enumerate(groups):
            rates = breakdown_data[group].get('rates', {})
            vals = [rates.get(p, {}).get('rate', 0) for p in processes]
            y_pos = y_base + i * bar_height
            bars = ax.barh(y_pos, vals, bar_height * 0.9, label=group, color=colors[i])
            for bar, v in zip(bars, vals):
                if v > 0:
                    ax.text(v + 2, bar.get_y() + bar.get_height()/2, f'{v:.1f}%',
                           va='center', fontsize=8)
        
        ax.set_yticks(y_base + bar_height * (len(groups) - 1) / 2)
        ax.set_yticklabels(processes, fontsize=10)
        ax.set_xlabel('選択率 (%)', fontsize=12)
        ax.set_title(f'{main_title}\n{sub_title}', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=9)
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)
        return fig
    
    # ==========================================
    # 可視化C: セキュリティ成熟度マップ
    # ==========================================
    
    def create_security_maturity_map(self):
        """
        可視化C: セキュリティ成熟度マップ
        
        地域別・部門別それぞれで作成
        """
        print("\n[可視化C] セキュリティ成熟度マップ（地域別・部門別）")
        
        security_data = self.analysis_results.get('security_maturity', {})
        region_data = security_data.get('by_region', {})
        dept_data = security_data.get('by_department', {})
        
        output_paths = []
        
        # 地域別
        if region_data:
            path = self._save_security_maturity_chart(
                region_data, security_data,
                'visualization_C_security_maturity_by_region.png',
                'セキュリティ成熟度（地域別）'
            )
            if path:
                output_paths.append(path)
                print(f"  ✓ 保存: {path}")
        
        # 部門別
        if dept_data:
            path = self._save_security_maturity_chart(
                dept_data, security_data,
                'visualization_C_security_maturity_by_department.png',
                'セキュリティ成熟度（部門別）'
            )
            if path:
                output_paths.append(path)
                print(f"  ✓ 保存: {path}")
        
        return output_paths[0] if output_paths else None
    
    def _save_security_maturity_chart(self, group_data, security_data, filename, title):
        """セキュリティ成熟度の横棒グラフを保存"""
        groups = []
        percentages = []
        levels = []
        
        for name, data in sorted(group_data.items(), key=lambda x: x[1]['percentage'], reverse=True):
            groups.append(name)
            percentages.append(data['percentage'])
            levels.append(data['maturity_level'])
        
        # 地域別の場合は統一色（日本=赤、北米=濃い青、EMEA=薄い青）、部門別は成熟度で色分け
        if all(g in REGION_COLORS for g in groups):
            colors = [REGION_COLORS[g] for g in groups]
        else:
            colors = []
            for level in levels:
                if level == '高':
                    colors.append('#4CAF50')
                elif level == '中':
                    colors.append('#FFC107')
                else:
                    colors.append('#F44336')
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(groups) * 1.2)))
        bars = ax.barh(groups, percentages, color=colors)
        
        for bar, pct, level in zip(bars, percentages, levels):
            ax.text(pct + 2, bar.get_y() + bar.get_height()/2, 
                   f'{pct:.1f}% ({level})', va='center', fontsize=9)
        
        overall_pct = security_data.get('overall', {}).get('percentage', 0)
        ax.axvline(overall_pct, color='blue', linestyle='--', 
                  linewidth=2, label=f'全体平均: {overall_pct:.1f}%', alpha=0.7)
        
        ax.set_xlabel('セキュリティ成熟度スコア (%)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(percentages) * 1.2 if percentages else 20)
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = self.graph_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return str(output_path)
    
    # ==========================================
    # 可視化D: 困りごと・ニーズ分析
    # ==========================================
    
    def create_pain_points_chart(self):
        """
        可視化D: 困りごと・ニーズ分析
        
        TOP10形式で地域間比較（困りごと、必要な支援を別々に）
        """
        print("\n[可視化D] 困りごと・ニーズ分析（TOP10・地域比較）")
        
        pain_data = self.analysis_results.get('pain_points', {})
        support_data = self.analysis_results.get('support_needs', {})
        
        pain_by_region = pain_data.get('by_region', {})
        support_by_region = support_data.get('by_region', {})
        
        if not pain_by_region and not support_by_region:
            print("  ⚠️ 地域別データが見つかりません")
            return None
        
        output_paths = {}
        
        # ========================================
        # 1. 困りごとの地域比較グラフ
        # ========================================
        if pain_by_region:
            fig = self._create_regional_comparison_chart(
                pain_by_region,
                '困りごとトップ10（地域比較）',
                'top_pain_points',
                'pain_point'
            )
            
            output_path_pain = self.graph_dir / 'visualization_D1_pain_points_regional_comparison.png'
            fig.savefig(output_path_pain, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  ✓ 保存: {output_path_pain}")
            output_paths['pain_points'] = str(output_path_pain)
        
        # ========================================
        # 2. 必要な支援の地域比較グラフ
        # ========================================
        if support_by_region:
            fig = self._create_regional_comparison_chart(
                support_by_region,
                '必要な支援トップ10（地域比較）',
                'top_support_needs',
                'support'
            )
            
            output_path_support = self.graph_dir / 'visualization_D2_support_needs_regional_comparison.png'
            fig.savefig(output_path_support, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"  ✓ 保存: {output_path_support}")
            output_paths['support_needs'] = str(output_path_support)
        
        return output_paths
    
    def _create_regional_comparison_chart(self, region_data, title, data_key, item_key):
        """
        地域比較グラフを作成（困りごと or 必要な支援）
        
        Args:
            region_data: 地域別データ
            title: グラフタイトル
            data_key: データキー ('top_pain_points' or 'top_support_needs')
            item_key: 項目キー ('pain_point' or 'support')
        
        Returns:
            matplotlib figure
        """
        regions = ['日本', '北米', 'EMEA']
        
        # 各地域のトップ10を取得
        region_items = {}
        for region in regions:
            if region in region_data:
                items = region_data[region].get(data_key, [])[:10]
                region_items[region] = items
        
        # 全地域の項目を統合してユニークな項目リストを作成（出現頻度順）
        all_items_count = {}
        all_items_first = {}  # 各項目名が最初に出現したデータを保持
        
        for region, items in region_items.items():
            for item in items:
                item_text = item[item_key]
                if item_text not in all_items_count:
                    all_items_count[item_text] = 0
                    all_items_first[item_text] = item  # 最初の出現を保存
                all_items_count[item_text] += item['count']
        
        # 出現頻度順にソート（上位15項目）
        sorted_items = sorted(all_items_count.items(), key=lambda x: x[1], reverse=True)[:15]
        unique_items = [item[0] for item in sorted_items]
        
        # 各地域・各項目の選択率を格納
        region_rates = {region: [] for region in regions}
        
        for item_text in unique_items:
            for region in regions:
                # この地域でこの項目の選択率を探す（最初に見つかったもののみ使用）
                rate = 0
                if region in region_items:
                    for item in region_items[region]:
                        if item[item_key] == item_text:
                            rate = item['rate']
                            break  # 最初に見つかったものを使用
                region_rates[region].append(rate)
        
        # グラフを作成（横並びの棒グラフ）
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # 項目数とバーの設定
        n_items = len(unique_items)
        bar_height = 0.25
        y_pos = np.arange(n_items)
        
        # 色設定（日本=赤、北米=濃い青、EMEA=薄い青）
        colors = REGION_COLORS
        
        # 各地域のバーを描画
        for idx, region in enumerate(regions):
            if region in region_items:
                offset = (idx - 1) * bar_height
                rates = region_rates[region]
                
                bars = ax.barh(y_pos + offset, rates, bar_height, 
                              label=f'{region} ({region_data[region]["respondent_count"]}名)',
                              color=colors.get(region, '#95A5A6'),
                              alpha=0.8)
                
                # 値ラベルを追加（5%以上の場合）
                for bar, rate in zip(bars, rates):
                    if rate >= 5.0:
                        width = bar.get_width()
                        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                               f'{rate:.0f}%',
                               va='center', fontsize=8, color=colors.get(region, '#95A5A6'))
        
        # 項目ラベル（長い場合は省略）
        item_labels = []
        for item in unique_items:
            if len(item) > 35:
                item_labels.append(item[:32] + '...')
            else:
                item_labels.append(item)
        
        # 軸の設定
        ax.set_yticks(y_pos)
        ax.set_yticklabels(item_labels, fontsize=10)
        ax.set_xlabel('選択率 (%)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
        
        # X軸の範囲を設定
        max_rate = max([max(rates) for rates in region_rates.values()] + [0])
        ax.set_xlim(0, max_rate * 1.2)
        
        plt.tight_layout()
        
        return fig
    
    def _plot_stacked_bars(self, ax, section_data, respondent_counts, section_colors, regions, title):
        """
        積み上げ横棒グラフをプロット
        
        Args:
            ax: matplotlibのaxesオブジェクト
            section_data: 地域別・セクション別のデータ {'日本': {'セクション4': {'percentage': 30.5, ...}, ...}, ...}
            respondent_counts: 地域別の回答者数 {'日本': 36, ...}
            section_colors: セクション別の色マッピング
            regions: 地域のリスト
            title: グラフタイトル
        """
        # 全セクションのリストを取得（出現順）
        all_sections = []
        for region_data in section_data.values():
            for section in region_data.keys():
                if section not in all_sections:
                    all_sections.append(section)
        
        # 地域数
        n_regions = len([r for r in regions if r in section_data])
        
        # Y軸の位置
        y_pos = np.arange(n_regions)
        
        # 各地域の積み上げバーを作成
        region_labels = []
        left_positions = [0] * n_regions
        
        for idx, region in enumerate(regions):
            if region not in section_data:
                continue
            
            respondent_count = respondent_counts.get(region, 0)
            region_labels.append(f'{region}\n({respondent_count}名)')
        
        # セクションごとにバーを積み上げ
        for section in all_sections:
            widths = []
            colors = []
            
            for region in regions:
                if region not in section_data:
                    continue
                
                region_sections = section_data[region]
                
                if section in region_sections:
                    percentage = region_sections[section]['percentage']
                    widths.append(percentage)
                else:
                    widths.append(0)
                
                colors.append(section_colors.get(section, '#95A5A6'))
            
            # バーをプロット
            bars = ax.barh(y_pos, widths, left=left_positions, 
                          color=colors, edgecolor='white', linewidth=1)
            
            # パーセンテージラベルを追加（5%以上の場合のみ）
            for idx, (bar, width, left) in enumerate(zip(bars, widths, left_positions)):
                if width >= 5.0:  # 5%以上の場合のみ表示
                    label_x = left + width / 2
                    label_y = bar.get_y() + bar.get_height() / 2
                    ax.text(label_x, label_y, f'{width:.1f}%',
                           ha='center', va='center', fontsize=9, 
                           color='white', fontweight='bold')
            
            # 左位置を更新
            left_positions = [left + width for left, width in zip(left_positions, widths)]
        
        # 軸の設定
        ax.set_yticks(y_pos)
        ax.set_yticklabels(region_labels, fontsize=11)
        ax.set_xlabel('割合 (%)', fontsize=11)
        ax.set_xlim(0, 100)
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
    
    # ==========================================
    # 可視化E: 部門別プロファイル
    # ==========================================
    
    def create_department_profile_chart(self):
        """
        可視化E: 部門別の強み分析（困りごとの少なさ）
        
        縦軸: 部門名
        横軸: セクション
        値: 困りごとの逆数（困りごとが少ない = 強み・ベストプラクティスを持つ可能性）
        """
        print("\n[可視化E] 部門別の強み分析（ヒートマップ）")
        
        # データの存在確認（詳細ログ付き）
        print(f"  - raw_data: {'あり' if self.raw_data is not None else 'なし'}")
        print(f"  - data: {'あり' if self.data is not None else 'なし'}")
        
        if self.raw_data is None:
            print("  ⚠️ 生データが見つかりません")
            return None
        
        if self.data is None:
            print("  ⚠️ 前処理済みデータが見つかりません")
            return None
        
        # 所属部門列の存在確認
        if '所属部門' not in self.raw_data.columns:
            print(f"  ⚠️ '所属部門'列が見つかりません")
            print(f"  利用可能な列: {list(self.raw_data.columns[:10])}")
            return None
        
        pain_data = self.analysis_results.get('pain_points', {})
        all_pain_points = pain_data.get('all_pain_points', [])
        
        print(f"  - 困りごとデータ: {len(all_pain_points)}件")
        
        if not all_pain_points:
            print("  ⚠️ 困りごとデータが見つかりません")
            return None
        
        # 部門リストを取得
        departments = sorted(self.raw_data['所属部門'].unique())
        print(f"  - 部門数: {len(departments)}")
        
        # セクションリスト
        sections = [
            'セクション1 tech adoption',
            'セクション2 security',
            'セクション3 data handling',
            'セクション4 change trouble',
            'セクション5 budget',
            'セクション6 vendor',
            'セクション7 others'
        ]
        # S1〜S7 に英語ラベルを付与（分かりやすくするため）
        section_labels = [
            'S1\nTech adoption',
            'S2\nSecurity',
            'S3\nData handling',
            'S4\nChange/Trouble',
            'S5\nBudget',
            'S6\nVendor',
            'S7\nOthers'
        ]
        
        # 部門×セクションの困りごとスコアを計算
        dept_section_scores = {}
        
        for dept in departments:
            dept_indices = self.raw_data[self.raw_data['所属部門'] == dept].index
            dept_data = self.data.loc[dept_indices]
            n_dept = len(dept_data)
            
            if n_dept == 0:
                continue
            
            dept_scores = []
            
            for section in sections:
                # このセクションの困りごとを抽出
                section_pain_points = [p for p in all_pain_points if p.get('section') == section]
                
                if not section_pain_points:
                    # データがない場合は中立値
                    dept_scores.append(50.0)
                    continue
                
                # この部門でのセクションの困りごと選択率を計算
                total_rate = 0
                count = 0
                
                for pain in section_pain_points:
                    pain_point = pain['pain_point']
                    # 困りごとの列名を構築（質問文は不明なので、列名から検索）
                    matching_cols = [col for col in dept_data.columns if pain_point in col]
                    
                    for col in matching_cols:
                        if dept_data[col].sum() > 0:
                            rate = (dept_data[col].sum() / n_dept) * 100
                            total_rate += rate
                            count += 1
                
                # 平均困りごと選択率
                avg_pain_rate = total_rate / count if count > 0 else 0
                
                # 逆数に変換（困りごとが少ない = 高スコア）
                strength_score = 100 - avg_pain_rate
                dept_scores.append(strength_score)
            
            dept_section_scores[dept] = dept_scores
        
        # ヒートマップ用の行列を作成
        heatmap_data = []
        dept_labels = []
        
        for dept in departments:
            if dept in dept_section_scores:
                heatmap_data.append(dept_section_scores[dept])
                dept_labels.append(dept)
        
        heatmap_matrix = np.array(heatmap_data)
        
        # RAGカラー: 閾値 20以下=赤(困っている), 20超〜50=黄(中間), 50超=緑(困っていない)
        RAG_THRESHOLD_TROUBLED = 20   # 以下なら困っている
        RAG_THRESHOLD_OK = 50         # 超えていれば困っていない
        rag_colors = ['#C62828', '#F9A825', '#2E7D32']  # Red, Amber, Green
        rag_cmap = ListedColormap(rag_colors)
        rag_bounds = [0, RAG_THRESHOLD_TROUBLED, RAG_THRESHOLD_OK, 100]
        rag_norm = BoundaryNorm(rag_bounds, rag_cmap.N)
        
        # ヒートマップを描画
        fig, ax = plt.subplots(figsize=(12, 8))
        
        im = ax.imshow(heatmap_matrix, cmap=rag_cmap, norm=rag_norm, aspect='auto')
        
        # 軸の設定
        ax.set_xticks(np.arange(len(section_labels)))
        ax.set_yticks(np.arange(len(dept_labels)))
        ax.set_xticklabels(section_labels, fontsize=11)
        ax.set_yticklabels(dept_labels, fontsize=11)
        
        # X軸ラベルを上に配置
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        
        # グリッド線
        ax.set_xticks(np.arange(len(section_labels) + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(len(dept_labels) + 1) - 0.5, minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
        
        # 各セルに値を表示
        for i in range(len(dept_labels)):
            for j in range(len(section_labels)):
                value = heatmap_matrix[i, j]
                # 値に応じて文字色を変更（赤セルは白文字、黄・緑は黒文字）
                text_color = 'white' if value <= RAG_THRESHOLD_TROUBLED else 'black'
                text = ax.text(j, i, f'{value:.0f}',
                             ha='center', va='center', 
                             color=text_color, fontsize=10, fontweight='bold')
        
        # カラーバー（閾値: ≤20=赤, 20-50=黄, >50=緑）
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, ticks=[10, 35, 75])
        cbar.ax.set_yticklabels(['≤20 困っている', '20-50 中間', '>50 困っていない'], fontsize=10)
        cbar.set_label('強みスコア', rotation=270, labelpad=20, fontsize=11)
        
        # タイトルと説明
        ax.set_xlabel('調査セクション', fontsize=12, labelpad=10)
        ax.set_ylabel('部門', fontsize=12)
        
        plt.title('部門別の強み分析（RAG: ≤20=赤/困っている, >50=緑/困っていない）', 
                 fontsize=14, fontweight='bold', pad=20)
        
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
2. [可視化一覧表](#2-可視化一覧表)
3. [A: 導入ツール・ベンダーマップ](#3-a-導入ツールベンダーマップ)
4. [B: 意思決定プロセスの実態](#4-b-意思決定プロセスの実態)
5. [C: セキュリティ成熟度マップ](#5-c-セキュリティ成熟度マップ)
6. [D: 困りごと・ニーズ分析](#6-d-困りごとニーズ分析)
7. [E: 部門別プロファイル](#7-e-部門別プロファイル)
8. [グラフ一覧](#8-グラフ一覧)

---

## 1. エグゼクティブサマリー

### 調査概要

- **総回答数**: {self.analysis_results['metadata']['total_respondents']}件
- **調査項目**: 全7セクション・37問

"""
        
        # セキュリティ成熟度サマリー
        sm = self.analysis_results.get('security_maturity', {}).get('overall', {})
        md += f"- **セキュリティ成熟度スコア**: {sm.get('percentage', 0):.1f}% ({sm.get('maturity_level', '不明')})\n\n"
        md += "---\n\n"
        
        # 可視化一覧表
        md += """## 2. 可視化一覧表

| 可視化 | 目的 | わかること | わからないこと | データソース |
|--------|------|-----------|---------------|-------------|
| **A: 導入ツール・ベンダーマップ** | 全社のツール・ベンダー利用状況を一覧化 | ・同じカテゴリで複数ツールが存在する領域<br>・部門ごとの契約状況<br>・年間コストの全体像 | ・統合した場合の正確な削減額（契約条件の詳細が必要）<br>・なぜそのツールを選んだのか（個別ヒアリングが必要） | セクション1 Q1<br>セクション6 Q1 |
| **B: 意思決定プロセスの実態** | 判断プロセスのバラつきを把握 | ・金額基準の部門間のバラつき<br>・実際にどういうプロセスで決めているか<br>・何に困っているか | ・なぜバラついているのか（歴史的経緯、組織文化）<br>・判断の質（良い判断ができているか） | セクション1 Q2, Q4, Q5 |
| **C: セキュリティ成熟度マップ** | セキュリティ対策の実施状況を部門別に把握 | ・部門別のセキュリティ成熟度<br>・特に対応が遅れている項目<br>・共通アカウント利用など明らかな問題 | ・実装の技術的な正確性（監査が必要）<br>・実際のインシデント発生状況（ログ分析が必要） | セクション2 Q1-Q4 |
| **D: 困りごと・ニーズ分析** | 現場が求める支援を特定 | ・現場が最も求めている支援<br>・共通する困りごと<br>・地域による違い | ・支援策の具体的な設計内容（別途検討が必要） | 全セクションの「困ること」<br>セクション5,6,7の支援質問 |
| **E: 部門別プロファイル** | ベストプラクティス保有部門の特定 | ・セクション別に困っていない度合い<br>・ベストプラクティスを持つ可能性がある部門<br>・部門間の知識共有の機会 | ・具体的なベストプラクティスの内容（個別ヒアリングが必要） | 全セクションの困りごと |

---

"""
        
        # A: 導入ツール・ベンダーマップ
        md += "## 3. A: 導入ツール・ベンダーマップ\n\n"
        md += '<img src="graphs/visualization_A_vendor_map.png" alt="導入ツール・ベンダーマップ" style="width: 50%;" />\n\n'
        md += "---\n\n"
        
        # B: 意思決定プロセスの実態
        md += "## 4. B: 意思決定プロセスの実態\n\n"
        md += "### 地域別\n\n"
        md += '<img src="graphs/visualization_B_decision_process_by_region.png" alt="意思決定プロセス（地域別）" style="width: 50%;" />\n\n'
        md += "### 部門別\n\n"
        md += '<img src="graphs/visualization_B_decision_process_by_department.png" alt="意思決定プロセス（部門別）" style="width: 50%;" />\n\n'
        md += "---\n\n"
        
        # C: セキュリティ成熟度マップ
        md += "## 5. C: セキュリティ成熟度マップ\n\n"
        md += "### 地域別\n\n"
        md += '<img src="graphs/visualization_C_security_maturity_by_region.png" alt="セキュリティ成熟度（地域別）" style="width: 50%;" />\n\n'
        md += "### 部門別\n\n"
        md += '<img src="graphs/visualization_C_security_maturity_by_department.png" alt="セキュリティ成熟度（部門別）" style="width: 50%;" />\n\n'
        md += "---\n\n"
        
        # D: 困りごと・ニーズ分析
        md += "## 6. D: 困りごと・ニーズ分析\n\n"
        
        md += "### 困りごとトップ10（地域比較）\n\n"
        
        md += '<img src="graphs/visualization_D1_pain_points_regional_comparison.png" alt="困りごとトップ10（地域比較）" style="width: 50%;" />\n\n'
        
        md += "### 必要な支援トップ10（地域比較）\n\n"
        
        md += '<img src="graphs/visualization_D2_support_needs_regional_comparison.png" alt="必要な支援トップ10（地域比較）" style="width: 50%;" />\n\n'
        
        md += "---\n\n"
        
        # E: 部門別プロファイル
        md += "## 7. E: 部門別の強み分析\n\n"
        
        md += '<img src="graphs/visualization_E_department_profile.png" alt="部門別の強み分析（困りごとの少なさ）" style="width: 50%;" />\n\n'
        
        md += "---\n\n"
        
        # グラフ一覧
        md += "## 8. グラフ一覧\n\n"
        md += "### 5つの主要可視化\n\n"
        md += "1. [A: 導入ツール・ベンダーマップ](graphs/visualization_A_vendor_map.png)\n"
        md += "2. B: 意思決定プロセスの実態\n"
        md += "   - [地域別](graphs/visualization_B_decision_process_by_region.png)\n"
        md += "   - [部門別](graphs/visualization_B_decision_process_by_department.png)\n"
        md += "3. C: セキュリティ成熟度マップ\n"
        md += "   - [地域別](graphs/visualization_C_security_maturity_by_region.png)\n"
        md += "   - [部門別](graphs/visualization_C_security_maturity_by_department.png)\n"
        md += "4. D: 困りごと・ニーズ分析（地域比較）\n"
        md += "   - [困りごとトップ10](graphs/visualization_D1_pain_points_regional_comparison.png)\n"
        md += "   - [必要な支援トップ10](graphs/visualization_D2_support_needs_regional_comparison.png)\n"
        md += "5. [E: 部門別プロファイル](graphs/visualization_E_department_profile.png)\n\n"
        
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
        
        # 可視化ファイル数のカウント（Dは辞書で2ファイル）
        viz_count = 0
        for v in results['visualizations'].values():
            if v:
                if isinstance(v, dict):
                    viz_count += len(v)  # Dの場合は2ファイル
                else:
                    viz_count += 1
        
        print(f"  ✓ 可視化: {viz_count}個")
        
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
