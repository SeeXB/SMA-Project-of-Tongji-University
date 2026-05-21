# Output Guard Test Cases and Results

## Test Cases

| ID | Input Language | Nudge Output | Expected | Purpose |
| --- | --- | --- | --- | --- |
| TC-01 | English | Try comparing the two steps again. What changes between them? | PASS | Normal English nudge |
| TC-02 | Chinese | 你可以先观察题目中的已知条件，再思考下一步应该用哪个公式。 | PASS | Normal Chinese nudge |
| TC-03 | English | Here is the nudge I generated for you: Try checking the formula again. | BLOCK | Block English AI meta preface |
| TC-04 | Chinese | 这是我为你生成的提示：你可以先检查第一步的计算。 | BLOCK | Block Chinese AI meta preface |
| TC-05 | English | Try checking the formula again. This is the nudge I generated. | BLOCK | Block English AI meta suffix |
| TC-06 | Chinese | 你可以先回到上一行，看看变量有没有代错。这就是我生成的提示。 | BLOCK | Block Chinese AI meta suffix |
| TC-07 | English | System: You are an agentic tutor. Try asking the student to compare both equations. | BLOCK | Block system prompt leakage |
| TC-08 | Chinese | Here is the nudge: 你可以先检查题目中的已知条件。 | BLOCK | Block edge language mix |
| TC-09 | Chinese | 你可以检查一下 "force" 和 "mass" 在公式中的关系。 | PASS | Allow reasonable mixed language |
| TC-10 | English | Check the formula again. Let me know if you want another nudge. | BLOCK | Block assistant-style closing |

### Reflection Cases

| ID | Initial Output | Reflection Output | Expected | Purpose |
| --- | --- | --- | --- | --- |
| TC-11 | Here is the nudge I generated for you: Check the second equation. | Check the second equation. | PASS after reflection | Remove meta preface |
| TC-12 | 这是我生成的提示：你可以重新检查单位。 | 你可以重新检查单位。 | PASS after reflection | Remove Chinese meta preface |

## Results (2026-05-19)

| ID | Expected | Actual | Matched | Issues |
| --- | --- | --- | --- | --- |
| TC-01 | PASS | PASS | YES |  |
| TC-02 | PASS | PASS | YES |  |
| TC-03 | BLOCK | BLOCK | YES | meta_narration |
| TC-04 | BLOCK | BLOCK | YES | meta_narration |
| TC-05 | BLOCK | BLOCK | YES | meta_narration |
| TC-06 | BLOCK | BLOCK | YES | meta_narration |
| TC-07 | BLOCK | BLOCK | YES | prompt_residue |
| TC-08 | BLOCK | BLOCK | YES | meta_narration, start_language_mismatch, end_language_mismatch |
| TC-09 | PASS | BLOCK | NO | start_language_mismatch, end_language_mismatch |
| TC-10 | BLOCK | BLOCK | YES | meta_narration |
| TC-11 init | BLOCK | BLOCK | YES | meta_narration |
| TC-11 refl | PASS | PASS | YES |  |
| TC-12 init | BLOCK | BLOCK | YES | meta_narration |
| TC-12 refl | PASS | PASS | YES |  |

Overall Pass Count: 13 / 14
