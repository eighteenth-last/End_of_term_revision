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
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果文本中没有答案，请根据题目内容生成正确答案
5. 如果文本中没有解析，请根据题目内容生成详细解析
6. 必须返回有效的 JSON 格式，不要包含任何其他文字

**【数学/物理公式识别要求】**
7. 所有数学公式和物理公式必须使用 LaTeX 格式：
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
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. type 只能是：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果图片中没有标注答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析
6. 必须返回有效的 JSON 格式，不要包含任何其他文字

**【数学/物理公式识别要求】**
7. 所有数学公式和物理公式必须使用 LaTeX 格式：
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
      "type": "single/multiple/judge/fill",
      "question": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "正确答案（单选填A/B/C/D，多选填A,B,C，判断填对/错，填空填具体答案）",
      "analysis": "题目解析"
    }}
  ]
}}

注意事项：
1. 仔细识别题目类型：single（单选）、multiple（多选）、judge（判断）、fill（填空）
2. 判断题的 options 为 ["对", "错"]
3. 填空题的 options 可以为空数组 []
4. 如果图片中包含答案，请使用图片中的答案；如果没有答案，请根据题目内容生成正确答案
5. 必须生成详细的题目解析，说明为什么这个答案是正确的
6. 必须返回有效的 JSON 格式，不要包含任何其他文字
7. 确保题目内容、选项、答案完整准确，不要出现乱码或遗漏

**【数学/物理公式识别要求】**
8. 所有数学公式和物理公式必须使用 LaTeX 格式：
   - 行内公式使用 $...$ 包裹，如：已知函数 $f(x)=x^2+2x+1$
   - 独立公式使用 $$...$$ 包裹，如：$$\\int_0^1 x^2 dx = \\frac{{1}}{{3}}$$
9. 必须保留完整的 LaTeX 语法：
   - 分式：\\frac{{a}}{{b}}
   - 上下标：x^2, x_i
   - 希腊字母：\\alpha, \\beta, \\gamma, \\theta, \\pi
   - 向量：\\vec{{v}}, \\overrightarrow{{AB}}
   - 积分：\\int, \\sum, \\lim
   - 根号：\\sqrt{{x}}, \\sqrt[n]{{x}}
   - 物理单位：m/s, kg·m/s^2（单位不需要公式符号）
10. 禁止将公式转换为自然语言描述
11. 禁止使用 MathML、图片或 Unicode 拼凑符号代替 LaTeX
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
