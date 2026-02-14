"""
ユーティリティ関数
"""
import yaml
import json
from pathlib import Path


def load_yaml(filepath):
    """YAMLファイルを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_json(data, filepath):
    """JSON形式でデータを保存"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath):
    """JSONファイルを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_dir(dirpath):
    """ディレクトリが存在しない場合は作成"""
    Path(dirpath).mkdir(parents=True, exist_ok=True)


def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step(step_num, title):
    """ステップタイトルを表示"""
    print(f"\n[Step {step_num}] {title}")
    print("-" * 80)
