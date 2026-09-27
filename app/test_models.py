from models import Document


document = Document(
    text="This is a sample government document.",
    source="sample.docx",
    file_type="docx",
    metadata={
        "page_count": 3
    }
)

print(document)
print()
print("Source:", document.source)
print("File type:", document.file_type)
print("Metadata:", document.metadata)