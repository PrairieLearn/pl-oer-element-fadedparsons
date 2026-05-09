from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import prairielearn as pl


@dataclass(frozen=True, slots=True)
class AnswerSpec:
    answers_name: str
    file_name: str
    function_name: str
    description: str
    weight: int
    cases: tuple[tuple[Any, ...], ...]


ANSWER_SPECS = (
    AnswerSpec(
        answers_name="focused",
        file_name="focused.py",
        function_name="stay_focused",
        description="returns an encouragement string",
        weight=4,
        cases=(("Bobby",), ("Kiara",)),
    ),
    AnswerSpec(
        answers_name="average",
        file_name="average.py",
        function_name="average",
        description="returns the sum of a list of numbers",
        weight=4,
        cases=(
            ([],),
            ([1],),
            ([4, -2, 3, 7],),
        ),
    ),
)


def grade(data: dict[str, Any]):
    params = data.setdefault("params", {})
    partial_scores = data.setdefault("partial_scores", {})
    submitted_answers = data.get("submitted_answers", {})

    graded_specs = params["graded_specs"] = [] # reset graded specs list from previous runs

    for spec in ANSWER_SPECS:
        reference_fn = load_reference_answer(data, spec)
        score, feedback = score_submission(
            submitted_answers.get(spec.answers_name, ""),
            reference_fn,
            spec.cases,
            spec.answers_name,
            spec.function_name,
        )
        partial_scores[spec.answers_name] = {
            "score": score,
            "feedback": feedback,
        }
        status_key, status_value = pl.determine_score_params(score)
        graded_specs.append(
            {
                "answers_name": spec.answers_name,
                "description": spec.description,
                "score": score,
                "status_key": status_key,
                "status_value": status_value,
                "feedback": feedback or f"All checks passed for `{spec.answers_name}`.",
            }
        )

    pl.set_weighted_score_data(data)
    return data


def load_reference_answer(data: dict[str, Any], spec: AnswerSpec) -> callable:
    return getattr(
        load_namespace(
            data["correct_answers"][spec.answers_name], filename=spec.function_name
        ),
        spec.function_name,
    )


def load_namespace(source: str, *, filename: str) -> SimpleNamespace:
    namespace: dict[str, object] = {}
    exec(compile(source, filename, "exec"), namespace)
    exported = {
        name: value for name, value in namespace.items() if not name.startswith("__")
    }
    return SimpleNamespace(**exported)


def score_submission(
    source: str,
    reference_fn,
    cases: tuple[tuple[Any, ...], ...],
    answers_name: str,
    function_name: str,
) -> tuple[float, str | None]:
    if not source:
        return 0.0, f"Missing submitted answer for `{answers_name}`."

    try:
        namespace = load_namespace(source, filename=f"<submitted {answers_name}>")
    except Exception as exc:
        return 0.0, f"Could not execute `{answers_name}`: {exc}"

    student_fn = getattr(namespace, function_name, None)
    if student_fn is None:
        return (
            0.0,
            f"Submitted code for `{answers_name}` does not define `{function_name}`.",
        )

    correct = 0
    total = 0
    for case in cases:
        total += 1
        try:
            user_val = student_fn(*case)
        except Exception:
            continue
        if user_val == reference_fn(*case):
            correct += 1

    if total == 0:
        return 0.0, f"No test cases were available for `{answers_name}`."

    score = correct / total
    if score == 1.0:
        return score, None
    return score, f"{correct} of {total} checks passed for `{answers_name}`."
