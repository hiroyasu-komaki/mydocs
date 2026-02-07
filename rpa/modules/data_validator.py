import os
import json
from typing import Dict, List, Tuple, Any


class DataValidator:
    """JSONデータの必須項目チェックとデータ型チェックを行うクラス"""
    
    def __init__(self, config_folder: str = 'config'):
        """
        データバリデーターの初期化
        
        Args:
            config_folder: 設定ファイルが格納されているフォルダのパス
        """
        self.config_folder = config_folder
        self.validation_configs = {}
        
        # ドキュメントタイプと設定ファイルのマッピング
        self.config_mapping = {
            'invoice': 'invoice_validation.json'
        }
        
        # 設定ファイルを読み込む
        self._load_validation_configs()
    
    def _load_validation_configs(self):
        """設定ファイルを読み込む"""
        for doc_type, config_file in self.config_mapping.items():
            config_path = os.path.join(self.config_folder, config_file)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.validation_configs[doc_type] = json.load(f)
            else:
                print(f"警告: 設定ファイルが見つかりません: {config_path}")
    
    def _check_required_fields(self, document: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        必須項目のチェック
        
        Args:
            document: チェック対象のドキュメント
            required_fields: 必須項目のリスト
            
        Returns:
            (チェック結果, エラーメッセージのリスト)
        """
        errors = []
        is_valid = True
        
        for field in required_fields:
            # _metadataフィールドは除外
            if field == '_metadata':
                continue
            
            # フィールドが存在しない、または空文字列の場合
            if field not in document or not document[field] or document[field].strip() == '':
                errors.append(f"必須項目 '{field}' が不足しています")
                is_valid = False
        
        return is_valid, errors
    
    def _check_field_type(self, value: Any, expected_type: str) -> bool:
        """
        データ型のチェック
        
        Args:
            value: チェック対象の値
            expected_type: 期待されるデータ型
            
        Returns:
            チェック結果
        """
        if value is None:
            return False
        
        # 空文字列の場合は型チェックをスキップ（必須チェックで処理）
        if isinstance(value, str) and value.strip() == '':
            return True
        
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            # 数値文字列も許容（"123"や"1,234"など）
            if isinstance(value, (int, float)):
                return True
            if isinstance(value, str):
                # カンマや円記号を除去して数値かチェック
                cleaned = value.replace(',', '').replace('円', '').replace('¥', '').replace('￥', '').strip()
                try:
                    float(cleaned)
                    return True
                except ValueError:
                    return False
            return False
        elif expected_type == 'date':
            # 日付文字列の形式チェック（簡易版）
            if isinstance(value, str):
                # 日付らしい形式を含むかチェック
                date_patterns = ['年', '月', '日', '/', '-', 'Date']
                return any(pattern in value for pattern in date_patterns)
            return False
        elif expected_type == 'email':
            if isinstance(value, str):
                return '@' in value and '.' in value.split('@')[1] if '@' in value else False
            return False
        else:
            # 未知の型の場合はTrueを返す（エラーにしない）
            return True
    
    def _check_data_types(self, document: Dict[str, Any], field_types: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        データ型のチェック
        
        Args:
            document: チェック対象のドキュメント
            field_types: フィールド名とデータ型のマッピング
            
        Returns:
            (チェック結果, エラーメッセージのリスト)
        """
        errors = []
        is_valid = True
        
        for field, expected_type in field_types.items():
            # _metadataフィールドは除外
            if field == '_metadata':
                continue
            
            # フィールドが存在する場合のみ型チェック
            if field in document:
                value = document[field]
                # 空文字列の場合は型チェックをスキップ
                if isinstance(value, str) and value.strip() == '':
                    continue
                
                if not self._check_field_type(value, expected_type):
                    errors.append(f"項目 '{field}' のデータ型が不正です（期待: {expected_type}, 実際: {type(value).__name__}）")
                    is_valid = False
        
        return is_valid, errors
    
    def validate_document(self, document: Dict[str, Any], doc_type: str) -> Tuple[bool, List[str]]:
        """
        単一ドキュメントのバリデーション
        
        Args:
            document: チェック対象のドキュメント
            doc_type: ドキュメントタイプ（invoice, po, quotation）
            
        Returns:
            (チェック結果, エラーメッセージのリスト)
        """
        if doc_type not in self.validation_configs:
            return False, [f"ドキュメントタイプ '{doc_type}' の設定が見つかりません"]
        
        config = self.validation_configs[doc_type]
        all_errors = []
        is_valid = True
        
        # 必須項目チェック
        required_fields = config.get('required_fields', [])
        required_valid, required_errors = self._check_required_fields(document, required_fields)
        all_errors.extend(required_errors)
        if not required_valid:
            is_valid = False
        
        # データ型チェック
        field_types = config.get('field_types', {})
        type_valid, type_errors = self._check_data_types(document, field_types)
        all_errors.extend(type_errors)
        if not type_valid:
            is_valid = False
        
        return is_valid, all_errors
    
    def validate_json_file(self, json_file_path: str) -> Dict[str, Any]:
        """
        JSONファイル全体のバリデーション
        
        Args:
            json_file_path: チェック対象のJSONファイルのパス
            
        Returns:
            バリデーション結果の辞書
        """
        # JSONファイルを読み込む
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doc_type = data.get('document_type')
        if not doc_type:
            print(f"エラー: ドキュメントタイプが指定されていません: {json_file_path}")
            return {'success': False, 'message': 'ドキュメントタイプが指定されていません'}
        
        if doc_type not in self.validation_configs:
            print(f"エラー: ドキュメントタイプ '{doc_type}' の設定が見つかりません")
            return {'success': False, 'message': f"ドキュメントタイプ '{doc_type}' の設定が見つかりません"}
        
        documents = data.get('documents', [])
        total_documents = len(documents)
        validated_count = 0
        invalidated_count = 0
        
        # 各ドキュメントをバリデーション
        for document in documents:
            is_valid, errors = self.validate_document(document, doc_type)
            
            # メタデータを更新
            if '_metadata' not in document:
                document['_metadata'] = {}
            
            if is_valid:
                document['_metadata']['処理ステータス'] = '良好'
                validated_count += 1
            else:
                document['_metadata']['処理ステータス'] = '要確認'
                document['_metadata']['バリデーションエラー'] = errors
                invalidated_count += 1
        
        # 更新されたデータをJSONファイルに書き戻す
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'doc_type': doc_type,
            'total_documents': total_documents,
            'validated_count': validated_count,
            'invalidated_count': invalidated_count,
            'file_path': json_file_path
        }
    
    def validate_all_json_files(self, output_folder: str = 'output') -> Dict[str, Dict[str, Any]]:
        """
        すべてのJSONファイルをバリデーション
        
        Args:
            output_folder: JSONファイルが格納されているフォルダ
            
        Returns:
            ドキュメントタイプごとのバリデーション結果の辞書
        """
        results = {}
        
        # 各ドキュメントタイプのJSONファイルを処理
        json_files = {
            'invoice': os.path.join(output_folder, 'invoice_data.json')
        }
        
        for doc_type, json_file_path in json_files.items():
            if os.path.exists(json_file_path):
                print(f"\n【{doc_type.upper()}】ファイルをバリデーション中...")
                print(f"  パス: {json_file_path}")
                
                result = self.validate_json_file(json_file_path)
                results[doc_type] = result
                
                if result.get('success'):
                    print("  ✓ バリデーション完了")
                    print(f"    - 総ドキュメント数: {result['total_documents']}")
                    print(f"    - 良好: {result['validated_count']}")
                    print(f"    - 要確認: {result['invalidated_count']}")
                else:
                    print(f"  ✗ エラー: {result.get('message', '不明なエラー')}")
            else:
                print(f"\n【{doc_type.upper()}】ファイルが見つかりません: {json_file_path}")
                results[doc_type] = {'success': False, 'message': 'ファイルが見つかりません'}
        
        return results
