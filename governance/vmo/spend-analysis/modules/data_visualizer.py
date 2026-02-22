"""
データ可視化処理モジュール
分析結果をグラフ化して可視化する
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # バックエンドを先に設定
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from pathlib import Path
from typing import Optional
import sys

# 日本語フォント設定（確実に動作する方法）
def setup_japanese_font():
    """日本語フォントを設定"""
    # システムのフォントリストを取得
    available_fonts = set([f.name for f in fm.fontManager.ttflist])
    
    # Mac用の日本語フォント候補
    mac_fonts = [
        'Hiragino Sans',
        'Hiragino Kaku Gothic Pro',
        'Hiragino Kaku Gothic ProN',
        'Hiragino Maru Gothic Pro',
        'Hiragino Mincho Pro',
        'Yu Gothic',
        'AppleGothic',
        'Osaka',
    ]
    
    # Windows用の日本語フォント候補
    windows_fonts = [
        'Yu Gothic',
        'MS Gothic',
        'MS PGothic',
        'Meiryo',
        'MS UI Gothic',
    ]
    
    # Linux用の日本語フォント候補
    linux_fonts = [
        'Noto Sans CJK JP',
        'Noto Sans JP',
        'IPAexGothic',
        'IPAGothic',
        'TakaoPGothic',
        'VL Gothic',
    ]
    
    # 全候補を統合
    all_candidates = mac_fonts + windows_fonts + linux_fonts
    
    # 利用可能なフォントを検索
    selected_font = None
    for font in all_candidates:
        if font in available_fonts:
            selected_font = font
            print(f"  📝 使用する日本語フォント: {selected_font}")
            break
    
    if selected_font:
        # 見つかったフォントを最優先に設定
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = [selected_font] + matplotlib.rcParams['font.sans-serif']
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = [selected_font] + plt.rcParams['font.sans-serif']
    else:
        print("  ⚠️  警告: 推奨される日本語フォントが見つかりません")
        print(f"     利用可能なフォント数: {len(available_fonts)}")
        # デバッグ用：日本語っぽいフォントを探す
        japanese_like = [f for f in available_fonts if any(keyword in f for keyword in 
                        ['Gothic', 'Mincho', 'Meiryo', 'Hiragino', 'Yu', 'IPA', 'Noto', 'MS'])]
        if japanese_like:
            print(f"     日本語フォント候補: {japanese_like[:3]}")
            # 最初の候補を使用
            matplotlib.rcParams['font.sans-serif'] = [japanese_like[0]] + matplotlib.rcParams['font.sans-serif']
            plt.rcParams['font.sans-serif'] = [japanese_like[0]] + plt.rcParams['font.sans-serif']
            print(f"  📝 代替フォントを使用: {japanese_like[0]}")
    
    # マイナス記号の文字化け対策
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.rcParams['axes.unicode_minus'] = False
    
    return selected_font

# フォント設定を実行
print("\n🔤 日本語フォント設定:")
JAPANESE_FONT = setup_japanese_font()
print()


class DataVisualizer:
    """分析結果を可視化するクラス"""
    
    def __init__(self, analysis_dir: Path):
        """
        Args:
            analysis_dir: 分析結果CSVファイルが格納されているディレクトリ
        """
        self.analysis_dir = analysis_dir
        
        # グラフスタイル設定
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        # seabornがフォント設定を上書きするので、再度設定
        if JAPANESE_FONT:
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = [JAPANESE_FONT] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            print(f"  🔄 フォント再設定: {JAPANESE_FONT}\n")
        
    def load_analysis_data(self, filename: str) -> pd.DataFrame:
        """
        分析結果CSVを読み込む
        
        Args:
            filename: CSVファイル名
            
        Returns:
            DataFrameオブジェクト
        """
        filepath = self.analysis_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
        
        return pd.read_csv(filepath, encoding='utf-8-sig')
    
    def visualize_vendor_spend_top20(self, output_dir: Path):
        """
        ベンダー別支出額TOP20の棒グラフを作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 ベンダー別支出額TOP20グラフを作成中...")
        
        # データ読み込み
        vendor_spend = self.load_analysis_data('vendor_spend_analysis.csv')
        top20 = vendor_spend.head(20)
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(14, 10))
        
        bars = ax.barh(
            range(len(top20)), 
            top20['total_annual_spend'],
            color=sns.color_palette("viridis", len(top20))
        )
        
        # ベンダー名とランクをY軸に設定
        ax.set_yticks(range(len(top20)))
        ax.set_yticklabels([f"{row['rank']}. {row['vendor_name'][:20]}" 
                            for _, row in top20.iterrows()])
        
        # X軸フォーマット（百万円単位）
        ax.set_xlabel('年間支出額（百万円）', fontsize=12, fontweight='bold')
        ax.set_ylabel('ベンダー', fontsize=12, fontweight='bold')
        ax.set_title('ベンダー別年間支出額 TOP20', fontsize=14, fontweight='bold', pad=20)
        
        # X軸の値を百万円単位に変換
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # グリッド線
        ax.grid(axis='x', alpha=0.3)
        
        # 各バーに金額と構成比を表示
        for i, (idx, row) in enumerate(top20.iterrows()):
            ax.text(
                row['total_annual_spend'], 
                i,
                f" ¥{row['total_annual_spend']/1e6:.1f}M ({row['spend_ratio']:.1f}%)",
                va='center',
                fontsize=9
            )
        
        plt.tight_layout()
        plt.savefig(output_dir / 'vendor_spend_top20.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ vendor_spend_top20.png")
    
    def visualize_pareto_chart(self, output_dir: Path):
        """
        パレート図（累積構成比）を作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 パレート図を作成中...")
        
        # データ読み込み
        pareto_data = self.load_analysis_data('pareto_analysis.csv')
        
        # グラフ作成
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # 棒グラフ（支出額）
        x = range(len(pareto_data))
        bars = ax1.bar(
            x, 
            pareto_data['total_annual_spend'],
            color='steelblue',
            alpha=0.7,
            label='年間支出額'
        )
        
        ax1.set_xlabel('ベンダー（支出額降順）', fontsize=12, fontweight='bold')
        ax1.set_ylabel('年間支出額（百万円）', fontsize=12, fontweight='bold', color='steelblue')
        ax1.tick_params(axis='y', labelcolor='steelblue')
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # 累積構成比の折れ線グラフ
        ax2 = ax1.twinx()
        line = ax2.plot(
            x, 
            pareto_data['cumulative_ratio'],
            color='red',
            marker='o',
            linewidth=2,
            markersize=4,
            label='累積構成比'
        )
        
        ax2.set_ylabel('累積構成比（%）', fontsize=12, fontweight='bold', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim(0, 105)
        
        # 80%ラインを追加
        ax2.axhline(y=80, color='green', linestyle='--', linewidth=2, alpha=0.7, label='80%ライン')
        
        # 80%に達するベンダー数を強調
        vendors_80 = len(pareto_data[pareto_data['cumulative_ratio'] <= 80])
        ax2.axvline(x=vendors_80-1, color='green', linestyle='--', linewidth=2, alpha=0.7)
        
        # タイトル
        ax1.set_title('パレート図：ベンダー別支出の累積構成比', fontsize=14, fontweight='bold', pad=20)
        
        # 凡例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # グリッド
        ax1.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'pareto_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ pareto_chart.png")
    
    def visualize_category_spend_pie(self, output_dir: Path):
        """
        サービスカテゴリ別支出の円グラフを作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 サービスカテゴリ別支出円グラフを作成中...")
        
        # データ読み込み
        category_spend = self.load_analysis_data('category_spend_analysis.csv')
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 色設定
        colors = sns.color_palette("Set3", len(category_spend))
        
        # 円グラフ
        wedges, texts, autotexts = ax.pie(
            category_spend['total_spend'],
            labels=category_spend['service_category'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # パーセンテージのフォントを太字に
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('サービスカテゴリ別支出構成比', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'category_spend_pie.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ category_spend_pie.png")
    
    def visualize_category_spend_bar(self, output_dir: Path):
        """
        サービスカテゴリ別支出の棒グラフを作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 サービスカテゴリ別支出棒グラフを作成中...")
        
        # データ読み込み
        category_spend = self.load_analysis_data('category_spend_analysis.csv')
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(
            range(len(category_spend)),
            category_spend['total_spend'],
            color=sns.color_palette("husl", len(category_spend))
        )
        
        ax.set_yticks(range(len(category_spend)))
        ax.set_yticklabels(category_spend['service_category'])
        ax.set_xlabel('支出額（百万円）', fontsize=12, fontweight='bold')
        ax.set_ylabel('サービスカテゴリ', fontsize=12, fontweight='bold')
        ax.set_title('サービスカテゴリ別支出額', fontsize=14, fontweight='bold', pad=20)
        
        # X軸を百万円単位に
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # 各バーに金額を表示
        for i, (idx, row) in enumerate(category_spend.iterrows()):
            ax.text(
                row['total_spend'],
                i,
                f" ¥{row['total_spend']/1e6:.1f}M ({row['spend_ratio']:.1f}%)",
                va='center',
                fontsize=9
            )
        
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'category_spend_bar.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ category_spend_bar.png")
    
    def visualize_contract_type_spend(self, output_dir: Path):
        """
        契約形態別支出の棒グラフを作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 契約形態別支出グラフを作成中...")
        
        # データ読み込み
        contract_type = self.load_analysis_data('contract_type_spend_analysis.csv')
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(
            range(len(contract_type)),
            contract_type['total_annual_spend'],
            color=sns.color_palette("muted", len(contract_type))
        )
        
        ax.set_yticks(range(len(contract_type)))
        ax.set_yticklabels(contract_type['contract_type'])
        ax.set_xlabel('年間支出額（百万円）', fontsize=12, fontweight='bold')
        ax.set_ylabel('契約形態', fontsize=12, fontweight='bold')
        ax.set_title('契約形態別年間支出額', fontsize=14, fontweight='bold', pad=20)
        
        # X軸を百万円単位に
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # 各バーに金額と契約数を表示
        for i, (idx, row) in enumerate(contract_type.iterrows()):
            ax.text(
                row['total_annual_spend'],
                i,
                f" ¥{row['total_annual_spend']/1e6:.1f}M ({row['contract_count']}件)",
                va='center',
                fontsize=9
            )
        
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'contract_type_spend.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ contract_type_spend.png")
    
    def visualize_unit_price_variance(self, output_dir: Path):
        """
        契約単価のばらつきを箱ひげ図で作成（1件のカテゴリは散布図）
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 契約単価ばらつきグラフを作成中...")
        
        # データ読み込み
        unit_price_stats = self.load_analysis_data('unit_price_analysis.csv')
        unit_price_details = self.load_analysis_data('unit_price_details.csv')
        
        # 全カテゴリを対象
        categories_all = unit_price_stats['primary_category'].tolist()
        plot_data = unit_price_details[unit_price_details['primary_category'].isin(categories_all)]
        
        if len(categories_all) == 0:
            print("  ⚠️  グラフ作成不可：カテゴリがありません")
            return
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # カテゴリ別にデータを整理（上位10カテゴリまで）
        categories_to_plot = categories_all[:10]
        data_by_category = []
        labels = []
        single_point_positions = []  # 1件のカテゴリの位置
        single_point_values = []     # 1件のカテゴリの値
        
        for i, category in enumerate(categories_to_plot):
            cat_data = plot_data[plot_data['primary_category'] == category]['monthly_amount']
            labels.append(category)
            
            if len(cat_data) >= 2:
                # 2件以上：箱ひげ図用
                data_by_category.append(cat_data)
            elif len(cat_data) == 1:
                # 1件のみ：散布図用（ダミーデータで位置確保）
                data_by_category.append([cat_data.iloc[0], cat_data.iloc[0]])  # ダミー
                single_point_positions.append(i + 1)  # 位置（1始まり）
                single_point_values.append(cat_data.iloc[0])
        
        if len(data_by_category) == 0:
            print("  ⚠️  グラフ作成不可：データが不足しています")
            return
        
        # 箱ひげ図
        bp = ax.boxplot(data_by_category, labels=labels, patch_artist=True, 
                        vert=True, widths=0.6, showfliers=True)
        
        # 色設定
        colors = sns.color_palette("Set3", len(data_by_category))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # 1件のみのカテゴリを散布図として上書き表示
        if len(single_point_positions) > 0:
            ax.scatter(single_point_positions, single_point_values, 
                      color='red', s=100, zorder=5, marker='D',
                      label='契約1件のみ')
            
            # 凡例を追加
            ax.legend(loc='upper right', fontsize=10)
        
        ax.set_xlabel('サービスカテゴリ', fontsize=12, fontweight='bold')
        ax.set_ylabel('月額単価（百万円）', fontsize=12, fontweight='bold')
        
        # タイトルに注記を追加
        title = 'カテゴリ別契約単価のばらつき'
        if len(single_point_positions) > 0:
            title += '\n（赤ダイヤ：契約1件のみ）'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Y軸を百万円単位に
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # X軸ラベルを回転
        plt.xticks(rotation=45, ha='right')
        
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'unit_price_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ unit_price_boxplot.png")
    
    def visualize_unit_price_comparison(self, output_dir: Path):
        """
        契約単価の比較グラフを作成（CV値の高いカテゴリ）
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 契約単価比較グラフを作成中...")
        
        # データ読み込み
        unit_price_stats = self.load_analysis_data('unit_price_analysis.csv')
        
        # CV値が高い順に上位8カテゴリを選択
        top_variance = unit_price_stats.head(8)
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(14, 10))
        
        y_pos = range(len(top_variance))
        
        # 最小値、平均値、最大値をプロット
        ax.barh(y_pos, top_variance['max_price'], color='lightcoral', alpha=0.3, label='最大値')
        ax.barh(y_pos, top_variance['avg_price'], color='steelblue', alpha=0.7, label='平均値')
        
        # エラーバー（標準偏差）
        ax.errorbar(top_variance['avg_price'], y_pos, 
                   xerr=top_variance['std_price'],
                   fmt='none', ecolor='red', capsize=5, alpha=0.6, label='標準偏差')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_variance['primary_category'])
        ax.set_xlabel('月額単価（百万円）', fontsize=12, fontweight='bold')
        ax.set_ylabel('サービスカテゴリ', fontsize=12, fontweight='bold')
        ax.set_title('単価ばらつきが大きいカテゴリ（上位8件）', fontsize=14, fontweight='bold', pad=20)
        
        # X軸を百万円単位に
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}'))
        
        # 各バーにCV値を表示
        for i, (idx, row) in enumerate(top_variance.iterrows()):
            ax.text(
                row['max_price'],
                i,
                f" CV={row['cv']:.1f}%",
                va='center',
                fontsize=9,
                color='red',
                fontweight='bold'
            )
        
        ax.legend(loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'unit_price_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ unit_price_comparison.png")
    
    def visualize_auto_renewal_contracts(self, output_dir: Path):
        """
        自動更新契約の可視化
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("📊 自動更新契約グラフを作成中...")
        
        # データ読み込み
        auto_renewal = self.load_analysis_data('auto_renewal_analysis.csv')
        
        # グラフ作成（2分割）
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # ラベル作成
        labels = ['自動更新あり' if flag else '自動更新なし' for flag in auto_renewal['auto_renewal_flag']]
        
        # 左：契約件数
        colors1 = ['#ff9999', '#66b3ff']
        wedges1, texts1, autotexts1 = ax1.pie(
            auto_renewal['contract_count'],
            labels=labels,
            autopct='%1.1f%%',
            colors=colors1,
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        for autotext in autotexts1:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title('契約件数の内訳', fontsize=12, fontweight='bold', pad=15)
        
        # 右：年間支出額
        colors2 = ['#ffcc99', '#99ccff']
        wedges2, texts2, autotexts2 = ax2.pie(
            auto_renewal['annual_amount'],
            labels=labels,
            autopct='%1.1f%%',
            colors=colors2,
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        for autotext in autotexts2:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax2.set_title('年間支出額の内訳', fontsize=12, fontweight='bold', pad=15)
        
        plt.suptitle('自動更新契約の分析', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig(output_dir / 'auto_renewal_contracts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("  ✓ auto_renewal_contracts.png")
    
    def visualize_all(self, output_dir: Path):
        """
        すべての可視化グラフを一括作成
        
        Args:
            output_dir: グラフ画像の出力先ディレクトリ
        """
        print("\n🎨 データ可視化を開始します...\n")
        
        output_dir.mkdir(exist_ok=True)
        
        try:
            # 1. ベンダー別支出分析
            self.visualize_vendor_spend_top20(output_dir)
            self.visualize_pareto_chart(output_dir)
            
            # 2. カテゴリ別支出分析
            self.visualize_category_spend_pie(output_dir)
            self.visualize_category_spend_bar(output_dir)
            
            # 3. 契約単価分析（NEW）
            self.visualize_unit_price_variance(output_dir)
            self.visualize_unit_price_comparison(output_dir)
            
            # 4. 契約形態別支出分析
            self.visualize_contract_type_spend(output_dir)
            
            # 5. 自動更新契約分析（NEW）
            self.visualize_auto_renewal_contracts(output_dir)
            
            print(f"\n✅ 全てのグラフを作成しました: {output_dir}\n")
            
        except Exception as e:
            print(f"❌ グラフ作成中にエラーが発生しました: {e}")
            raise
