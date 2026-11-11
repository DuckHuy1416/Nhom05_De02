"""Luật ký hiệu chỉ phục vụ test, không phải tri thức về bệnh lúa."""
import json
from pathlib import Path

import pytest

from scripts.check_rules import validate_rules
from src.rules.backward import backward
from src.rules.forward import forward

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def symbolic_rules():
    return [
        {"id": "T1", "nếu": ["A"], "thì": "B", "nguon": "fixture logic, không phải nguồn nông học",
         "ghi_chu": "Chỉ dùng kiểm thử"},
        {"id": "T2", "nếu": ["B", "D"], "thì": "C",
         "nguon": "fixture logic, không phải nguồn nông học", "ghi_chu": "Chỉ dùng kiểm thử"},
    ]


@pytest.mark.xfail(reason="chưa cài đặt", raises=NotImplementedError)
def test_forward_chain_and_all_conditions(symbolic_rules):
    assert forward({"A", "D"}, symbolic_rules) == {"A", "B", "C", "D"}
    assert forward({"A"}, symbolic_rules) == {"A", "B"}


@pytest.mark.xfail(reason="chưa cài đặt", raises=NotImplementedError)
def test_backward_proof_and_unknown(symbolic_rules):
    assert backward("C", {"A", "D"}, symbolic_rules, lambda question: None) is True
    assert backward("C", {"A"}, symbolic_rules, lambda question: None) is False
    assert backward("Z", {"A"}, symbolic_rules, lambda question: None) is False


def test_repository_rules_schema():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    assert validate_rules(document) == []


@pytest.mark.xfail(reason="chưa cài đặt", raises=AssertionError)
def test_at_least_20_real_rules():
    document = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))
    assert len(document["rules"]) >= 20


def test_validator_accepts_symbolic_fixture(symbolic_rules):
    assert validate_rules({"rules": symbolic_rules}) == []


@pytest.mark.parametrize("change", [
    {"nguon": ""}, {"nguon": None}, {"nếu": []}, {"thì": ""},
    {"ghi_chu": "tên thuốc bị cấm"}, {"ghi_chu": "liều lượng bị cấm"},
    {"ghi_chu": "5 ml/l"}, {"ghi_chu": "2 g mỗi lít"}, {"ghi_chu": "5%"},
])
def test_validator_rejects_invalid_or_prohibited(change, symbolic_rules):
    rule = {**symbolic_rules[0], **change}
    assert validate_rules({"rules": [rule]})


def test_validator_rejects_missing_source_and_duplicate_id(symbolic_rules):
    rule = dict(symbolic_rules[0])
    del rule["nguon"]
    assert validate_rules({"rules": [rule]})
    assert validate_rules({"rules": [symbolic_rules[0], symbolic_rules[0]]})
