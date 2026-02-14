"""
ITガバナンス実態調査 分析システム - メインプログラム
"""
import sys
import os
from modules.data_generator import DataGenerator
from modules.data_preprocess import DataPreprocessor
from modules.data_analyser import ITGovernanceAnalyser
from modules.report_generator import ITGovernanceReportGenerator
from modules.util import print_section, ensure_dir


def get_sample_size():
    """ユーザーにサンプルサイズを入力させる"""
    while True:
        try:
            size_input = input("\n生成するサンプル数を入力してください（デフォルト: 100）: ").strip()
            
            if size_input == '':
                return None  # デフォルト値を使用
            
            size = int(size_input)
            if size <= 0:
                print("❌ エラー: 1以上の数値を入力してください")
                continue
            
            if size > 10000:
                confirm = input(f"⚠️  {size}件は多いですが、本当に生成しますか？ (Y/N): ").strip().upper()
                if confirm != 'Y':
                    continue
            
            return size
            
        except ValueError:
            print("❌ エラー: 有効な数値を入力してください")


def confirm_action(message):
    """アクションの確認を取る"""
    response = input(f"\n{message} (Y/N): ").strip().upper()
    return response == 'Y'


def main():
    """メイン処理"""
    print_section("ITガバナンス実態調査 分析システム")
    print("\nこのシステムは以下の機能を提供します:")
    print("  1. サンプルデータの自動生成")
    print("  2. データの前処理（バイナリ変換・One-Hot Encoding）")
    print("  3. データ分析（選択率・成熟度・困りごと分析）")
    print("  4. レポート生成（5つの可視化 + Markdownレポート）")
    
    # 必要なディレクトリを作成
    ensure_dir('csv')
    ensure_dir('out')
    ensure_dir('reports/graphs')
    
    # ========================================
    # ステップ1: データ生成
    # ========================================
    print_section("Step 1: サンプルデータ生成")
    
    raw_data_exists = os.path.exists('csv/survey_sample_data.csv')
    
    if raw_data_exists:
        print("既存の生データが見つかりました: csv/survey_sample_data.csv")
        if not confirm_action("新しいサンプルデータを生成しますか？（Nで既存データを使用）"):
            print("既存のサンプルデータを使用します。")
        else:
            # 新規生成
            sample_size = get_sample_size()
            try:
                generator = DataGenerator()
                df = generator.generate(sample_size=sample_size)
                generator.save_to_csv(df)
                generator.print_summary(df)
                
                print("\n✓ データ生成が完了しました！")
                print(f"  - csv/survey_sample_data.csv ({len(df)}件)")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    else:
        # 新規生成
        if not confirm_action("サンプルデータを生成しますか？"):
            print("\n処理を終了します。")
            return
        
        sample_size = get_sample_size()
        
        try:
            generator = DataGenerator()
            df = generator.generate(sample_size=sample_size)
            generator.save_to_csv(df)
            generator.print_summary(df)
            
            print("\n✓ データ生成が完了しました！")
            print(f"  - csv/survey_sample_data.csv ({len(df)}件)")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # ========================================
    # ステップ2: データ前処理
    # ========================================
    print_section("Step 2: データ前処理")
    
    preprocessed_data_exists = os.path.exists('csv/survey_preprocessed_data.csv')
    
    if preprocessed_data_exists:
        print("既存の前処理済みデータが見つかりました: csv/survey_preprocessed_data.csv")
        if not confirm_action("前処理を再実行しますか？（Nで既存データを使用）"):
            print("既存の前処理済みデータを使用します。")
        else:
            # 前処理実行
            try:
                preprocessor = DataPreprocessor()
                df_raw = preprocessor.load_raw_data()
                df_processed = preprocessor.preprocess(df_raw)
                preprocessor.save_preprocessed_data(df_processed)
                preprocessor.save_preprocessing_report()
                preprocessor.print_summary(df_processed)
                
                print("\n✓ データ前処理が完了しました！")
                print(f"  - csv/survey_preprocessed_data.csv ({df_processed.shape[0]}件 × {df_processed.shape[1]}列)")
                print(f"  - out/preprocessing_report.json")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    else:
        if not confirm_action("データ前処理を実行しますか？"):
            print("前処理をスキップします。")
        else:
            # 前処理実行
            try:
                preprocessor = DataPreprocessor()
                df_raw = preprocessor.load_raw_data()
                df_processed = preprocessor.preprocess(df_raw)
                preprocessor.save_preprocessed_data(df_processed)
                preprocessor.save_preprocessing_report()
                preprocessor.print_summary(df_processed)
                
                print("\n✓ データ前処理が完了しました！")
                print(f"  - csv/survey_preprocessed_data.csv ({df_processed.shape[0]}件 × {df_processed.shape[1]}列)")
                print(f"  - out/preprocessing_report.json")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    # ========================================
    # ステップ3: データ分析
    # ========================================
    print_section("Step 3: データ分析")
    
    analysis_results_exists = os.path.exists('out/analysis_results.json')
    
    if analysis_results_exists:
        print("既存の分析結果が見つかりました: out/analysis_results.json")
        if not confirm_action("分析を再実行しますか？（Nで既存結果を使用）"):
            print("既存の分析結果を使用します。")
        else:
            # 分析実行
            try:
                analyser = ITGovernanceAnalyser()
                analyser.load_data()
                results = analyser.run_analysis_pipeline()
                analyser.save_results()
                analyser.print_summary()
                
                print("\n✓ データ分析が完了しました！")
                print(f"  - out/analysis_results.json")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    else:
        if not confirm_action("データ分析を実行しますか？"):
            print("分析をスキップします。")
        else:
            # 分析実行
            try:
                analyser = ITGovernanceAnalyser()
                analyser.load_data()
                results = analyser.run_analysis_pipeline()
                analyser.save_results()
                analyser.print_summary()
                
                print("\n✓ データ分析が完了しました！")
                print(f"  - out/analysis_results.json")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    # ========================================
    # ステップ4: レポート生成
    # ========================================
    print_section("Step 4: レポート生成")
    
    markdown_report_exists = os.path.exists('reports/governance_report.md')
    
    if markdown_report_exists:
        print("既存のレポートが見つかりました: reports/governance_report.md")
        if not confirm_action("レポートを再生成しますか？（Nで既存レポートを使用）"):
            print("既存のレポートを使用します。")
        else:
            # レポート生成
            try:
                report_gen = ITGovernanceReportGenerator()
                results = report_gen.generate_full_report()
                
                print("\n✓ レポート生成が完了しました！")
                print(f"  - {results['markdown_report']}")
                print(f"  - 可視化: {len([v for v in results['visualizations'].values() if v])}個")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    else:
        if not confirm_action("レポート生成を実行しますか？"):
            print("レポート生成をスキップします。")
        else:
            # レポート生成
            try:
                report_gen = ITGovernanceReportGenerator()
                results = report_gen.generate_full_report()
                
                print("\n✓ レポート生成が完了しました！")
                print(f"  - {results['markdown_report']}")
                print(f"  - 可視化: {len([v for v in results['visualizations'].values() if v])}個")
                
            except Exception as e:
                print(f"\n❌ エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    # ========================================
    # 完了メッセージ
    # ========================================
    print_section("処理完了")
    print("\n生成されたファイル:")
    if os.path.exists('csv/survey_sample_data.csv'):
        print("  ✓ csv/survey_sample_data.csv - 生データ")
    if os.path.exists('csv/survey_preprocessed_data.csv'):
        print("  ✓ csv/survey_preprocessed_data.csv - 前処理済みデータ")
    if os.path.exists('out/preprocessing_report.json'):
        print("  ✓ out/preprocessing_report.json - 前処理レポート")
    if os.path.exists('out/analysis_results.json'):
        print("  ✓ out/analysis_results.json - 分析結果")
    
    print("\n次のステップ:")
    print("  - レポート生成機能は今後実装予定です")
    print("  - 分析結果（JSON）をExcelやBIツールで可視化できます")


if __name__ == '__main__':
    main()
