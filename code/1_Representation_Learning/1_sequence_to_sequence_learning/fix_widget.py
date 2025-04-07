#!/usr/bin/env python3
import json
import sys
import os

def fix_widgets_in_notebook(notebook_data, remove_instead_of_add=True):
    """
    주어진 notebook_data(파이썬 dict)에서 widgets 문제를 해결한다.
    
    - remove_instead_of_add=True: 'state' 키가 없으면 widgets 전체를 제거
    - remove_instead_of_add=False: 'state' 키가 없으면 빈 dict 로 추가 -> {"state": {}}
    
    반환값:
      - (fixed_data, changed_something)
    """
    changed_something = False
    # 최상위 metadata
    if "metadata" in notebook_data:
        top_meta = notebook_data["metadata"]
        if isinstance(top_meta, dict) and "widgets" in top_meta:
            widgets = top_meta["widgets"]
            # widgets가 dict일 때 'state' 키가 없으면 처리
            if isinstance(widgets, dict) and "state" not in widgets:
                if remove_instead_of_add:
                    del top_meta["widgets"]
                    changed_something = True
                else:
                    top_meta["widgets"]["state"] = {}
                    changed_something = True

    # 각 셀의 metadata
    for idx, cell in enumerate(notebook_data.get("cells", [])):
        cell_meta = cell.get("metadata", {})
        if isinstance(cell_meta, dict) and "widgets" in cell_meta:
            widgets = cell_meta["widgets"]
            # widgets가 dict일 때 'state' 키가 없으면 처리
            if isinstance(widgets, dict) and "state" not in widgets:
                if remove_instead_of_add:
                    del cell_meta["widgets"]
                    changed_something = True
                else:
                    cell_meta["widgets"]["state"] = {}
                    changed_something = True

    return notebook_data, changed_something


def process_file(input_path, output_path=None, remove_instead_of_add=True):
    """
    input_path로부터 노트북 파일을 읽어 widgets 메타데이터를 수정하고,
    output_path에 결과를 기록한다 (output_path가 없으면 덮어쓴다).
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 실패: {input_path} -> {e}")
            return

    fixed_data, changed = fix_widgets_in_notebook(data, remove_instead_of_add=remove_instead_of_add)
    if not changed:
        print(f"[INFO] 변경 사항 없음: {input_path}")
        return
    else:
        # 출력 경로 지정
        if output_path is None:
            output_path = input_path  # 덮어쓰기

        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=1)
        
        if input_path == output_path:
            print(f"[FIXED] {input_path} 파일이 수정되었습니다.")
        else:
            print(f"[FIXED] {input_path} -> {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Colab 노트북 'metadata.widgets' 문제 자동 수정 스크립트")
    parser.add_argument("notebooks", nargs="+", help="하나 이상의 ipynb 파일 경로")
    parser.add_argument("--remove", action="store_true",
                        help="widgets['state']가 없으면 widgets를 완전히 제거(기본 동작)")
    parser.add_argument("--add-state", action="store_true",
                        help="widgets['state']가 없으면 빈 dict로 추가")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="출력 디렉토리를 지정하면, 해당 디렉토리에 수정된 파일을 저장 (기존 이름 유지)")
    args = parser.parse_args()

    # 우선순위: --add-state가 있으면 remove_instead_of_add=False
    #           기본은 remove_instead_of_add=True
    remove_instead_of_add = not args.add_state

    for nb_file in args.notebooks:
        # 출력 디렉토리가 주어지면, 파일명만 따서 그 디렉토리 하위로
        if args.output_dir:
            base_name = os.path.basename(nb_file)
            output_path = os.path.join(args.output_dir, base_name)
        else:
            output_path = None

        process_file(nb_file, output_path=output_path,
                     remove_instead_of_add=remove_instead_of_add)


if __name__ == "__main__":
    main()
