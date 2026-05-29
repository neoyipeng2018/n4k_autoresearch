from __future__ import annotations

from prepare import OOSResult, passes_validation_gate


def test_validation_gate_ignores_bad_locked_oos_diagnostics_when_validation_improves() -> None:
    result = OOSResult(
        train_cagr=0.10,
        validation_cagr=0.12,
        oos_cagr=-0.20,
        benchmark_oos_cagr=0.05,
        excess_oos_cagr_vs_dbmf=-0.25,
        ruined=False,
        passed=False,
    )

    assert passes_validation_gate(result, previous_best_validation_cagr=0.10)


def test_validation_gate_rejects_ruin_nonfinite_and_nonpositive_validation() -> None:
    base = OOSResult(
        train_cagr=0.10,
        validation_cagr=0.02,
        oos_cagr=-0.20,
        benchmark_oos_cagr=0.03,
        excess_oos_cagr_vs_dbmf=-0.23,
        ruined=False,
        passed=False,
    )

    assert not passes_validation_gate(OOSResult(**(base.__dict__ | {"ruined": True})), 0.0)
    assert not passes_validation_gate(OOSResult(**(base.__dict__ | {"validation_cagr": 0.0})), 0.0)
    assert not passes_validation_gate(OOSResult(**(base.__dict__ | {"validation_cagr": float("nan")})), 0.0)
    assert passes_validation_gate(base, 0.01)
