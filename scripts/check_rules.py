"""Kiểm tra schema luật và dấu hiệu nội dung bị cấm; cần duyệt thủ công nguồn."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"id", "nếu", "thì", "nguon", "ghi_chu"}


def validate_rules(document: object) -> list[str]:
    """Trả lỗi cấu trúc/nguồn rỗng/dấu hiệu thuốc và liều, không thẩm định tri thức."""
    errors = []
    if not isinstance(document, dict) or not isinstance(document.get("rules"), list):
        return ["Cần đối tượng chứa danh sách rules."]
    seen = set()
    for index, rule in enumerate(document["rules"]):
        prefix = f"Luật {index + 1}"
        if not isinstance(rule, dict) or set(rule) != REQUIRED:
            errors.append(f"{prefix}: cần đúng các trường {sorted(REQUIRED)}.")
            continue
        for key in ["id", "thì", "nguon"]:
            if not isinstance(rule[key], str) or not rule[key].strip():
                errors.append(f"{prefix}: {key} phải là chuỗi không rỗng.")
        if isinstance(rule["id"], str):
            if rule["id"] in seen:
                errors.append(f"{prefix}: id trùng.")
            seen.add(rule["id"])
        conditions = rule["nếu"]
        if not isinstance(conditions, list) or not conditions or any(
            not isinstance(value, str) or not value.strip() for value in conditions
        ):
            errors.append(f"{prefix}: nếu phải là danh sách sự kiện không rỗng.")
        if not isinstance(rule["ghi_chu"], str):
            errors.append(f"{prefix}: ghi_chu phải là chuỗi.")
        # Quét cả nguồn và ghi chú; cố ý bảo thủ, không thay thế người duyệt.
        content = json.dumps(rule, ensure_ascii=False).lower().replace("đ", "d")
        content = "".join(c for c in unicodedata.normalize("NFD", content)
                          if unicodedata.category(c) != "Mn")
        # "tài liệu" mất dấu thành "tai lieu", dễ bị quét nhầm từ "liều".
        content = content.replace("tai lieu", "tailieu")
        if re.search(r"\b(?:thuoc|hoat[ _-]*chat|lieu|pesticide|fungicide|herbicide|insecticide)\b", content):
            errors.append(f"{prefix}: có dấu hiệu đề cập thuốc/hoạt chất/liều.")
        if re.search(r"\d+(?:[.,]\d+)?\s*(?:mg|ml|kg|g|l|cc|lit|%|wp|ec|sc|wg)(?!\w)", content):
            errors.append(f"{prefix}: có dấu hiệu đơn vị liều hoặc dạng chế phẩm.")
    return errors


def main() -> None:
    """Kiểm tra file được chọn; danh sách rỗng hợp lệ về schema nhưng chưa đạt đồ án."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "src/rules/rules.json")
    args = parser.parse_args()
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Không đọc được luật: {error}\n")
    errors = validate_rules(document)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"Schema hợp lệ: {len(document['rules'])} luật. Vẫn cần duyệt nội dung và nguồn.")
    if len(document["rules"]) < 20:
        print("Chưa đủ ít nhất 20 luật thật cho đồ án.")


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
