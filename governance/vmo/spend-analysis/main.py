#!/usr/bin/env python3
"""
ベンダーマネジメント支出分析ツール

ベンダー支出データを分析・可視化します。

使い方:
    # 方法1: inサブフォルダにCSVファイルを配置して実行
    python main.py
    
    # 方法2: データディレクトリを明示的に指定
    python main.py <data_directory>
    
例:
    python main.py
    python main.py ../vendor_management/out
"""

import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_analyzer import DataAnalyzer
from modules.data_visualizer import DataVisualizer


def print_banner():
    """バナーを表示"""
    print("=" * 80)
    print("  ベンダーマネジメント支出分析ツール - Spend Analysis")
    print("=" * 80)
    print()


def print_usage():
    """使い方を表示"""
    print("使い方:")
    print("  # 方法1: inサブフォルダにCSVファイルを配置して実行")
    print("  python main.py")
    print()
    print("  # 方法2: データディレクトリを明示的に指定")
    print("  python main.py <data_directory>")
    print()
    print("引数:")
    print("  data_directory  : CSVデータが格納されているディレクトリパス（省略時は./inを使用）")
    print()
    print("例:")
    print("  python main.py")
    print("  python main.py ../vendor_management/out")
    print("  python main.py /path/to/csv/data")
    print()


def validate_data_directory(data_dir: Path) -> bool:
    """
    データディレクトリの検証
    
    Args:
        data_dir: データディレクトリのパス
        
    Returns:
        検証結果（True: OK, False: NG）
    """
    if not data_dir.exists():
        print(f"❌ エラー: ディレクトリが存在しません: {data_dir}")
        return False
    
    if not data_dir.is_dir():
        print(f"❌ エラー: ディレクトリではありません: {data_dir}")
        return False
    
    # 必要なCSVファイルの存在確認
    required_files = ['vendors.csv', 'contracts.csv', 'orders.csv', 'services.csv']
    missing_files = []
    
    for filename in required_files:
        if not (data_dir / filename).exists():
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ エラー: 必要なファイルが見つかりません:")
        for filename in missing_files:
            print(f"  - {filename}")
        return False
    
    return True


def main():
    """メイン処理"""
    print_banner()
    
    # プロジェクトのディレクトリ設定
    project_root = Path(__file__).parent
    
    # データディレクトリの取得
    if len(sys.argv) >= 2:
        # コマンドライン引数でデータディレクトリが指定された場合
        data_dir = Path(sys.argv[1])
        print(f"📂 指定されたデータディレクトリ: {data_dir.absolute()}\n")
    else:
        # 引数がない場合はinサブフォルダを使用
        data_dir = project_root / "in"
        print(f"📂 デフォルトのデータディレクトリを使用: {data_dir.absolute()}\n")
    
    # データディレクトリの検証
    if not validate_data_directory(data_dir):
        print()
        print_usage()
        sys.exit(1)
    output_dir = project_root / "out"
    png_dir = project_root / "png"
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir.mkdir(exist_ok=True)
    png_dir.mkdir(exist_ok=True)
    
    try:
        # ========================================
        # ステップ1: データ分析・集計
        # ========================================
        print("=" * 80)
        print("  STEP 1: データ分析・集計")
        print("=" * 80)
        print()
        
        analyzer = DataAnalyzer(data_dir)
        analyzer.load_data()
        analyzer.save_analysis_results(output_dir)
        
        # ========================================
        # ステップ2: データ可視化
        # ========================================
        print("=" * 80)
        print("  STEP 2: データ可視化")
        print("=" * 80)
        
        visualizer = DataVisualizer(output_dir)
        visualizer.visualize_all(png_dir)
        
        # ========================================
        # 完了メッセージ
        # ========================================
        print("=" * 80)
        print("  🎉 分析完了")
        print("=" * 80)
        print()
        print("📊 分析結果:")
        print(f"  - CSV集計データ: {output_dir.absolute()}")
        print(f"  - グラフ画像:     {png_dir.absolute()}")
        print()
        
        # 生成されたファイル一覧
        print("📁 生成されたファイル:")
        print()
        print("  [CSV集計データ]")
        csv_files = sorted(output_dir.glob('*.csv'))
        for csv_file in csv_files:
            print(f"    ✓ {csv_file.name}")
        
        print()
        print("  [グラフ画像]")
        png_files = sorted(png_dir.glob('*.png'))
        for png_file in png_files:
            print(f"    ✓ {png_file.name}")
        
        print()
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
