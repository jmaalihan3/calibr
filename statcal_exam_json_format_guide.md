# StatCal Exam JSON Schema and LLM Authoring Guide

## Purpose

This document defines the **StatCal exam-content format** used for multiple-choice assessments and post-exam review. It is intended as an implementation reference and as explicit instructions for an LLM that generates, transforms, or validates exam files.

The companion exam Markdown file contains **one fenced `json` code block** whose contents are a single valid JSON object. Parse the JSON inside the fence; the Markdown fence is not part of the JSON data. The example below is illustrative, not an additional exam question.

## Normative structure

The top-level object has three required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `unit` | integer | Curriculum unit identifier, e.g. `1`. |
| `unit_name` | string | Human-readable unit name. |
| `questions` | array of question objects | Questions in their intended display order. |

Each **question object** has these required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | integer | Unique identifier within this exam; stable across revisions. |
| `topic` | string | Broad curriculum section (prefer the Khan Academy unit subsection name). |
| `question` | string | Complete student-facing question stem. |
| `choices` | array | Answer options in display order. |
| `review` | object | Metadata for post-assessment learning feedback. |

Each **choice object** has these fields:

| Field | Type | Required? | Meaning |
| --- | --- | --- | --- |
| `id` | string | Yes | Stable, unique **within a question**; this exam uses `A`, `B`, `C`, `D`. |
| `text` | string | Yes | Exact student-facing answer option. |
| `is_correct` | boolean | Yes | Exactly one choice per question must be `true`. |
| `explanation` | string | Yes | For the correct choice: why it is correct. For an incorrect choice: the misconception or error associated with choosing it. |
| `misconception_id` | string | **Only for incorrect choices** | Unique identifier for that incorrect choice's misconception. Format in this exam: `QNN-MNN` (e.g. `Q01-M01`). Do not put this field on correct choices. |

Each **review object** has these required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `title` | string | Concise, question-specific heading for the expandable results panel. |
| `learning_objective` | string | Measurable skill or understanding targeted by the question. |
| `related_concepts` | array of strings | Usually 2–5 concise academic concepts directly connected to the question. |

`related_concepts` should use precise, reusable statistical terminology, not arbitrary keywords or misconception descriptions. Prefer Khan Academy's **Analyzing categorical data** terminology and supplement it with conventional terminology from academic statistics sources. Do not imply that every label is the exact title of a Khan Academy lesson: some are related or extended concepts. For analytics, normalize spelling and capitalization consistently across questions.

## Example (complete one-question exam object)

```json
{
  "unit": 1,
  "unit_name": "Analyzing Categorical Data",
  "questions": [
    {
      "id": 1,
      "topic": "Analyzing one categorical variable",
      "question": "A researcher records the primary color of cars in a parking lot. Which type of variable is 'car color', and what is the best way to summarize the distribution?",
      "choices": [
        {
          "id": "A",
          "text": "Quantitative; summarized by the mean and standard deviation.",
          "is_correct": false,
          "explanation": "Confuses qualitative categories with quantitative measures, assuming any data collection automatically results in numerical variables suitable for arithmetic mean.",
          "misconception_id": "Q01-M01"
        },
        {
          "id": "B",
          "text": "Categorical; summarized by frequencies or relative frequencies of each category.",
          "is_correct": true,
          "explanation": "Car color is a categorical (qualitative) variable because it places individuals into categories without numerical ordering. Categorical variables are summarized using counts (frequencies) or proportions/percentages (relative frequencies)."
        },
        {
          "id": "C",
          "text": "Quantitative; summarized by a histogram or stem-and-leaf plot.",
          "is_correct": false,
          "explanation": "Mistakes categorical labels for continuous numerical values that can be plotted on a continuous number line (histogram/stemplot).",
          "misconception_id": "Q01-M02"
        },
        {
          "id": "D",
          "text": "Categorical; summarized by the median and interquartile range.",
          "is_correct": false,
          "explanation": "Correctly identifies the variable type as categorical, but incorrectly applies quantitative summary statistics (median and IQR), assuming ordinal ranking exists where none does.",
          "misconception_id": "Q01-M03"
        }
      ],
      "review": {
        "title": "Identifying and summarizing categorical variables",
        "learning_objective": "Classify a variable as categorical and select appropriate frequency-based summaries",
        "related_concepts": [
          "Categorical variables",
          "Qualitative data",
          "Frequency",
          "Relative frequency"
        ]
      }
    }
  ]
}
```

## Results-screen logic

1. The results page displays the question, the learner's selected choice, and the correct choice. The choice order is the order in `choices`.
2. Use `review.title` as the heading for the question's expandable review panel. Show `review.learning_objective` and `review.related_concepts` as optional *UI displays*; they are **required in the data**.
3. Always show the **correct choice's** `explanation` as the correct-answer explanation, whether or not the learner answered correctly.
4. **Only if the learner answered incorrectly**, show the `explanation` of **the specific incorrect choice the learner selected**, labeled as misconception feedback. Do not show the explanations of other incorrect choices.
5. Do not present an incorrect-choice `explanation` as an authoritative statement of what the student believes. It is a **potential misconception suggested by the response**, not a diagnosis.
6. A missing learner response is not an incorrect choice selection: do not invent misconception feedback for an unanswered question.
7. `misconception_id` is for analytics and content management, not necessarily for student display. It is not a confidence score.

### Pseudocode

```text
correct_choice = exactly_one(question.choices where is_correct == true)
selected_choice = find(question.choices where id == student_answer_id)
show(correct_choice.text)
show(correct_choice.explanation)
if selected_choice exists and selected_choice.is_correct == false:
    show(selected_choice.explanation)  # only this selected misconception
```

## Validation rules for an LLM or script

- The file must contain one parseable JSON object; preserve the Markdown `json` fence if writing an `.md` file.
- All required top-level, question, choice, and review fields must exist and have the specified types.
- Question IDs must be unique; each question must have exactly one correct choice.
- Choice IDs must be unique within each question; answer text and explanations must be nonempty.
- Every incorrect choice must have one nonempty `misconception_id`; correct choices must not have it. Misconception IDs must be unique **within the exam**.
- `review.title` and `review.learning_objective` must be nonempty; `review.related_concepts` must contain 2–5 distinct, nonempty strings.
- For an existing exam conversion, preserve question stems, choice text and order, answer key, and all original explanation text **verbatim** unless separately asked to correct content.
- Preserve source question ordering and broad `topic` labels. Do not silently change answer keys or claim the content has been academically validated merely because the schema passes.
- An LLM should propose edits separately if it detects potentially inaccurate statistics, ambiguous answers, weak distractors, or unsupported misconception descriptions.

## Mapping from the previous StatCal format

| Previous field | New field |
| --- | --- |
| `options[i]` | `choices[i].text` |
| `correct` (zero-based index) | `choices[i].is_correct` (`true` only for the matching index) |
| Question-level `explanation` | `choices[correct].explanation` |
| `misconceptions[str(i)]` | `choices[i].explanation` for incorrect choices |
| No previous choice IDs | `choices[i].id` (`A`–`D`) |
| No previous misconception IDs | `choices[i].misconception_id` for incorrect choices |
| No previous review metadata | `review.title`, `review.learning_objective`, `review.related_concepts` |

## Source alignment and limitations

The original exam's question text, answer keys, and explanations were preserved during structural conversion. The new review titles, objectives, and concept tags are **editorial additions**, informed by the curriculum and standard statistical terminology; they are not quotations from the sources. No claim is made that the original questions or explanations have undergone a new full academic correctness review.

Primary curricular source:
- Khan Academy, *Statistics and probability — Unit 1: Analyzing categorical data*: https://www.khanacademy.org/math/statistics-probability/analyzing-categorical-data
- Khan Academy, *Two-way relative frequency tables and associations*: https://www.khanacademy.org/math/statistics-probability/analyzing-categorical-data/two-way-tables-for-categorical-data/a/two-way-relative-frequency-tables-super-powers

Supplementary academic references:
- OpenStax, *Introductory Statistics 2e*, §3.4, *Contingency Tables*: https://openstax.org/books/introductory-statistics-2e/pages/3-4-contingency-tables
- OpenIntro, *Advanced High School Statistics*, §2.1, *Relationships between two categorical variables*: https://www.openintro.org/go/?id=ahss4_for_screen_reader

Topics such as Simpson's paradox, confounding, and graphical perception extend beyond the unit's named lesson headings. Their inclusion reflects the existing exam questions and standard related statistical concepts, not an assertion that Khan Academy Unit 1 explicitly teaches every such extension.
