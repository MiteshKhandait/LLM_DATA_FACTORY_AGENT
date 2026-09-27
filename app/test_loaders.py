from app.loaders import load_document


files = [
    "data/input/test.txt",
    "data/input/test.docx",
    "data/input/test.pdf",
]


for file_path in files:

    print("\n" + "=" * 60)
    print(f"Loading: {file_path}")
    print("=" * 60)

    try:
        document = load_document(file_path)

        print("File type:", document.file_type)
        print("Source:", document.source)
        print("Metadata:", document.metadata)

        print("\nText preview:")
        print(document.text[:500])

    except Exception as error:
        print("ERROR:", error)