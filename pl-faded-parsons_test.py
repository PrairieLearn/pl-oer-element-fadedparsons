import base64
import importlib
import json
import os
import sys
import types
from pathlib import Path

import pytest

ELEMENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ELEMENT_DIR))

sys.modules["chevron"] = types.SimpleNamespace(
    render=lambda _template, params, **_kwargs: json.dumps(params)
)

pl_stub = types.SimpleNamespace(
    QuestionData=dict,
    get_string_attrib=lambda element, name, default=None: element.get(name, default),
    get_boolean_attrib=lambda element, name, default=None: (
        element.get(name, str(default)).lower() in {"true", "1", "yes"}
        if element.get(name) is not None
        else default
    ),
    get_integer_attrib=lambda element, name, default=None: (
        int(element.get(name)) if element.get(name) is not None else default
    ),
    check_attribs=lambda *args, **kwargs: None,
    check_answers_names=lambda _data, *_names: None,
    add_submitted_file=lambda data, name, contents: (
        data.setdefault("submitted_answers", {})
        .setdefault("_files", [])
        .append({"name": name, "contents": contents})
    ),
    get_uuid=lambda: "test-uuid",
)
sys.modules["prairielearn"] = pl_stub

pl_faded = importlib.import_module("pl-faded-parsons")


def _base_data(panel: str = "question") -> dict:
    return {
        "panel": panel,
        "options": {"question_path": str(ELEMENT_DIR)},
        "raw_submitted_answers": {},
        "submitted_answers": {},
        "correct_answers": {},
        "format_errors": {},
        "feedback": {},
    }


def _element(markup: str, **attrs) -> str:
    attr_text = " ".join(
        f'{name.replace("_", "-")}="{value}"' for name, value in attrs.items()
    )
    return (
        f'<pl-faded-parsons answers-name="fpp" {attr_text}>{markup}</pl-faded-parsons>'
    )


def _render(element_html: str, data: dict) -> dict:
    old_cwd = os.getcwd()
    try:
        os.chdir(ELEMENT_DIR)
        return json.loads(pl_faded.render(element_html, data))
    finally:
        os.chdir(old_cwd)


def test_parse_author_markup_line_recognizes_pin_blank_and_placeholder() -> None:
    line = pl_faded._parse_author_markup_line("  return __(base case)__ #pin(2)", 1)

    assert line.raw_leading_spaces == 2
    assert line.role == "solution"
    assert line.indent == 2
    assert line.pinned is True
    assert [token.kind for token in line.tokens] == ["text", "blank"]
    assert line.tokens[1].placeholder == "base case"


def test_parse_author_markup_line_recognizes_distractors() -> None:
    line = pl_faded._parse_author_markup_line("n_less_0 = fibonacci(n) #distractor", 1)

    assert line.role == "distractor"


def test_optional_fade_markup_preserves_solution_and_placeholder() -> None:
    line = pl_faded._parse_author_markup_line("return __[b](right operand)__", 1)

    assert line.tokens[1].kind == "optional"
    assert line.tokens[1].value == "b"
    assert line.tokens[1].placeholder == "right operand"


def test_compile_code_interleaves_snippets_blanks_and_indentation() -> None:
    lines = [
        {
            "codeSnippets": ["def f():", ""],
            "blankValues": [],
            "blankPlaceholders": [],
            "indent": 0,
            "pinned": True,
        },
        {
            "codeSnippets": ["return ", ""],
            "blankValues": ["42"],
            "blankPlaceholders": ["answer"],
            "indent": 1,
            "pinned": False,
        },
    ]

    assert pl_faded._compile_code(lines) == "def f():\n    return 42"


def test_text_block_rejects_inconsistent_indentation() -> None:
    with pytest.raises(IndentationError, match="post-text line"):
        pl_faded._build_text_block("  if x:\n    return x", placement="post")


def test_build_config_rejects_legacy_and_unknown_formats() -> None:
    with pytest.raises(ValueError, match="renamed to `one-tray`"):
        pl_faded._build_config(_element("print('x')", format="no-code"), _base_data())

    with pytest.raises(ValueError, match="Unsupported format"):
        pl_faded._build_config(_element("print('x')", format="sideways"), _base_data())


def test_build_config_validates_limits_and_text_block_combinations() -> None:
    with pytest.raises(ValueError, match="max-indent-level"):
        pl_faded._build_config(
            _element("print('x')", max_indent_level="-1"),
            _base_data(),
        )

    with pytest.raises(ValueError, match="pre-text and post-text"):
        pl_faded._build_config(
            _element("<pre-text>before</pre-text><code-lines>print('x')</code-lines>"),
            _base_data(),
        )

    with pytest.raises(ValueError, match="one-tray format requires"):
        pl_faded._build_config(
            _element("<pre-text>before</pre-text>", format="one-tray"),
            _base_data(),
        )


def test_prepare_infers_correct_answer_when_all_blanks_are_optional() -> None:
    data = _base_data()

    pl_faded.prepare(
        _element("def f():\n    return __[42]__", language="python"),
        data,
    )

    assert data["correct_answers"]["fpp"] == "def f():\n    return 42"


def test_parse_saved_state_rejects_non_object_and_bad_lines() -> None:
    with pytest.raises(pl_faded.ParsingError, match="JSON object"):
        pl_faded._parse_saved_state("[]", "[]")

    with pytest.raises(pl_faded.ParsingError, match="codeSnippets"):
        pl_faded._parse_saved_state(
            json.dumps(
                {
                    "solution": [
                        {
                            "indent": 0,
                            "pinned": False,
                            "codeSnippets": "return",
                            "blankValues": [],
                        }
                    ]
                }
            ),
            "[]",
        )


def test_parse_compiles_saved_solution_and_adds_submitted_file() -> None:
    data = _base_data()
    data["raw_submitted_answers"]["fpp.main"] = json.dumps(
        {
            "solution": [
                {
                    "indent": 0,
                    "pinned": True,
                    "codeSnippets": ["def f():"],
                    "blankValues": [],
                    "blankPlaceholders": [],
                },
                {
                    "indent": 1,
                    "pinned": False,
                    "codeSnippets": ["return ", ""],
                    "blankValues": ["42"],
                    "blankPlaceholders": ["answer"],
                },
            ],
            "starter": [],
        }
    )
    data["raw_submitted_answers"]["fpp.log"] = json.dumps(
        [{"timestamp": "now", "tag": "move", "data": {}}]
    )

    pl_faded.parse(_element("def f():\n    return __(answer)__"), data)

    assert data["submitted_answers"]["fpp"] == "def f():\n    return 42"
    submitted = data["submitted_answers"]["_files"][0]
    assert submitted["name"] == "user_code.py"
    assert base64.b64decode(submitted["contents"]).decode() == "def f():\n    return 42"


def test_parse_reports_incomplete_blank_without_submitting_file() -> None:
    data = _base_data()
    data["raw_submitted_answers"]["fpp.main"] = json.dumps(
        {
            "solution": [
                {
                    "indent": 0,
                    "pinned": False,
                    "codeSnippets": ["return ", ""],
                    "blankValues": [""],
                    "blankPlaceholders": ["answer"],
                }
            ],
            "starter": [],
        }
    )

    pl_faded.parse(_element("return __(answer)__"), data)

    assert data["format_errors"]["fpp"].startswith("Your answer has incomplete blanks")
    assert "_files" not in data["submitted_answers"]


def test_test_correct_round_trips_reference_source_and_submitted_file() -> None:
    data = _base_data()
    source = "def f():\n    return 42\n"
    data["test_type"] = "correct"
    data["correct_answers"]["fpp"] = source
    data["partial_scores"] = {"question-owned": {"score": 0.25}}
    data["score"] = 0.25

    pl_faded.test(_element("def f():\n    return ___"), data)

    saved_state = json.loads(data["raw_submitted_answers"]["fpp.main"])
    assert saved_state["starter"] == []
    assert [line["codeSnippets"] for line in saved_state["solution"]] == [
        ["def f():"],
        ["    return 42"],
        [""],
    ]
    assert data["partial_scores"] == {"question-owned": {"score": 0.25}}
    assert data["score"] == 0.25

    pl_faded.parse(_element("def f():\n    return ___"), data)

    assert data["submitted_answers"]["fpp"] == source
    submitted = data["submitted_answers"]["_files"][0]
    assert submitted["name"] == "user_code.py"
    assert base64.b64decode(submitted["contents"]).decode() == source


def test_test_correct_without_reference_answer_defers_to_question_test() -> None:
    data = _base_data()
    data["test_type"] = "correct"
    data["raw_submitted_answers"]["question-owned"] = "answer"

    pl_faded.test(_element("return ___"), data)

    assert data["raw_submitted_answers"] == {"question-owned": "answer"}


def test_test_incorrect_creates_valid_empty_source_submission() -> None:
    data = _base_data()
    data["test_type"] = "incorrect"

    pl_faded.test(_element("print('answer')"), data)

    assert json.loads(data["raw_submitted_answers"]["fpp.main"]) == {
        "solution": [],
        "starter": [],
    }

    pl_faded.parse(_element("print('answer')"), data)

    assert data["format_errors"] == {}
    assert data["submitted_answers"]["fpp"] == ""
    submitted = data["submitted_answers"]["_files"][0]
    assert base64.b64decode(submitted["contents"]).decode() == ""


def test_test_invalid_reproduces_incomplete_blank_error_without_authored_fade() -> None:
    data = _base_data()
    data["test_type"] = "invalid"

    pl_faded.test(_element("print('answer')"), data)

    expected_error = data["format_errors"]["fpp"]
    saved_state = json.loads(data["raw_submitted_answers"]["fpp.main"])
    assert saved_state["solution"][0]["blankValues"] == [""]

    data["format_errors"] = {}
    pl_faded.parse(_element("print('answer')"), data)

    assert data["format_errors"]["fpp"] == expected_error
    assert "fpp" not in data["submitted_answers"]
    assert "_files" not in data["submitted_answers"]



def test_render_question_builds_one_tray_with_pre_and_post_text() -> None:
    rendered = _render(
        _element(
            "<pre-text>def f():</pre-text>"
            '<code-lines visual-indent="1">    return __[42]__</code-lines>'
            "<post-text>print(f())</post-text>",
            format="one-tray",
        ),
        _base_data(),
    )

    assert rendered["starter"] == ""
    assert rendered["solution"]["wide"] is True
    assert rendered["pre_text"] == {"text": "def f():\n", "language": "", "indent": 0.0}
    assert rendered["post_text"] == {
        "text": "\nprint(f())",
        "language": "",
        "indent": 0.0,
    }
    assert rendered["visual_indent"] == 1


def test_render_submission_includes_compiled_code_and_empty_blank_message() -> None:
    data = _base_data(panel="submission")
    data["raw_submitted_answers"]["fpp.main"] = json.dumps(
        {
            "solution": [
                {
                    "indent": 0,
                    "pinned": False,
                    "codeSnippets": ["return ", ""],
                    "blankValues": [""],
                    "blankPlaceholders": ["answer"],
                }
            ],
            "starter": [],
        }
    )
    data["feedback"] = {"fpp": "try again"}

    rendered = _render(_element("return __(answer)__"), data)

    assert rendered["code"] == "return "
    assert rendered["has_feedback"] is True
    assert rendered["incomplete_blank_message"].startswith(
        "Your answer has incomplete blanks"
    )


def test_render_answer_uses_correct_answer_or_solution_path() -> None:
    data = _base_data(panel="answer")
    data["correct_answers"]["fpp"] = "print('answer')"

    rendered = _render(_element("print('starter')", language="python"), data)

    assert rendered["language"] == "python"
    assert rendered["correct_answer"] == "print('answer')"


def test_render_answer_infers_python_grader_tests_ans_solution(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    solution = tests_dir / "ans.py"
    solution.write_text(
        "def count_long_words(words, min_len):\n"
        "    return sum(1 for word in words if len(word) >= min_len)\n",
        encoding="utf-8",
    )
    data = _base_data(panel="answer")
    data["options"]["question_path"] = str(tmp_path)

    rendered = _render(
        _element(
            "def count_long_words(words, min_len):\n"
            "    count = 0 #pin(1)\n"
            "    for word in words: #pin(1)\n"
            "        if len(word) >= __(min_len)__: #pin(2)\n"
            "            count += 1\n"
            "    return count #pin(1)",
            language="python",
        ),
        data,
    )

    assert rendered["language"] == "python"
    assert rendered["solution_path"] == str(solution)
