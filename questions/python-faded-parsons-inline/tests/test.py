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
    @name("uppercase found")
    def test_0(self):
        score_cases(self.st.first_uppercase, self.ref.first_uppercase,
            ("abcD",),
            ("mNo",),
        )

    @points(6)
    @name("no uppercase")
    def test_1(self):
        score_cases(self.st.first_uppercase, self.ref.first_uppercase,
            ("lowercase only",),
            ("123 !?",),
        )
