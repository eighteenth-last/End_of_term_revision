'''
*@BelongsProject: End_of_term_revision
*@BelongsPackage: 
*@Author: 程序员Eighteen
*@CreateTime: 2025-12-17  21:29
*@Description: 统一设置提示词
*@Version: 1.0
'''

# 文本解析为题目 JSON 的提示词
PARSE_TEXT_TO_QUESTIONS_PROMPT = '''你是一个专业的题目解析专家。请将以下文本解析成标准的题目格式。

文本内容：
{text}

科目：{subject}

请严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill/major",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）、major（大型题）
2. 判断题的 options 为 ["对", "错"]，答案只能是 "对" 或 "错"
3. 填空题的 options 可以为空数组 []
4. 如果文本中没有答案，请根据题目内容生成正确答案
5. 如果文本中没有解析，请根据题目内容生成详细解析，并写出关键计算步骤
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
7. 必须从文本中尽量识别出所有题目，禁止返回 "questions": []
8. 文本通常为试卷或复习题，带有编号 1.、2.、(1)、(2) 等，请根据这些编号拆分成多道题目。遇到类似“19. 判断题”这种小题集合时，(1)、(2)… 每一小问都要单独输出为一条 type="judge" 的题目
9. 当题干中出现“_____”“（ ）”等空格，需要填写一个或多个数值、概率、函数表达式等明确答案时，即使需要一定计算步骤，也统一使用填空题 type="fill"
10. 只有当题目要求书写较长的推导过程、证明、论述或综合分析时，才使用大型题 type="major"，options 使用 []
11. 大型题必须是主观题，analysis 必须给出分步推导过程（列公式、代入、计算每一步），而不是只给出最终答案
12. 对于 single/multiple 题，options 中每一项必须包含完整的选项内容，禁止出现只有 "A."、"B."、"C."、"D." 而没有文字或公式的情况

**【数学/物理公式识别要求】**
11. 所有数学公式和物理公式必须使用 LaTeX 格式：
   - 行内公式使用 $...$ 包裹，如：已知函数 $f(x)=x^2+2x+1$
   - 独立公式使用 $$...$$ 包裹，如：$$\\int_0^1 x^2 dx = \\frac{{1}}{{3}}$$
8. 必须保留完整的 LaTeX 语法：
   - 分式：\\frac{{a}}{{b}}
   - 上下标：x^2, x_i
   - 希腊字母：\\alpha, \\beta, \\gamma, \\theta, \\pi
   - 向量：\\vec{{v}}, \\overrightarrow{{AB}}
   - 积分：\\int, \\sum, \\lim
   - 根号：\\sqrt{{x}}, \\sqrt[n]{{x}}
9. 禁止将公式转换为自然语言描述
10. 禁止使用 MathML、图片或 Unicode 拼凑符号代替 LaTeX
'''

# OCR 文本解析为题目 JSON 的提示词
PARSE_IMAGE_TO_QUESTIONS_PROMPT = '''你是一个专业的题目识别专家。以下是从图片中 OCR 提取的文本，可能包含题目、选项等信息。

OCR 文本：
{image_text}

科目：{subject}

请识别并解析出题目，严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill/major",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）、major（大型题）
2. 判断题的 options 为 ["对", "错"]，答案只能是 "对" 或 "错"
3. 填空题的 options 可以为空数组 []
4. 如果图片中没有标注答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析，并写出关键计算步骤
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
7. 必须从 OCR 文本中尽量识别出所有题目，禁止返回 "questions": []
8. OCR 文本通常包含编号 1.、2.、(1)、(2) 等，请根据这些编号拆分成多道题目。遇到类似“19. 判断题”这种小题集合时，(1)、(2)… 每一小问都要单独输出为一条 type="judge" 的题目
9. 当题干中出现“_____”“（ ）”等空格，需要填写一个或多个数值、概率、函数表达式等明确答案时，即使需要一定计算步骤，也统一使用填空题 type="fill"
10. 只有当题目要求书写较长的推导过程、证明、论述或综合分析时，才使用大型题 type="major"，options 使用 []
11. 大型题必须是主观题，analysis 必须给出分步推导过程（列公式、代入、计算每一步），而不是只给出最终答案
12. 对于 single/multiple 题，options 中每一项必须包含完整的选项内容，禁止出现只有 "A."、"B."、"C."、"D." 而没有文字或公式的情况

**【数学/物理公式识别要求】**
11. 所有数学公式和物理公式必须使用 LaTeX 格式：
   - 行内公式使用 $...$ 包裹，如：已知函数 $f(x)=x^2+2x+1$
   - 独立公式使用 $$...$$ 包裹，如：$$\\int_0^1 x^2 dx = \\frac{{1}}{{3}}$$
8. 必须保留完整的 LaTeX 语法：
   - 分式：\\frac{{a}}{{b}}
   - 上下标：x^2, x_i
   - 希腊字母：\\alpha, \\beta, \\gamma, \\theta, \\pi
   - 向量：\\vec{{v}}, \\overrightarrow{{AB}}
   - 积分：\\int, \\sum, \\lim
   - 根号：\\sqrt{{x}}, \\sqrt[n]{{x}}
9. 禁止将公式转换为自然语言描述
10. 禁止使用 MathML、图片或 Unicode 拼凑符号代替 LaTeX
'''

# 图片直接解析为题目 JSON 的提示词
PARSE_IMAGE_DIRECT_PROMPT = '''你是一个专业的题目识别专家。请仔细观察图片中的题目内容，识别并解析出所有题目。

科目：{subject}

请严格按照以下 JSON 格式输出（必须是有效的 JSON）：
{{
  "subject": "{subject}",
  "questions": [
    {{
      "type": "single/multiple/judge/fill/major",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. 仔细识别题目类型：single（单选）、multiple（多选）、judge（判断）、fill（填空）、major（大型题）
2. 判断题的 options 为 ["对", "错"]，答案只能是 "对" 或 "错"
3. 填空题的 options 可以为空数组 []
4. 如果图片中包含答案，请使用图片中的答案；如果没有答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析，说明为什么这个答案是正确的，并写出关键计算步骤
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
7. 确保题目内容、选项、答案完整准确，不要出现乱码或遗漏
8. 必须尽量识别出所有题目，禁止返回 "questions": []
9. 试卷通常带有题号 1.、2.、(1)、(2) 等，请依据题号拆分成多道题目。遇到类似“19. 判断题”这种小题集合时，(1)、(2)… 每一小问都要单独输出为一条 type="judge" 的题目
10. 当题干中出现“_____”“（ ）”等空格，需要填写一个或多个数值、概率、函数表达式等明确答案时，即使需要一定计算步骤，也统一使用填空题 type="fill"
11. 只有当题目要求书写较长的推导过程、证明、论述或综合分析时，才使用大型题 type="major"，options 使用 []
12. 对于 single/multiple 题，options 中每一项必须包含完整的选项内容，禁止出现只有 "A."、"B."、"C."、"D." 而没有文字或公式的情况

**【数学/物理公式识别要求】**
12. 所有数学公式和物理公式必须使用 LaTeX 格式：
   - 行内公式使用 $...$ 包裹，如：已知函数 $f(x)=x^2+2x+1$
   - 独立公式使用 $$...$$ 包裹，如：$$\\int_0^1 x^2 dx = \\frac{{1}}{{3}}$$
13. 必须保留完整的 LaTeX 语法：
   - 分式：\\frac{{a}}{{b}}
   - 上下标：x^2, x_i
   - 希腊字母：\\alpha, \\beta, \\gamma, \\theta, \\pi
   - 向量：\\vec{{v}}, \\overrightarrow{{AB}}
   - 积分：\\int, \\sum, \\lim
   - 根号：\\sqrt{{x}}, \\sqrt[n]{{x}}
   - 物理单位：m/s, kg·m/s^2（单位不需要公式符号）
14. 禁止将公式转换为自然语言描述
15. 禁止使用 MathML、图片或 Unicode 拼凑符号代替 LaTeX
'''

# 生成题目解析的提示词
GENERATE_ANALYSIS_PROMPT = '''请为以下题目生成详细的解析说明。

题目：{question}

选项：
{options_text}

正确答案：{answer}

请生成详细的解析，说明为什么这个答案是正确的，以及解题思路。
'''

# 系统角色提示词
SYSTEM_ROLE_PARSE_TEXT = "你是一个专业的题目解析助手，擅长将文本转换为结构化的题目数据。"
SYSTEM_ROLE_PARSE_IMAGE = "你是一个专业的图片题目识别助手，擅长从 OCR 文本中提取并结构化题目数据。"
SYSTEM_ROLE_GENERATE_ANALYSIS = "你是一个专业的教育专家，擅长为题目提供清晰易懂的解析。"
