from app.loaders import load_document
from app.tools import (
    extract_information,
    summarize_document,
    answer_question,
)


document = load_document(
    "data/input/test.docx"
)


print("\n" + "=" * 60)
print("INFORMATION EXTRACTION")
print("=" * 60)

extraction_result = extract_information(
    document=document,
    fields=[
        "scheme_name",
        "department",
        "budget",
        "target_beneficiaries",
        "districts_covered",
    ],
)

print(extraction_result)


print("\n" + "=" * 60)
print("DOCUMENT SUMMARY")
print("=" * 60)

summary_result = summarize_document(
    document=document,
)

print(summary_result)

print("\n" + "=" * 60)
print("DOCUMENT QUESTION ANSWERING")
print("=" * 60)

question_result = answer_question(
    document=document,
    question="What is the budget allocation?",
)

print(question_result)