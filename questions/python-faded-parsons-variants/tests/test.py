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
    @name("focusing")
    def test_0(self):
        score_cases(self.st.stay_focused, self.ref.stay_focused,
            ("Bobby",),
            ("Kiara",),
        )

    @points(4)
    @name("averages")
    def test_1(self):
        score_cases(self.st.average, self.ref.average,
            ([]),
            ([1]),
            ([4,-2, 3, 7]),
        )
