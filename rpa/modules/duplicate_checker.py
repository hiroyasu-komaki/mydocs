import os
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime
from modules.datetime_utils import get_jst_datetime_str


class DuplicateChecker:
    """請求書の重複チェックを行うクラス"""
    
    def __init__(self, history_folder: str = 'history'):
        """
        重複チェッカーの初期化
        
        Args:
            history_folder: 過去の請求書JSONファイルが格納されているフォルダのパス
        """
        self.history_folder = history_folder
        self.history_data = []
        
        # 履歴フォルダが存在する場合は過去データを読み込む
        if os.path.exists(history_folder):
            self._load_history_data()
    
    def _load_history_data(self):
        """historyフォルダとそのサブフォルダから全てのJSONファイルを読み込む"""
        print(f"\n履歴データを読み込み中: {self.history_folder}")
        
        json_files = []
        
        # historyフォルダとその配下を再帰的に探索
        for root, dirs, files in os.walk(self.history_folder):
            for file in files:
                if file.endswith('.json'):
                    json_path = os.path.join(root, file)
                    json_files.append(json_path)
        
        if not json_files:
            print("  履歴ファイルが見つかりません（初回実行の可能性があります）")
            return
        
        print(f"  {len(json_files)}個のJSONファイルを発見")
        
        # 各JSONファイルを読み込む
        for json_path in json_files:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # invoice形式のJSONファイルのみを処理
                if data.get('document_type') == 'invoice':
                    documents = data.get('documents', [])
                    for doc in documents:
                        # 履歴データとして保存（どのファイルから来たかも記録）
                        doc['_history_source'] = json_path
                        self.history_data.append(doc)
            except Exception as e:
                print(f"  警告: {json_path} の読み込みに失敗しました: {e}")
        
        print(f"  履歴データ読み込み完了: {len(self.history_data)}件の請求書を登録")
    
    def _normalize_value(self, value: Any) -> str:
        """値を正規化（比較用）"""
        if value is None:
            return ""
        
        # 文字列化
        str_value = str(value).strip()
        
        # 空白文字の正規化
        str_value = ' '.join(str_value.split())
        
        # 通貨記号・カンマを除去（金額比較用）
        str_value = str_value.replace('¥', '').replace('￥', '').replace(',', '').replace('円', '')
        
        return str_value
    
    def _check_exact_duplicate(self, document: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        完全一致の重複チェック（請求書番号）
        
        Args:
            document: チェック対象のドキュメント
            
        Returns:
            (重複あり/なし, 重複したドキュメントのリスト)
        """
        invoice_number = self._normalize_value(document.get('請求書番号', ''))
        
        if not invoice_number:
            # 請求書番号が空の場合はチェックをスキップ
            return False, []
        
        duplicates = []
        for hist_doc in self.history_data:
            hist_invoice_number = self._normalize_value(hist_doc.get('請求書番号', ''))
            
            if invoice_number and invoice_number == hist_invoice_number:
                duplicates.append(hist_doc)
        
        return len(duplicates) > 0, duplicates
    
    def _check_similar_duplicate(self, document: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        類似の重複チェック（発行者名 + 請求日 + 請求金額）
        
        Args:
            document: チェック対象のドキュメント
            
        Returns:
            (類似あり/なし, 類似したドキュメントのリスト)
        """
        # チェック対象の値を正規化
        issuer = self._normalize_value(document.get('発行者名', ''))
        date = self._normalize_value(document.get('請求日', ''))
        amount = self._normalize_value(document.get('請求金額', ''))
        
        # いずれかが空の場合はチェックをスキップ
        if not issuer or not date or not amount:
            return False, []
        
        similar_docs = []
        for hist_doc in self.history_data:
            hist_issuer = self._normalize_value(hist_doc.get('発行者名', ''))
            hist_date = self._normalize_value(hist_doc.get('請求日', ''))
            hist_amount = self._normalize_value(hist_doc.get('請求金額', ''))
            
            # 3つの項目が全て一致する場合
            if (issuer == hist_issuer and 
                date == hist_date and 
                amount == hist_amount):
                similar_docs.append(hist_doc)
        
        return len(similar_docs) > 0, similar_docs
    
    def check_duplicate(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        単一ドキュメントの重複チェック
        
        Args:
            document: チェック対象のドキュメント
            
        Returns:
            重複チェック結果の辞書
        """
        result = {
            'has_exact_duplicate': False,
            'has_similar_duplicate': False,
            'exact_duplicates': [],
            'similar_duplicates': []
        }
        
        # 完全一致チェック（請求書番号）
        has_exact, exact_dups = self._check_exact_duplicate(document)
        result['has_exact_duplicate'] = has_exact
        result['exact_duplicates'] = exact_dups
        
        # 類似チェック（発行者名 + 請求日 + 請求金額）
        has_similar, similar_dups = self._check_similar_duplicate(document)
        result['has_similar_duplicate'] = has_similar
        result['similar_duplicates'] = similar_dups
        
        return result
    
    def check_json_file(self, json_file_path: str, errors_output_path: str = None) -> Dict[str, Any]:
        """
        JSONファイル全体の重複チェック
        
        Args:
            json_file_path: チェック対象のJSONファイルのパス
            errors_output_path: エラー情報を出力するJSONファイルのパス
            
        Returns:
            重複チェック結果の辞書
        """
        # JSONファイルを読み込む
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doc_type = data.get('document_type')
        
        # 請求書以外はスキップ
        if doc_type != 'invoice':
            return {
                'success': True,
                'skipped': True,
                'message': f'請求書以外のドキュメントタイプ（{doc_type}）はスキップします'
            }
        
        documents = data.get('documents', [])
        total_documents = len(documents)
        exact_duplicate_count = 0
        similar_duplicate_count = 0
        
        # エラー情報を格納するリスト
        errors = []
        alerts = []
        
        # 各ドキュメントをチェック
        for idx, document in enumerate(documents):
            dup_result = self.check_duplicate(document)
            
            # 完全一致の重複がある場合（エラー）
            if dup_result['has_exact_duplicate']:
                exact_duplicate_count += 1
                
                # 重複元の情報を収集
                dup_info = []
                for dup_doc in dup_result['exact_duplicates']:
                    dup_info.append({
                        '請求書番号': dup_doc.get('請求書番号', ''),
                        '請求日': dup_doc.get('請求日', ''),
                        '請求金額': dup_doc.get('請求金額', ''),
                        '履歴ファイル': dup_doc.get('_history_source', '不明')
                    })
                
                # エラー情報を追加
                errors.append({
                    'index': idx,
                    'ファイル名': document.get('_metadata', {}).get('ファイル名', '不明'),
                    'ファイルパス': document.get('_metadata', {}).get('ファイルパス', '不明'),
                    '請求書番号': document.get('請求書番号', ''),
                    '請求日': document.get('請求日', ''),
                    '請求金額': document.get('請求金額', ''),
                    '重複理由': '同一請求書番号が履歴に存在',
                    '重複詳細': dup_info
                })
            
            # 類似の重複がある場合（アラート）
            elif dup_result['has_similar_duplicate']:
                similar_duplicate_count += 1
                
                # 類似元の情報を収集
                similar_info = []
                for sim_doc in dup_result['similar_duplicates']:
                    similar_info.append({
                        '発行者名': sim_doc.get('発行者名', ''),
                        '請求日': sim_doc.get('請求日', ''),
                        '請求金額': sim_doc.get('請求金額', ''),
                        '請求書番号': sim_doc.get('請求書番号', ''),
                        '履歴ファイル': sim_doc.get('_history_source', '不明')
                    })
                
                # アラート情報を追加
                alerts.append({
                    'index': idx,
                    'ファイル名': document.get('_metadata', {}).get('ファイル名', '不明'),
                    'ファイルパス': document.get('_metadata', {}).get('ファイルパス', '不明'),
                    '発行者名': document.get('発行者名', ''),
                    '請求日': document.get('請求日', ''),
                    '請求金額': document.get('請求金額', ''),
                    '重複理由': '発行者名・請求日・請求金額が一致',
                    '類似詳細': similar_info
                })
        
        # エラー情報をJSONファイルに出力
        if errors_output_path:
            errors_data = {
                'generated_at': get_jst_datetime_str(),
                'source_file': json_file_path,
                'total_documents': total_documents,
                'error_count': exact_duplicate_count,
                'alert_count': similar_duplicate_count,
                'errors': errors,
                'alerts': alerts
            }
            
            with open(errors_output_path, 'w', encoding='utf-8') as f:
                json.dump(errors_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'doc_type': doc_type,
            'total_documents': total_documents,
            'exact_duplicate_count': exact_duplicate_count,
            'similar_duplicate_count': similar_duplicate_count,
            'file_path': json_file_path,
            'errors_output_path': errors_output_path
        }
    
    def check_invoice_file(self, output_folder: str = 'output') -> Dict[str, Any]:
        """
        請求書JSONファイルの重複チェック
        
        Args:
            output_folder: JSONファイルが格納されているフォルダ
            
        Returns:
            重複チェック結果の辞書
        """
        invoice_file = os.path.join(output_folder, 'invoice_data.json')
        errors_file = os.path.join(output_folder, 'duplicate.errors.json')
        
        if not os.path.exists(invoice_file):
            return {
                'success': False,
                'message': f'請求書ファイルが見つかりません: {invoice_file}'
            }
        
        # 既存のエラーファイルを削除
        if os.path.exists(errors_file):
            try:
                os.remove(errors_file)
                print(f"  既存のエラーファイルを削除しました: {errors_file}")
            except Exception as e:
                print(f"  警告: エラーファイルの削除に失敗しました: {e}")
        
        print(f"\n【重複チェック】請求書ファイルをチェック中...")
        print(f"  パス: {invoice_file}")
        
        result = self.check_json_file(invoice_file, errors_output_path=errors_file)
        
        if result.get('success'):
            print(f"  ✓ 重複チェック完了")
            print(f"    - 総ドキュメント数: {result['total_documents']}")
            print(f"    - エラー（完全一致）: {result['exact_duplicate_count']}")
            print(f"    - アラート（類似）: {result['similar_duplicate_count']}")
            
            if result['exact_duplicate_count'] > 0 or result['similar_duplicate_count'] > 0:
                print(f"    - エラー詳細: {errors_file}")
        
        return result
