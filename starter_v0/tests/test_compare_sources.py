
from tools.compare_sources.tool import compare_sources


def test_identical_sources():
    result = compare_sources(
        "OpenAI released a new model.",
        "OpenAI released a new model.",
    )
    assert result["similarity_score"] == 1.0
    assert len(result["common_statements"]) == 1


def test_different_sources():
    result = compare_sources(
        "OpenAI released a new model.",
        "NVIDIA announced a new GPU.",
    )
    assert len(result["unique_to_a"]) == 1
    assert len(result["unique_to_b"]) == 1


def test_empty_source():
    result = compare_sources(
        "",
        "Some valid research text.",
    )
    assert "error" in result
