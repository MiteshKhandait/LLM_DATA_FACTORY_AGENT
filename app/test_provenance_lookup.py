from app.loaders import load_document
from app.provenance import find_evidence


document = load_document(
    "data/input/test.docx"
)


test_cases = [
    "Budget Allocation: Rs. 150 crore",
    "Budget Allocation: Rs. 150crore",
    "Rs. 150 crore",
    "Expenditure in 2024",
]


for evidence in test_cases:

    print("\n" + "=" * 60)
    print(f"Searching for: {evidence}")
    print("=" * 60)

    result = find_evidence(
        document=document,
        evidence=evidence,
    )

    print(result)