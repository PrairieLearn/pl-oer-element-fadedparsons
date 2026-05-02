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

    # set_score must be in range 0.0 to 1.0
    if cases:
        Feedback.set_score(correct / len(cases))
    else:
        Feedback.set_score(1.0)

class Test(PLTestCase):
    @points(2)
    @name("basic cases")
    def test_0(self):
        score_cases(self.st.total, self.ref.total,
          ([0,],),
          ([1,],),
          ([],)
        )


    @points(8)
    @name("complex cases")
    def test_1(self):
        score_cases(self.st.total, self.ref.total,
            ([5,4,3,2,1],),
            ([10,-7,5,0],),
        )