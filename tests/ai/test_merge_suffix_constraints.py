from ai_lsp.ai.constraints import merge_suffix_constraints
from ai_lsp.domain.constraints import SuffixConstraints


def test_merge_suffix_constraints_deduplicates_and_preserves_order() -> None:
    c1: SuffixConstraints = SuffixConstraints(
        must_not_repeat=[")"],
        must_close=[")"],
        stop_sequences=[")", "\n"],
        forbidden_newlines=True,
        confidence=0.9,
    )

    c2: SuffixConstraints = SuffixConstraints(
        must_not_repeat=[";"],
        must_close=[],
        stop_sequences=[";"],
        forbidden_newlines=False,
        confidence=0.5,
    )

    merged: SuffixConstraints = merge_suffix_constraints([c1, c2])

    assert merged.stop_sequences == [")", "\n", ";"]
    assert merged.forbidden_newlines is True
    assert merged.confidence == 0.9
