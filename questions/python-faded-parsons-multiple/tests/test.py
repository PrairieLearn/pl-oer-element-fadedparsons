from typing import Iterable

from pl_helpers import name, points
from pl_unit_test import PLTestCase
from code_feedback import Feedback

def score_cases(student_fn, ref_fn, *cases):
    def wrapped(*case):
        x = student_fn(*case)
        if isinstance(x, Iterable):
            return list(x)
        return [x]
    correct = 0
    for case in cases:
        user_val = Feedback.call_user(wrapped, *case)
        ref_val = list(ref_fn(*case))
        if Feedback.check_list('output', ref_val, user_val):
            correct += 1

    if cases:
        Feedback.set_score(correct / len(cases))
    else:
        Feedback.set_score(1.0)

class Test(PLTestCase):
    @points(4)
    @name("small limits")
    def test_0(self):
        score_cases(self.st.multiples_of_three, self.ref.multiples_of_three,
            (2,),
            (3,),
        )

    @points(6)
    @name("larger limits")
    def test_1(self):
        score_cases(self.st.multiples_of_three, self.ref.multiples_of_three,
            (10,),
            (15,),
        )
