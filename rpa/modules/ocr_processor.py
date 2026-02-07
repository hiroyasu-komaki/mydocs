import os
import re
import yaml
import pandas as pd
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import List, Dict, Tuple
import io
import subprocess
from datetime import datetime
from modules.datetime_utils import get_jst_datetime_str

class OCRProcessor:
    def __init__(self, config_path: str):
        """
        OCRプロセッサの初期化
        
        Args:
            config_path: YAML設定ファイルのパス
        """
        # Tesseractの設定
        self._setup_tesseract()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # サポートするドキュメントタイプ
        self.document_types = ['invoice']
    
    def _setup_tesseract(self):
        """Tesseractの環境変数とパスを設定"""
        # tessdataのパスを探す
        possible_paths = [
            '/opt/homebrew/share/tessdata',  # Apple Silicon Mac
            '/usr/local/share/tessdata',      # Intel Mac
            '/usr/share/tessdata',            # Linux
            'C:\\Program Files\\Tesseract-OCR\\tessdata',  # Windows
        ]
        
        tessdata_path = None
        for path in possible_paths:
            if os.path.exists(path):
                tessdata_path = path
                break
        
        if tessdata_path:
            os.environ['TESSDATA_PREFIX'] = tessdata_path
            print(f"Tesseract data path: {tessdata_path}")
        
        # 利用可能な言語を確認
        try:
            result = subprocess.run(['tesseract', '--list-langs'], 
                                  capture_output=True, text=True)
            if 'jpn' not in result.stdout:
                print("警告: 日本語データ(jpn)が見つかりません")
                print("以下のコマンドでインストールしてください:")
                print("  Mac: brew install tesseract-lang")
                print("  Windows: Tesseractインストール時に日本語を選択")
        except Exception as e:
            print(f"Tesseractの確認中にエラー: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        PDFファイルからテキストを抽出（テキストベース優先、必要に応じてOCR）
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            抽出されたテキスト
        """
        print(f"  Processing: {os.path.basename(pdf_path)}")
        
        # PDFを開く
        pdf_document = fitz.open(pdf_path)
        
        all_text = ""
        
        for page_num in range(len(pdf_document)):
            print(f"    Page {page_num + 1}/{len(pdf_document)} を処理中...", end=' ')
            
            # ページを取得
            page = pdf_document[page_num]
            
            # まずテキストベースで抽出を試みる
            text = page.get_text()
            
            # テキストが十分に抽出できた場合
            if text and len(text.strip()) > 50:
                print(f"(テキスト抽出: {len(text)} 文字)")
                all_text += text + "\n"
            else:
                # テキストが少ない場合はOCRを実行
                print(f"(OCR実行中...)", end=' ')
                
                # ページを高解像度の画像に変換
                mat = fitz.Matrix(300/72, 300/72)  # 300dpi
                pix = page.get_pixmap(matrix=mat)
                
                # PixmapをPIL Imageに変換
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # OCR実行（日英両対応）
                ocr_text = pytesseract.image_to_string(image, lang='jpn+eng')
                print(f"{len(ocr_text)} 文字)")
                all_text += ocr_text + "\n"
        
        pdf_document.close()
        return all_text
    
    def _clean_extracted_value(self, value: str) -> str:
        """
        抽出した値から文字化け文字をクリーンアップ
        
        Args:
            value: 抽出した値
            
        Returns:
            クリーンアップされた値
        """
        if not value:
            return value
        
        # 私用領域の文字（U+E000-U+F8FF）を除去または置換
        # これらは通常、カスタムフォントで使用される文字
        import unicodedata
        
        cleaned = ""
        for char in value:
            # 私用領域の文字をチェック
            if '\ue000' <= char <= '\uf8ff':
                # 数字のような文字化けの場合は'X'に置換
                cleaned += 'X'
            else:
                cleaned += char
        
        return cleaned
    
    def extract_fields(self, text: str, doc_type: str) -> Dict[str, str]:
        """
        テキストから定義された項目を抽出
        
        Args:
            text: 抽出したテキスト
            doc_type: ドキュメントタイプ（invoice, po, quotation）
            
        Returns:
            項目名と値の辞書
        """
        extracted_data = {}
        
        # ドキュメントタイプに対応する設定を取得
        if doc_type not in self.config:
            print(f"    警告: {doc_type} の設定が見つかりません")
            return extracted_data
        
        fields = self.config[doc_type]['fields']
        
        # 改行やスペースを正規化
        normalized_text = re.sub(r'\s+', ' ', text)
        
        for field in fields:
            field_name = field['name']
            pattern = field['pattern']
            
            # 元のテキストと正規化したテキストの両方で試す
            match = re.search(pattern, text, re.MULTILINE)
            if not match:
                match = re.search(pattern, normalized_text)
            
            if match:
                # 複数のキャプチャグループがある場合、最初の非Noneグループを取得
                value = None
                for i in range(1, len(match.groups()) + 1):
                    if match.group(i) is not None:
                        value = match.group(i).strip()
                        break
                
                if value:
                    # 文字化け文字をクリーンアップ
                    cleaned_value = self._clean_extracted_value(value)
                    extracted_data[field_name] = cleaned_value
                else:
                    extracted_data[field_name] = ""
            else:
                extracted_data[field_name] = ""
        
        return extracted_data
    
    def process_folder(self, folder_path: str, doc_type: str, output_folder: str) -> Tuple[str, int]:
        """
        特定のフォルダ内のPDFファイルを処理
        
        Args:
            folder_path: PDFファイルが格納されているフォルダ
            doc_type: ドキュメントタイプ（invoice, po, quotation）
            output_folder: JSON/CSV出力先フォルダ
            
        Returns:
            (出力ファイルパス, 処理したファイル数)
        """
        # PDFファイルのリストを取得
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"  PDFファイルが見つかりませんでした。")
            return None, 0
        
        print(f"  {len(pdf_files)}個のPDFファイルを処理します。\n")
        
        # 各PDFを処理
        all_data = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            
            # テキスト抽出
            text = self.extract_text_from_pdf(pdf_path)
            
            # フィールド抽出
            data = self.extract_fields(text, doc_type)
            
            # メタデータを追加
            data['_metadata'] = {
                'ファイル名': pdf_file,
                'ファイルパス': pdf_path,
                '処理日時': get_jst_datetime_str(),
                '処理ステータス': '読み取り完了'
            }
            
            all_data.append(data)
            print(f"    ✓ 完了\n")
        
        # 出力フォルダが存在しない場合は作成
        os.makedirs(output_folder, exist_ok=True)
        
        # 出力形式を取得（デフォルトはjson）
        output_config = self.config[doc_type]['output']
        output_format = output_config.get('format', 'json')
        filename = output_config.get('filename', f'{doc_type}_data.json')
        output_path = os.path.join(output_folder, filename)
        
        if output_format == 'json':
            # JSON形式で出力
            output_data = {
                'document_type': doc_type,
                'processed_at': get_jst_datetime_str(),
                'total_documents': len(all_data),
                'documents': all_data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ JSON出力完了: {filename}")
            print(f"    - ドキュメント数: {len(all_data)}\n")
        else:
            # CSV形式で出力（後方互換性のため）
            # メタデータをフラット化
            for item in all_data:
                if '_metadata' in item:
                    metadata = item.pop('_metadata')
                    item.update(metadata)
            
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"  ✓ CSV出力完了: {filename}")
            print(f"    - 列数: {len(df.columns)}")
            print(f"    - 行数: {len(df)}\n")
        
        return output_path, len(pdf_files)
    
    def process_selected_folders(self, base_pdf_folder: str, output_folder: str, selected_types: List[str]) -> Dict[str, str]:
        """
        選択されたサブフォルダのみを処理
        
        Args:
            base_pdf_folder: PDFファイルが格納されているベースフォルダ
            output_folder: JSON/CSV出力先フォルダ
            selected_types: 処理対象のドキュメントタイプのリスト
            
        Returns:
            ドキュメントタイプごとの出力ファイルパスの辞書
        """
        results = {}
        total_files = 0
        
        print("\n" + "=" * 70)
        print("  PDF OCR処理を開始します")
        print("=" * 70 + "\n")
        
        for doc_type in selected_types:
            if doc_type not in self.document_types:
                print(f"⚠ 警告: '{doc_type}' は未対応のドキュメントタイプです。スキップします。\n")
                continue
            
            folder_path = os.path.join(base_pdf_folder, doc_type)
            
            doc_type_names = {
                'invoice': '請求書'
            }
            
            print(f"【{doc_type_names.get(doc_type, doc_type).upper()}】フォルダを処理中...")
            print(f"  パス: {folder_path}")
            
            if not os.path.exists(folder_path):
                print(f"  ⚠ フォルダが存在しません。スキップします。\n")
                continue
            
            output_path, file_count = self.process_folder(folder_path, doc_type, output_folder)
            
            if output_path:
                results[doc_type] = output_path
                total_files += file_count
        
        print("=" * 70)
        print(f"  すべての処理が完了しました")
        print(f"  処理ファイル数: {total_files}")
        print(f"  出力ファイル数: {len(results)}")
        print("=" * 70 + "\n")
        
        return results
    
    def process_all_folders(self, base_pdf_folder: str, output_folder: str) -> Dict[str, str]:
        """
        ベースフォルダ配下のすべてのサブフォルダを処理
        
        Args:
            base_pdf_folder: PDFファイルが格納されているベースフォルダ
            output_folder: JSON/CSV出力先フォルダ
            
        Returns:
            ドキュメントタイプごとの出力ファイルパスの辞書
        """
        results = {}
        total_files = 0
        
        print("\n" + "=" * 70)
        print("  PDF OCR処理を開始します")
        print("=" * 70 + "\n")
        
        for doc_type in self.document_types:
            folder_path = os.path.join(base_pdf_folder, doc_type)
            
            print(f"【{doc_type.upper()}】フォルダを処理中...")
            print(f"  パス: {folder_path}")
            
            if not os.path.exists(folder_path):
                print(f"  ⚠ フォルダが存在しません。スキップします。\n")
                continue
            
            csv_path, file_count = self.process_folder(folder_path, doc_type, output_folder)
            
            if csv_path:
                results[doc_type] = csv_path
                total_files += file_count
        
        print("=" * 70)
        print(f"  すべての処理が完了しました")
        print(f"  処理ファイル数: {total_files}")
        print(f"  出力CSV数: {len(results)}")
        print("=" * 70 + "\n")
        
        return results