"""
データ前処理モジュール - ITガバナンス実態調査対応版
"""
import pandas as pd
import numpy as np
import json
from modules.util import load_yaml, save_json


class DataPreprocessor:
    """サンプルデータを前処理するクラス"""
    
    def __init__(self, config_path='config/config.yaml', questions_path='config/survey_questions.yaml'):
        """初期化"""
        self.config = load_yaml(config_path)
        self.questions = load_yaml(questions_path)
        self.preprocessing_log = {
            'original_shape': None,
            'processed_shape': None,
            'transformations': [],
            'column_mapping': {}
        }
    
    def load_raw_data(self, filepath=None):
        """生データを読み込む
        
        Args:
            filepath (str): 読み込むファイルパス
        
        Returns:
            pd.DataFrame: 読み込んだデータ
        """
        if filepath is None:
            filepath = self.config['paths']['raw_data']
        
        print(f"\n生データを読み込み中: {filepath}")
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        self.preprocessing_log['original_shape'] = df.shape
        print(f"✓ 読み込み完了: {df.shape[0]}行 × {df.shape[1]}列")
        
        return df
    
    def preprocess(self, df):
        """データを前処理する
        
        Args:
            df (pd.DataFrame): 生データ
        
        Returns:
            pd.DataFrame: 前処理済みデータ
        """
        print("\n" + "=" * 80)
        print("  データ前処理を開始")
        print("=" * 80)
        
        # 処理済みデータを格納する辞書
        processed_data = {}
        
        # 1. 回答者IDはそのまま保持
        processed_data['回答者ID'] = df['回答者ID']
        
        # 2. 基本情報の処理
        print("\n[1/5] 基本情報の処理中...")
        processed_data.update(self._process_basic_info(df))
        
        # 3. 複数選択質問のバイナリ変換
        print("\n[2/5] 複数選択質問のバイナリ変換中...")
        processed_data.update(self._process_multiple_choice(df))
        
        # 4. 単一選択質問のOne-Hot Encoding
        print("\n[3/5] 単一選択質問のOne-Hot Encoding中...")
        processed_data.update(self._process_single_choice(df))
        
        # 5. 優先順位付き複数選択の処理
        print("\n[4/5] 優先順位付き複数選択の処理中...")
        processed_data.update(self._process_priority_choice(df))
        
        # 6. テキスト項目（自由記述）の処理
        print("\n[5/5] テキスト項目の処理中...")
        processed_data.update(self._process_text_fields(df))
        
        # DataFrameに変換
        df_processed = pd.DataFrame(processed_data)
        
        self.preprocessing_log['processed_shape'] = df_processed.shape
        
        print("\n" + "=" * 80)
        print("  前処理完了")
        print("=" * 80)
        print(f"元データ: {self.preprocessing_log['original_shape'][0]}行 × {self.preprocessing_log['original_shape'][1]}列")
        print(f"処理後: {df_processed.shape[0]}行 × {df_processed.shape[1]}列")
        print(f"追加された列数: {df_processed.shape[1] - self.preprocessing_log['original_shape'][1]}")
        
        return df_processed
    
    def _process_basic_info(self, df):
        """基本情報を処理"""
        processed = {}
        
        for item in self.questions['basic_info']:
            question = item['question']
            q_type = item['type']
            q_id = item['id']
            
            if question not in df.columns:
                continue
            
            if q_type == 'text':
                if q_id == 'it_budget':
                    # IT予算は数値として保持
                    processed[question] = pd.to_numeric(df[question], errors='coerce').fillna(0)
                    self.preprocessing_log['transformations'].append({
                        'column': question,
                        'method': 'numeric_conversion',
                        'description': '数値として変換、欠損値は0'
                    })
                elif q_id == 'department':
                    # 所属部門はLabel Encoding
                    processed[f'{question}_code'] = pd.factorize(df[question])[0]
                    self.preprocessing_log['transformations'].append({
                        'column': question,
                        'method': 'label_encoding',
                        'description': 'カテゴリをコード化'
                    })
                # その他のテキスト項目は除外（氏名など）
                
            elif q_type == 'single_choice':
                # One-Hot Encoding
                options = item['options']
                for opt in options:
                    col_name = f'{question}_{opt}'
                    processed[col_name] = (df[question] == opt).astype(int)
                
                self.preprocessing_log['transformations'].append({
                    'column': question,
                    'method': 'one_hot_encoding',
                    'num_columns': len(options)
                })
                
            elif q_type == 'multiple_choice':
                # 管掌範囲などの複数選択
                options = item['options']
                for opt in options:
                    col_name = f'{question}_{opt}'
                    processed[col_name] = df[question].apply(
                        lambda x: 1 if isinstance(x, str) and opt in x else 0
                    )
                
                self.preprocessing_log['transformations'].append({
                    'column': question,
                    'method': 'binary_encoding',
                    'num_columns': len(options)
                })
        
        print(f"  ✓ 基本情報を処理: {len(processed)}列生成")
        return processed
    
    def _process_multiple_choice(self, df):
        """複数選択質問をバイナリ変換"""
        processed = {}
        total_columns = 0
        
        sections = [
            'section1_tech_adoption',
            'section2_security',
            'section3_data_handling',
            'section4_change_trouble',
            'section5_budget',
            'section6_vendor',
            'section7_others'
        ]
        
        for section_name in sections:
            if section_name not in self.questions:
                continue
            
            for q in self.questions[section_name]:
                if q['type'] != 'multiple_choice':
                    continue
                
                question = q['question']
                if question not in df.columns:
                    continue
                
                options = q['options']
                
                for opt in options:
                    col_name = f'{question}_{opt}'
                    processed[col_name] = df[question].apply(
                        lambda x: 1 if isinstance(x, str) and opt in x else 0
                    )
                    total_columns += 1
                
                self.preprocessing_log['transformations'].append({
                    'column': question,
                    'method': 'binary_encoding',
                    'num_columns': len(options)
                })
        
        print(f"  ✓ 複数選択質問を変換: {total_columns}列生成")
        return processed
    
    def _process_single_choice(self, df):
        """単一選択質問をOne-Hot Encoding"""
        processed = {}
        total_columns = 0
        
        sections = [
            'section1_tech_adoption',
            'section2_security',
            'section3_data_handling',
            'section4_change_trouble',
            'section5_budget',
            'section6_vendor',
            'section7_others'
        ]
        
        for section_name in sections:
            if section_name not in self.questions:
                continue
            
            for q in self.questions[section_name]:
                if q['type'] != 'single_choice':
                    continue
                
                question = q['question']
                if question not in df.columns:
                    continue
                
                options = q['options']
                
                for opt in options:
                    col_name = f'{question}_{opt}'
                    processed[col_name] = (df[question] == opt).astype(int)
                    total_columns += 1
                
                self.preprocessing_log['transformations'].append({
                    'column': question,
                    'method': 'one_hot_encoding',
                    'num_columns': len(options)
                })
        
        print(f"  ✓ 単一選択質問を変換: {total_columns}列生成")
        return processed
    
    def _process_priority_choice(self, df):
        """優先順位付き複数選択を処理"""
        processed = {}
        total_columns = 0
        
        sections = [
            'section1_tech_adoption',
            'section6_vendor'
        ]
        
        for section_name in sections:
            if section_name not in self.questions:
                continue
            
            for q in self.questions[section_name]:
                if q['type'] != 'multiple_choice_with_priority':
                    continue
                
                question = q['question']
                if question not in df.columns:
                    continue
                
                options = q['options']
                
                for opt in options:
                    # 選択有無（バイナリ）
                    col_name_binary = f'{question}_{opt}_選択'
                    processed[col_name_binary] = df[question].apply(
                        lambda x: 1 if isinstance(x, str) and opt in x else 0
                    )
                    
                    # 優先順位（数値、選択されていない場合は0）
                    col_name_priority = f'{question}_{opt}_順位'
                    processed[col_name_priority] = df[question].apply(
                        lambda x: self._extract_priority(x, opt) if isinstance(x, str) else 0
                    )
                    
                    total_columns += 2
                
                self.preprocessing_log['transformations'].append({
                    'column': question,
                    'method': 'priority_encoding',
                    'num_columns': len(options) * 2,
                    'description': '選択有無と順位の両方を保持'
                })
        
        print(f"  ✓ 優先順位付き質問を変換: {total_columns}列生成")
        return processed
    
    def _extract_priority(self, text, option):
        """テキストから優先順位を抽出
        
        例: "コスト(1)、使いやすさ(2)" から "コスト" の優先順位 1 を抽出
        """
        if not isinstance(text, str):
            return 0
        
        # 選択肢を含む部分を探す
        items = text.split('、')
        for item in items:
            if option in item:
                # (数字) の部分を抽出
                import re
                match = re.search(r'\((\d+)\)', item)
                if match:
                    return int(match.group(1))
        return 0
    
    def _process_text_fields(self, df):
        """テキスト項目（自由記述）を処理"""
        processed = {}
        
        # 自由記述は除外または簡易処理
        # セクション7 Q4（自由意見）は除外
        
        # 必要に応じて、自由記述の文字数などを特徴量にすることも可能
        for section_name in ['section7_others']:
            if section_name not in self.questions:
                continue
            
            for q in self.questions[section_name]:
                if q['type'] == 'text' and q['id'] == 's7_q4':
                    question = q['question']
                    if question in df.columns:
                        # 自由記述の有無をフラグ化
                        processed[f'{question}_記入あり'] = df[question].apply(
                            lambda x: 1 if isinstance(x, str) and len(x.strip()) > 0 else 0
                        )
                        
                        self.preprocessing_log['transformations'].append({
                            'column': question,
                            'method': 'text_flag',
                            'description': '記入有無をフラグ化'
                        })
        
        print(f"  ✓ テキスト項目を処理: {len(processed)}列生成")
        return processed
    
    def save_preprocessed_data(self, df, filepath=None):
        """前処理済みデータを保存
        
        Args:
            df (pd.DataFrame): 前処理済みデータ
            filepath (str): 保存先ファイルパス
        """
        if filepath is None:
            filepath = self.config['paths']['preprocessed_data']
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\n✓ 前処理済みデータを保存: {filepath}")
    
    def save_preprocessing_report(self, filepath=None):
        """前処理レポートを保存
        
        Args:
            filepath (str): 保存先ファイルパス
        """
        if filepath is None:
            filepath = self.config['paths']['preprocessing_report']
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        save_json(self.preprocessing_log, filepath)
        print(f"✓ 前処理レポートを保存: {filepath}")
    
    def print_summary(self, df_processed):
        """前処理結果のサマリーを表示
        
        Args:
            df_processed (pd.DataFrame): 前処理済みデータ
        """
        print("\n" + "=" * 80)
        print("  前処理結果サマリー")
        print("=" * 80)
        
        print(f"\n【データ形状】")
        print(f"  行数: {df_processed.shape[0]}件")
        print(f"  列数: {df_processed.shape[1]}列")
        
        print(f"\n【変換サマリー】")
        method_counts = {}
        for trans in self.preprocessing_log['transformations']:
            method = trans['method']
            method_counts[method] = method_counts.get(method, 0) + 1
        
        for method, count in method_counts.items():
            print(f"  {method}: {count}項目")
        
        print(f"\n【列名サンプル（最初の20列）】")
        for i, col in enumerate(df_processed.columns[:20], 1):
            print(f"  {i:2d}. {col}")
        
        if len(df_processed.columns) > 20:
            print(f"  ... 他 {len(df_processed.columns) - 20}列")
        
        print(f"\n【データ型】")
        dtype_counts = df_processed.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count}列")
        
        print(f"\n【欠損値】")
        missing = df_processed.isnull().sum().sum()
        print(f"  総欠損値数: {missing}")
        if missing > 0:
            print(f"  欠損値がある列数: {(df_processed.isnull().sum() > 0).sum()}")


def main():
    """メイン関数（テスト用）"""
    from modules.util import print_section
    
    print_section("データ前処理テスト")
    
    # 前処理器を初期化
    preprocessor = DataPreprocessor()
    
    # 生データを読み込み
    df_raw = preprocessor.load_raw_data()
    
    # 前処理を実行
    df_processed = preprocessor.preprocess(df_raw)
    
    # 保存
    preprocessor.save_preprocessed_data(df_processed)
    preprocessor.save_preprocessing_report()
    
    # サマリー表示
    preprocessor.print_summary(df_processed)
    
    # 先頭データを表示
    print("\n" + "=" * 80)
    print("  前処理済みデータ（先頭5行）")
    print("=" * 80)
    print(df_processed.head())


if __name__ == '__main__':
    main()
