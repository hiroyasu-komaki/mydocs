import os
import json
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta


class HistoryExporter:
    """過去実績をCSV形式でエクスポートするクラス"""
    
    def __init__(self, history_folder: str = 'history'):
        """
        履歴エクスポーターの初期化
        
        Args:
            history_folder: 過去の請求書JSONファイルが格納されているフォルダのパス
        """
        self.history_folder = history_folder
    
    def _escape_csv_value(self, value: Any) -> str:
        """
        CSVの値をエスケープ（シングルクォートが含まれている場合はダブルクォートで囲む）
        
        Args:
            value: エスケープする値
            
        Returns:
            エスケープされた文字列
        """
        if value is None:
            return ""
        
        str_value = str(value)
        
        # シングルクォート、カンマ、改行が含まれている場合はダブルクォートで囲む
        needs_quotes = ("'" in str_value or ',' in str_value or '\n' in str_value or '\r' in str_value)
        
        if needs_quotes:
            # 既存のダブルクォートをエスケープ（""に変換）
            str_value = str_value.replace('"', '""')
            # ダブルクォートで囲む
            return f'"{str_value}"'
        
        return str_value
    
    def _flatten_document(self, document: Dict[str, Any], source_file: str) -> Dict[str, Any]:
        """
        ドキュメントをフラット化（メタデータも含める）
        
        Args:
            document: ドキュメント辞書
            source_file: ソースファイルのパス
            
        Returns:
            フラット化された辞書
        """
        flat = {}
        
        # 通常のフィールドをコピー
        for key, value in document.items():
            if key != '_metadata':
                flat[key] = value
        
        # メタデータを展開
        metadata = document.get('_metadata', {})
        flat['ファイル名'] = metadata.get('ファイル名', '')
        flat['ファイルパス'] = metadata.get('ファイルパス', '')
        flat['処理日時'] = metadata.get('処理日時', '')
        flat['処理ステータス'] = metadata.get('処理ステータス', '')
        
        # ソースファイル情報を追加
        flat['履歴ファイル'] = source_file
        
        return flat
    
    def export_to_csv(self, output_folder: str = 'audit') -> Dict[str, Any]:
        """
        historyフォルダ内の全請求書JSONを読み込み、CSVファイルに出力
        
        Args:
            output_folder: CSVファイルの出力先フォルダ
            
        Returns:
            エクスポート結果の辞書
        """
        if not os.path.exists(self.history_folder):
            return {
                'success': False,
                'message': f'履歴フォルダが見つかりません: {self.history_folder}'
            }
        
        print(f"\n履歴データを読み込み中: {self.history_folder}")
        
        # 全JSONファイルを収集
        all_documents = []
        json_files = []
        
        for root, dirs, files in os.walk(self.history_folder):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    json_files.append(json_path)
                    
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # invoice形式のJSONファイルのみを処理
                        if data.get('document_type') == 'invoice':
                            documents = data.get('documents', [])
                            for doc in documents:
                                # 処理日時を取得（ソート用）
                                metadata = doc.get('_metadata', {})
                                processed_time = metadata.get('処理日時', '')
                                
                                # フラット化して追加
                                flat_doc = self._flatten_document(doc, json_path)
                                flat_doc['_sort_key'] = processed_time
                                all_documents.append(flat_doc)
                    except Exception as e:
                        print(f"  警告: {json_path} の読み込みに失敗しました: {e}")
        
        if not all_documents:
            return {
                'success': False,
                'message': '履歴データが見つかりませんでした'
            }
        
        print(f"  {len(json_files)}個のJSONファイルから {len(all_documents)}件の請求書を発見")
        
        # 処理日時でソート
        all_documents.sort(key=lambda x: x.get('_sort_key', ''))
        
        # 出力フォルダを作成
        os.makedirs(output_folder, exist_ok=True)
        
        # CSVファイル名を生成（現在の日時を含む、JST）
        jst = timezone(timedelta(hours=9))
        timestamp = datetime.now(jst).strftime('%Y%m%d_%H%M%S')
        csv_filename = f'invoice_history_{timestamp}.csv'
        csv_path = os.path.join(output_folder, csv_filename)
        
        # 全ドキュメントからカラム名を取得（順序を保持）
        if all_documents:
            # 最初のドキュメントからキーを取得（_sort_keyを除く）
            columns = [key for key in all_documents[0].keys() if key != '_sort_key']
            
            # 固定の順序で並べ替え（重要なフィールドを先頭に）
            priority_columns = [
                '処理日時', 'ファイル名', '請求日', '請求書番号', '登録番号',
                '宛先会社名', '請求金額', '小計', '消費税', '合計',
                '振込期日', '発行者名', '電話番号', 'メールアドレス',
                'ファイルパス', '処理ステータス', '履歴ファイル'
            ]
            
            # 優先カラムを先に、残りを後ろに
            ordered_columns = []
            for col in priority_columns:
                if col in columns:
                    ordered_columns.append(col)
                    columns.remove(col)
            
            # 残りのカラムを追加
            ordered_columns.extend(sorted(columns))
            columns = ordered_columns
        else:
            columns = []
        
        # CSVファイルに書き込み
        try:
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                # ヘッダー行を書き込み
                header_row = []
                for col in columns:
                    header_row.append(self._escape_csv_value(col))
                f.write(','.join(header_row) + '\n')
                
                # データ行を書き込み
                for doc in all_documents:
                    row = []
                    for col in columns:
                        value = doc.get(col, '')
                        # シングルクォートが含まれている場合はダブルクォートで囲む
                        escaped_value = self._escape_csv_value(value)
                        row.append(escaped_value)
                    f.write(','.join(row) + '\n')
            
            print(f"\n  ✓ CSV出力完了: {csv_filename}")
            print(f"    - 総レコード数: {len(all_documents)}")
            print(f"    - 出力先: {csv_path}")
            
            return {
                'success': True,
                'total_records': len(all_documents),
                'csv_path': csv_path,
                'csv_filename': csv_filename
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'CSVファイルの書き込みに失敗しました: {str(e)}'
            }
