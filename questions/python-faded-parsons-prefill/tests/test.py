from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

def score_cases(student_fn, ref_fn, *cases):
    correct = 0
    for case in cases:
        user_val = Feedback.call_user(student_fn, *case)
        ref_val = ref_fn(*case)
        if user_val == ref_val:
            correct += 1

    if cases:
        Feedback.set_score(correct / len(cases))
    else:
        Feedback.set_score(1.0)

class Test(PLTestCase):
    @points(4)
    @name("simple thresholds")
    def test_0(self):
        score_cases(self.st.count_long_words, self.ref.count_long_words,
            (["a", "bb", "ccc"], 2),
            (["short", "tiny", "large"], 5),
        )

    @points(6)
    @name("empty and mixed")
    def test_1(self):
        score_cases(self.st.count_long_words, self.ref.count_long_words,
            ([], 3),
            (["python", "go", "rust", "c"], 4),
        )
