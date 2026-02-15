"""
サンプルデータ生成モジュール - ITガバナンス実態調査対応版
"""
import pandas as pd
import numpy as np
import random
from modules.util import load_yaml


class DataGenerator:
    """ITガバナンス実態調査のサンプルデータを生成するクラス"""
    
    def __init__(self, config_path='config/config.yaml', questions_path='config/survey_questions.yaml'):
        """初期化"""
        self.config = load_yaml(config_path)
        self.questions = load_yaml(questions_path)
        
        # 乱数シード設定
        seed = self.config['data_generation'].get('random_seed')
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def generate(self, sample_size=None):
        """サンプルデータを生成
        
        Args:
            sample_size (int): 生成するサンプル数（Noneの場合は設定ファイルから取得）
        
        Returns:
            pd.DataFrame: 生成されたサンプルデータ
        """
        if sample_size is None:
            sample_size = self.config['data_generation']['default_sample_size']
        
        print(f"\n{sample_size}件のサンプルデータを生成中...")
        
        # データフレームを初期化
        data = []
        
        # 各回答者のデータを生成
        for i in range(sample_size):
            response = {'回答者ID': f'R{i+1:03d}'}
            
            # 基本情報を生成
            response.update(self._generate_basic_info())
            
            # 各セクションの回答を生成
            response.update(self._generate_section_responses())
            
            data.append(response)
        
        df = pd.DataFrame(data)
        
        # 統計情報を表示
        total_questions = self._count_total_questions()
        
        print(f"✓ {len(df)}件のサンプルデータを生成しました")
        print(f"  - 列数: {len(df.columns)}列")
        print(f"  - 基本情報: {len(self.questions['basic_info'])}項目")
        print(f"  - 質問数: {total_questions}問")
        
        return df
    
    def _count_total_questions(self):
        """全質問数をカウント"""
        count = 0
        for section_name in ['section1_tech_adoption', 'section2_security', 
                             'section3_data_handling', 'section4_change_trouble',
                             'section5_budget', 'section6_vendor', 'section7_others']:
            if section_name in self.questions:
                count += len(self.questions[section_name])
        return count
    
    def _generate_basic_info(self):
        """基本情報を生成"""
        info = {}
        
        for item in self.questions['basic_info']:
            q_id = item['id']
            q_type = item['type']
            question = item['question']
            
            if q_type == 'text':
                # テキスト項目は簡略化して生成
                if q_id == 'department':
                    info[question] = self._random_department_from_config()
                elif q_id == 'name_position':
                    info[question] = f"回答者{random.randint(1, 999)}"
                elif q_id == 'main_management_target':
                    info[question] = self._random_from_list(['販売管理システム', '受注プロセス', 'インフラ全般', 'セキュリティ'])
                elif q_id == 'it_budget':
                    info[question] = random.randint(100, 10000)  # 万円単位
                else:
                    info[question] = ""
                    
            elif q_type == 'single_choice':
                options = item['options']
                info[question] = random.choice(options)
                
            elif q_type == 'multiple_choice':
                options = item['options']
                num_selections = random.randint(1, min(3, len(options)))
                selected = random.sample(options, num_selections)
                info[question] = '、'.join(selected)
        
        return info
    
    def _generate_section_responses(self):
        """全セクションの回答を生成"""
        responses = {}
        
        # 各セクションを処理
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
            if section_name in self.questions:
                responses.update(self._generate_section(self.questions[section_name]))
        
        return responses
    
    def _generate_section(self, section_questions):
        """特定セクションの回答を生成"""
        responses = {}
        
        for q in section_questions:
            q_type = q['type']
            question = q['question']
            
            if q_type == 'multiple_choice':
                responses[question] = self._generate_multiple_choice(q)
            elif q_type == 'single_choice':
                responses[question] = self._generate_single_choice(q)
            elif q_type == 'multiple_choice_with_priority':
                responses[question] = self._generate_multiple_choice_with_priority(q)
            elif q_type == 'text':
                responses[question] = self._generate_text(q)
        
        return responses
    
    def _generate_multiple_choice(self, q):
        """複数選択質問の回答を生成"""
        options = q['options']
        
        # 「特に困っていない」「その他」などのネガティブ選択肢を特定
        negative_options = [opt for opt in options if any(word in opt for word in ['特に', 'その他', '不要', 'していない', 'なし', 'わからない'])]
        positive_options = [opt for opt in options if opt not in negative_options]
        
        # 80%の確率で肯定的な回答
        if random.random() < 0.8 and positive_options:
            num_selections = random.randint(1, min(4, len(positive_options)))
            selected = random.sample(positive_options, num_selections)
        else:
            # 20%はネガティブまたは少数回答
            if negative_options and random.random() < 0.5:
                selected = [random.choice(negative_options)]
            else:
                num_selections = random.randint(1, 2)
                selected = random.sample(options, min(num_selections, len(options)))
        
        return '、'.join(selected)
    
    def _generate_single_choice(self, q):
        """単一選択質問の回答を生成"""
        options = q['options']
        
        # より現実的な分布を作成（重み付け）
        if len(options) >= 3:
            # 中間的な選択肢に重みを付ける
            weights = [0.3] + [0.4 / (len(options) - 2)] * (len(options) - 2) + [0.3]
            weights = [w / sum(weights) for w in weights]  # 正規化
            return np.random.choice(options, p=weights)
        else:
            return random.choice(options)
    
    def _generate_multiple_choice_with_priority(self, q):
        """優先順位付き複数選択の回答を生成"""
        options = q['options']
        
        # 3つ選んで優先順位を付ける
        num_selections = min(3, len(options))
        selected = random.sample(options, num_selections)
        
        # 優先順位付き形式: "選択肢A(1)、選択肢B(2)、選択肢C(3)"
        prioritized = [f"{opt}({i+1})" for i, opt in enumerate(selected)]
        return '、'.join(prioritized)
    
    def _generate_text(self, q):
        """テキスト回答を生成（簡略化版）"""
        # 自由記述は空欄またはサンプルテキスト
        if random.random() < 0.3:  # 30%の確率で記入
            samples = [
                "承認プロセスを簡素化してほしい",
                "セキュリティ基準をもっとわかりやすくしてほしい",
                "他部門の成功事例を共有する場がほしい",
                "全社推奨ツールのリストがあると助かる",
                "特になし"
            ]
            return random.choice(samples)
        return ""
    
    def _random_from_list(self, items):
        """リストからランダムに選択"""
        return random.choice(items)

    def _random_department_from_config(self):
        """configのpopulation_distribution.departmentに従って部門を重み付きランダム選択"""
        dist = self.config.get('data_generation', {}).get('population_distribution', {}).get('department', {})
        if not dist:
            return random.choice(['営業部', '開発部', 'インフラ部', '企画部', '管理部'])
        names = list(dist.keys())
        weights = list(dist.values())
        return random.choices(names, weights=weights, k=1)[0]
    
    def save_to_csv(self, df, filepath=None):
        """DataFrameをCSVファイルに保存
        
        Args:
            df (pd.DataFrame): 保存するデータフレーム
            filepath (str): 保存先ファイルパス（Noneの場合は設定ファイルから取得）
        """
        if filepath is None:
            filepath = self.config['paths']['raw_data']
        
        # ディレクトリが存在しない場合は作成
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\n✓ データを保存しました: {filepath}")
    
    def print_summary(self, df):
        """生成データのサマリーを表示
        
        Args:
            df (pd.DataFrame): サンプルデータ
        """
        print("\n" + "=" * 80)
        print("  生成データのサマリー")
        print("=" * 80)
        
        # 基本情報
        print(f"\n総回答数: {len(df)}件")
        print(f"総列数: {len(df.columns)}列")
        
        # 基本情報の分布を表示
        print("\n【基本情報】")
        for item in self.questions['basic_info']:
            question = item['question']
            if question in df.columns:
                if item['type'] == 'single_choice' or item['id'] == 'department':
                    print(f"\n  {question}:")
                    value_counts = df[question].value_counts()
                    for value, count in value_counts.head(5).items():
                        percentage = (count / len(df)) * 100
                        print(f"    {value}: {count}件 ({percentage:.1f}%)")
        
        # いくつかの複数選択質問のサンプルを表示
        print("\n【主要な質問の回答状況】")
        
        # セクション4 Q1（変更管理）を表示
        section4_q1 = None
        for q in self.questions.get('section4_change_trouble', []):
            if q['id'] == 's4_q1':
                section4_q1 = q
                break
        
        if section4_q1:
            question = section4_q1['question']
            print(f"\n  {question}")
            
            # 各選択肢の出現数を集計
            all_selections = []
            for selections in df[question]:
                if pd.notna(selections) and selections:
                    all_selections.extend(selections.split('、'))
            
            from collections import Counter
            counts = Counter(all_selections)
            
            for opt in section4_q1['options']:
                count = counts.get(opt, 0)
                percentage = (count / len(df)) * 100
                print(f"    {opt}: {count}件 ({percentage:.1f}%)")


def main():
    """メイン関数（テスト用）"""
    generator = DataGenerator()
    df = generator.generate(sample_size=100)
    generator.save_to_csv(df)
    generator.print_summary(df)
    
    # 先頭データを表示
    print("\n" + "=" * 80)
    print("  先頭5件のデータプレビュー")
    print("=" * 80)
    print(df.head())


if __name__ == '__main__':
    main()
