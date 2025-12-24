from services.file_reader import FileReader
from services.question_preprocessor import QuestionPreprocessor

# 读取测试文件
text = FileReader.read_docx(r'r:\Code_Repository\End_of_term_revision\2025-2026概率期末复习题.docx')

# 预处理
preprocessor = QuestionPreprocessor()
questions = preprocessor.extract_questions_structure(text)

# 输出统计
print(f'识别题目数量: {len(questions)}')
print(f'平均置信度: {preprocessor.calculate_average_confidence(questions):.2f}')
print('\n前5道题:')
for q in questions[:5]:
    print(f"题{q['question_number']}: {q['detected_type']} (置信度{q['confidence']}), 选项数{len(q['options'])}")
