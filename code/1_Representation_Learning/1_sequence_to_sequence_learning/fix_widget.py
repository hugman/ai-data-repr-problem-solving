#!/usr/bin/env python3
import sys
import json
import os

def main():
    if len(sys.argv) < 3:
        print("사용법: python fix_widgets_simple.py <입력.ipynb> <출력.ipynb>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"[ERROR] 입력 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)

    # 노트북 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        try:
            notebook_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 실패: {e}")
            sys.exit(1)

    changed = False

    # 1) 최상위 metadata.widgets 처리
    top_meta = notebook_data.get("metadata", {})
    widgets_meta = top_meta.get("widgets")
    if isinstance(widgets_meta, dict):
        if "state" not in widgets_meta:
            del top_meta["widgets"]
            changed = True

    # 2) 각 셀의 metadata.widgets 처리
    cells = notebook_data.get("cells", [])
    for idx, cell in enumerate(cells):
        cell_meta = cell.get("metadata", {})
        widgets_in_cell = cell_meta.get("widgets")
        if isinstance(widgets_in_cell, dict):
            if "state" not in widgets_in_cell:
                del cell_meta["widgets"]
                changed = True

    # 수정된 데이터를 출력 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(notebook_data, out, ensure_ascii=False, indent=1)

    if changed:
        print(f"[INFO] 위젯 메타데이터를 수정했습니다. 결과: {output_file}")
    else:
        print(f"[INFO] 수정할 항목이 없었습니다. 결과: {output_file}")

if __name__ == "__main__":
    main()
