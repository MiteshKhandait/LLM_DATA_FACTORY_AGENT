from app.loaders import load_document


files = [
    "data/input/test.txt",
    "data/input/test.docx",
    "data/input/test.pdf",
]


for file_path in files:

    print("\n" + "=" * 60)
    print(f"File: {file_path}")
    print("=" * 60)

    document = load_document(file_path)

    print("Type:", document.file_type)
    print("Number of segments:", len(document.segments))

    for segment in document.segments:
        print(
            f"\nID: {segment.segment_id}"
        )
        print(
            f"Location: {segment.location}"
        )
        print(
            f"Text: {segment.text}"
        )