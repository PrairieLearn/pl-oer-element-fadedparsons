# PrairieLearn OER Element: Faded Parsons Problem

This element was developed by the [ACE Lab at UC Berkeley](https://acelab.berkeley.edu). Please carefully test the element and understand its features and limitations before deploying it in a course. It is provided as-is and not officially maintained by PrairieLearn, so we can only provide limited support for any issues you encounter!

If you like this element, you can use it in your own PrairieLearn course by copying the contents of the `elements` folder into your own course repository. After syncing, the element can be used as illustrated by the example question that is also contained in this repository.


## `pl-faded-parsons` element

This element creates a "faded" version of a Parsons Problem, where students drag and drop lines of code into order. In the faded version of the problem, students also fill in gaps in the code via embedded text inputs. This element is conceptually similar to `pl-order-blocks`, but adds support for faded code fragments and uses test-based grading (e.g., via the Python auto-grader) rather than comparing submissions to a sample solution. The latter can be beneficial when multiple correct solutions for a problem exist.


### Element Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `answers-name` | string (required) | Unique name for the element. |
| `format` | string (default: `"right"`) | Format of the element. `"right"`/`"bottom"` for placement of the code canvas relative to the tray; `"one-tray"` for one-tray format (see below). |
| `language` | string (default: `""`) | Code language, primarily used for syntax highlighting. |
| `file-name` | string (default: `"user_code.py"`) | Name for the code file submitted to the auto-grader. |
| `solution-path` | string (default: `"./solution"`) | Name of the solution code file displayed in the answer panel. If language is set to `"python"` and no valid path is provided, the path is automatically inferred as `"tests/ans.py"`. |
| `max-indent-level` | integer (default: `5`) | Maximum indentation level for student submissions. |
| `enable-copy-code` | boolean (default: `false`) | Whether a button should be displayed that allows students to copy their submission as plain text. |
| `log` | boolean (default: `false`) | Whether advanced logging should be enabled to record interactions with the element UI in the student submission data. This might be useful for research or debugging purposes.


### How to Use This Element

#### Question configuration and grading

Generally, questions that use `pl-faded-parsons` should be configured the same way as standard coding questions. For example, to use the element for Python questions, refer to the [Python auto-grading documentation](https://docs.prairielearn.com/python-grader/) and configure your `info.json` file to use the Python auto-grader:

```json title="info.json"
{
	// other configuration...
	"gradingMethod": "External",
	"externalGradingOptions": {
	  "image": "prairielearn/grader-python"
	}
}
```

Unit tests should be configured as usual for the external auto-grader, so for example, Python coding questions should provide a sample solution in `"tests/ans.py"` and unit tests in `tests/test.py`.


#### Scaffolding syntax

The provided scaffolding code is set up directly within the `question.html` file inside the `<pl-faded-parsons>` tags. Note that unlike in `pl-order-blocks`, this code is not directly used for grading purposes, and the sample solution file (e.g., `"tests/ans.py"`) is what gets displayed to students in the answer panel.

The scaffolding code is automatically broken down line-by-line into re-arrangeable blocks. Any indentation is stripped and serves solely to make the question file easier to read. Blocks are shuffled and added to the available block tray (or directly to the coding canvas for questions that use the "one-tray" format).

To provide preset blocks at a certain location in the coding canvas, annotate the line with `#Ngiven`, where `N` is the block's initial indentation level. These blocks are inserted into the coding canvas in the same order as they appear in the question file. Note that preset blocks can still be re-arranged by students.

You can also annotate lines as `#distractor` to mark that they should not appear in a valid solution. This annotation is purely for readability purposes and not used in the question or grading logic. Submissions that contain `#distractor` blocks are still auto-graded based on the provided tests.

To add "faded" text inputs to code blocks, use the annotation `!BLANK` in place of the missing value. For example, `return !BLANK` would provide students with a return statement scaffold, but let them input the returned value as text. The annotation `#blank prefill` can be used to insert a `prefill` value into a text box. 

Multiple `!BLANK` annotations can be used in the same line. You can use separate annotations (i.e., `#blank A #blank B`) to prefill them left to right.

When designing questions, keep in mind that students can enter arbitrary text into text boxes. This means that they could, for example, add unintended delimiters or return statements to "break out of" the provided scaffold. You should always use careful unit testing for grading purposes and not rely on scaffolding to restrict the range of possible student submissions.


### Examples

#### Standard Parsons Problem

```html
<pl-faded-parsons answers-name="fpp" language="python">
  def fibonacci(n: int): #0given
    if n <= 2: #1given
      return 1 #2given
    n_less_2 = fibonacci(n - 2)
    n_less_1 = fibonacci(n - 1)
    n_less_0 = fibonacci(n) #distractor
    return n_less_1 + n_less_2 #1given
</pl-faded-parsons>
```

![Standard Parsons example](images/standard-parsons.png)

This is a Parsons Problem without any faded blanks.
Students build up a solution by dragging and and indenting the lines from the tray on the left into the canvas on the right.
In this example, a distractor code line on the left is remains that is not part of the correct solution.

Notice how the reference answer and student answer don't exactly match, even though they're equivalent. This works because the element emits answers as code and grades the via a test suite, just like a standard programming question.

![Python auto-grading output](images/python-out.png)


#### Faded Parsons Problem

```html
<pl-faded-parsons answers-name="fpp" language="python">
  def fibonacci(n: int): #0given
    if n <= !BLANK:
      return 1
    return fibonacci(!BLANK) + fibonacci(!BLANK)
</pl-faded-parsons>
```

![Faded Parsons example](images/faded-parsons.png)

This is a Faded Parsons Problem with blanks that need to be filled by students. In the screenshot, one of the blanks is already filled by the student. It is also possible to configure the problem so that some blanks are prefilled, for example with placeholder values or hints.


#### One-Tray Faded Parsons Problem

```html
<pl-faded-parsons answers-name="student-parsons-solution" format="one-tray" language="ruby">
<pre-text>
describe GiftCard do
</pre-text>
<code-lines>
  it 'fails to instantiate with negative balance' do #0given
    !BLANK { GiftCard.new(-1) }.to raise_error(ArgumentError) #1given #blank expect
  end #0given
  it 'successfully assigns a positive balance on instantiation' do #0given
    gift_card = !BLANK.new(20) #1given #blank GiftCard
    expect(gift_card.balance).to eq(20) #1given
  end #0given
</code-lines>
<post-text>
end

</post-text>
</pl-faded-parsons>
```

A special question format that the element supports is the "one-tray" format. In this format, there is only one canvas and students directly interact with it by re-arranging and filling the provided blocks. 

Note that this format does not support distractors since it is not possible to remove blocks from the submission. It is however possible to include pre-text and post-text blocks that are fixed and provide context for the solution.

![One-Tray Faded Parsons example](images/one-tray-faded-parsons.png)

Note that the example above is written in Ruby to demonstrate that this element supports external auto-graders other than Python. They just need to be set up as one would for standard programming questions, and the element provides the submission code to them.

![Ruby auto-grading output](images/ruby-out.png)


### Credits and Thanks

The element is the product of the work of
- Serena Caraco ([GitHub](https://www.github.com/SybelBlue))
- Nelson Lojo ([GitHub](https://www.github.com/nelson-lojo), [LinkedIn](https://www.linkedin.com/in/nelson-lojo))
- Nathaniel (Weinman) Gainsboro during his PhD @ UC Berkeley ([LinkedIn](https://www.linkedin.com/in/nate-gainsboro), [Google Scholar](https://scholar.google.com/citations?user=OlvIQyoAAAAJ&hl=en))
- Armando Fox, generously advising them all ([GitHub](https://github.com/armandofox), [Homepage](https://www.armandofox.com/))


#### More Work on Faded Parsons Problems

The following work provides more context on the benefits of Faded Parsons Problems and the motivation for and implementation of this element: 

[Nathaniel Weinman, Armando Fox, and Marti A. Hearst. 2021. Improving Instruction of Programming Patterns with Faded Parsons Problems. In Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems (CHI '21). Association for Computing Machinery, New York, NY, USA, Article 53, 1–4. https://doi.org/10.1145/3411764.3445228](https://dl.acm.org/doi/10.1145/3411764.3445228)

[Logan Caraco, Nate Weinman, Stanley Ko and Armando Fox. 2022. Automatically Converting Code-Writing Exercises to Variably-Scaffolded Parsons Problems. EECS Department University of California, Berkeley Technical Report No. UCB/EECS-2022-173. June 27, 2022. http://www2.eecs.berkeley.edu/Pubs/TechRpts/2022/EECS-2022-173.pdf](http://www2.eecs.berkeley.edu/Pubs/TechRpts/2022/EECS-2022-173.pdf)

[Nelson Lojo and Armando Fox. 2022. Teaching Test-Writing As a Variably-Scaffolded Programming Pattern. In Proceedings of the 27th ACM Conference on on Innovation and Technology in Computer Science Education Vol. 1 (ITiCSE '22). Association for Computing Machinery, New York, NY, USA, 498–504. https://doi.org/10.1145/3502718.3524789](https://dl.acm.org/doi/10.1145/3502718.3524789)

[Lauren Zhou, Akshit Dewan, Anirudh Kothapalli, Pamela Fox, Michael Ball, and Thomas Joseph. 2023. Implementing Faded Parsons Problems in a Very Large CS1 Course. In Proceedings of the 54th ACM Technical Symposium on Computer Science Education V. 2 (SIGCSE 2023). Association for Computing Machinery, New York, NY, USA, 1356. https://doi.org/10.1145/3545947.3576300](https://dl.acm.org/doi/abs/10.1145/3545947.3576300)

[Slide deck for a CS 194-244 project at University of California, Berkeley around problem autogeneration](https://docs.google.com/presentation/d/1XPSyo1BaQnEEaCSphn9YJi3tg7m5fiIwGa7qGVNdAzg/edit?usp=sharing)