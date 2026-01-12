from ai_lsp.domain.constraints import SuffixConstraints


def merge_suffix_constraints(constraints: list[SuffixConstraints]) -> SuffixConstraints:
    merged = SuffixConstraints()

    for c in constraints:
        merged.must_not_repeat.extend(c.must_not_repeat)
        merged.must_close.extend(c.must_close)
        merged.stop_sequences.extend(c.stop_sequences)

        merged.forbidden_newlines |= c.forbidden_newlines
        merged.confidence = max(merged.confidence, c.confidence)

    # de-dup while preserving order
    merged.stop_sequences = list(dict.fromkeys(merged.stop_sequences))

    return merged

