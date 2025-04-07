#!/usr/bin/env python3
import json
import sys
import os

def check_widgets(notebook_path):
    if not os.path.isfile(notebook_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {notebook_path}")
        return

    # ipynb(=JSON) 읽기
    with open(notebook_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 실패: {notebook_path}\n{e}")
            return

    # 1) 노트북 전체(최상위) metadata 확인
    top_level_metadata = data.get("metadata", {})
    widgets_meta = top_level_metadata.get("widgets")
    if widgets_meta is not None:
        # widgets 키는 있는데 state 키가 없는지 확인
        if isinstance(widgets_meta, dict) and "state" not in widgets_meta:
            print(f"[WARN] 최상위 metadata.widgets에서 'state' 키가 누락됨: {notebook_path}")
        else:
            print(f"[INFO] 최상위 metadata.widgets에는 문제가 없어 보입니다: {notebook_path}")
    else:
        print(f"[INFO] 최상위 metadata에 widgets가 없습니다: {notebook_path}")

    # 2) 각 셀별로 metadata.widgets 확인
    cells = data.get("cells", [])
    for idx, cell in enumerate(cells):
        cell_meta = cell.get("metadata", {})
        cell_widgets = cell_meta.get("widgets")
        if cell_widgets is not None:
            # 셀 메타데이터의 widgets가 있지만 state가 누락된 경우
            if isinstance(cell_widgets, dict) and "state" not in cell_widgets:
                print(f"[WARN] 셀 #{idx} (0-based) metadata.widgets에서 'state' 누락: {notebook_path}")
            else:
                print(f"[INFO] 셀 #{idx} metadata.widgets에는 문제가 없어 보입니다.")

def main():
    if len(sys.argv) < 2:
        print("사용법: python check_widgets.py <notebook.ipynb> [다른노트북.ipynb ...]")
        sys.exit(1)

    # 여러 개의 ipynb 파일도 인자로 받을 수 있도록
    for nb_file in sys.argv[1:]:
        check_widgets(nb_file)

if __name__ == "__main__":
    main()
