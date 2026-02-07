import os
import sys
from modules.ocr_processor import OCRProcessor
from modules.data_validator import DataValidator
from modules.duplicate_checker import DuplicateChecker
from modules.history_exporter import HistoryExporter

def display_header():
    """ヘッダーを表示"""
    print("=" * 70)
    print("  請求書OCR処理システム")
    print("=" * 70)
    print()

def display_folder_structure():
    """期待されるフォルダ構成を表示"""
    print("\n期待されるフォルダ構成:")
    print("  pdf/                (請求書PDFを配置)")
    print("  history/           (過去の請求書JSON履歴)")
    print()

def select_mode():
    """処理モードを選択"""
    print("処理モードを選択してください:")
    print("  1. 請求書OCR処理を実行")
    print("  2. 過去実績をCSVで出力")
    print()
    
    while True:
        choice = input("選択 (1/2): ").strip()
        
        if choice == "1":
            print("→ 請求書OCR処理を実行します\n")
            return 'ocr'
        elif choice == "2":
            print("→ 過去実績をCSVで出力します\n")
            return 'export'
        else:
            print("エラー: 1 または 2 を入力してください。")

def run_ocr_processing():
    """OCR処理を実行"""
    # パス設定
    config_path = os.path.join('config', 'fields.yaml')
    pdf_folder = 'pdf'
    output_folder = 'output'
    history_folder = 'history'
    
    # 設定ファイルの存在確認
    if not os.path.exists(config_path):
        print(f"エラー: 設定ファイルが見つかりません: {config_path}")
        sys.exit(1)
    
    # PDFフォルダの存在確認
    if not os.path.exists(pdf_folder):
        print(f"エラー: PDFフォルダが見つかりません: {pdf_folder}")
        display_folder_structure()
        sys.exit(1)
    
    print("処理対象: 請求書")
    
    try:
        # OCRプロセッサの初期化
        processor = OCRProcessor(config_path)
        
        # 請求書フォルダを処理
        output_path, file_count = processor.process_folder(
            pdf_folder, 
            'invoice', 
            output_folder
        )
        
        # 結果表示
        if output_path:
            print("\n【処理結果】")
            print(f"  ✓ 請求書 → {output_path}")
            
            # データチェック処理を実行
            print("\n" + "=" * 70)
            print("  JSONデータチェック処理を開始します")
            print("=" * 70)
            
            validator = DataValidator(config_folder='config')
            validation_result = validator.validate_json_file(output_path)
            
            # バリデーション結果のサマリーを表示
            if validation_result.get('success'):
                print("\n" + "=" * 70)
                print("  【バリデーション結果サマリー】")
                print("=" * 70)
                
                total_docs = validation_result.get('total_documents', 0)
                total_valid = validation_result.get('validated_count', 0)
                total_invalid = validation_result.get('invalidated_count', 0)
                
                print(f"  請求書: 良好 {total_valid}件 / "
                      f"要確認 {total_invalid}件 / "
                      f"合計 {total_docs}件")
                print("=" * 70 + "\n")
                
                # 重複チェック処理を実行
                print("=" * 70)
                print("  二重払い防止チェック処理を開始します")
                print("=" * 70)
                
                duplicate_checker = DuplicateChecker(history_folder=history_folder)
                duplicate_result = duplicate_checker.check_invoice_file(output_folder)
                
                # 重複チェック結果のサマリーを表示
                if duplicate_result.get('success'):
                    print("\n" + "=" * 70)
                    print("  【二重払い防止チェック結果サマリー】")
                    print("=" * 70)
                    
                    total = duplicate_result.get('total_documents', 0)
                    errors = duplicate_result.get('exact_duplicate_count', 0)
                    alerts = duplicate_result.get('similar_duplicate_count', 0)
                    normal = total - errors - alerts
                    
                    print(f"  請求書: 正常 {normal}件 / "
                          f"エラー {errors}件 / "
                          f"アラート {alerts}件 / "
                          f"合計 {total}件")
                    
                    if errors > 0:
                        print(f"\n  ⚠️ エラー: {errors}件の請求書で同一請求書番号が検出されました")
                        print(f"     → 詳細は {duplicate_result.get('errors_output_path')} を確認してください")
                    
                    if alerts > 0:
                        print(f"\n  ⚠️ アラート: {alerts}件の請求書で類似データが検出されました")
                        print(f"     → 発行者名・請求日・請求金額が一致する履歴があります")
                        print(f"     → 詳細は {duplicate_result.get('errors_output_path')} を確認してください")
                    
                    if errors == 0 and alerts == 0:
                        print(f"\n  ✓ 重複なし: すべての請求書が正常です")
                    
                    print("=" * 70 + "\n")
        else:
            print("\n処理するファイルがありませんでした。")
    
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_history_export():
    """過去実績をCSVで出力"""
    history_folder = 'history'
    csv_folder = 'audit'
    
    try:
        exporter = HistoryExporter(history_folder=history_folder)
        result = exporter.export_to_csv(output_folder=csv_folder)
        
        if result.get('success'):
            print("\n" + "=" * 70)
            print("  【過去実績エクスポート完了】")
            print("=" * 70)
            print(f"  ✓ CSVファイル: {result.get('csv_filename')}")
            print(f"  ✓ 総レコード数: {result.get('total_records')}件")
            print(f"  ✓ 出力先: {result.get('csv_path')}")
            print("=" * 70 + "\n")
        else:
            print(f"\nエラー: {result.get('message', '不明なエラー')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """メイン処理"""
    display_header()
    
    # 処理モードを選択
    mode = select_mode()
    
    if mode == 'ocr':
        run_ocr_processing()
    elif mode == 'export':
        run_history_export()

if __name__ == "__main__":
    main()