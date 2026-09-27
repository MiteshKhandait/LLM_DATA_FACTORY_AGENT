from typing import Any

from app.llm import LLMClient
from app.models import Document
from app.provenance import find_evidence


llm = LLMClient()


def extract_information(
    document: Document,
    fields: list[str],
) -> dict[str, Any]:
    """
    Extract requested fields from a document.

    Information that is not explicitly supported by the
    document should be returned as null.
    """

    fields_text = "\n".join(
        f"- {field}"
        for field in fields
    )

    prompt = f"""
You are an information extraction system for government documents.

Extract only information that is explicitly supported by the
document provided below.

Requested fields:
{fields_text}

Rules:
1. Return one JSON object.
2. Use the requested field names as the JSON keys.
3. If a requested field is not present in the document, return null.
4. Do not infer or invent missing information.
5. Preserve the meaning and wording of the source where practical.
6. Return only valid JSON.
7. Do not add fields that were not requested.

Document source:
{document.source}

Document:
{document.text}
"""

    extracted_data = llm.generate_json(prompt)

    return {
        "source": document.source,
        "data": extracted_data,
    }


def summarize_document(
    document: Document,
) -> dict[str, Any]:
    """
    Generate a structured summary of a document.

    The summary must be based only on information explicitly
    supported by the document.
    """

    prompt = f"""
You are a strict government-document summarization system.

Summarize ONLY what is explicitly stated in the document.

Return exactly one JSON object with these keys:

1. "summary"
   - A concise summary containing only explicit facts stated in the document.
   - Do not describe something as a program, initiative, project, policy,
     objective, cause, or purpose unless the document explicitly uses that
     terminology or clearly states it.

2. "key_findings"
   - A list of important facts or observations explicitly stated in the document.

3. "important_entities"
   - A list of explicitly named entities such as departments,
     organizations, schemes, programs, locations, or people.
   - Do not include numbers, budgets, dates, or generic concepts as entities.

Strict rules:
1. Do not use outside knowledge.
2. Do not infer relationships between facts.
3. Do not infer purpose, intent, causation, or classification.
4. Do not introduce words such as "program", "initiative", "project",
   "focus", "aim", or "support" unless explicitly supported by the document.
5. Preserve the meaning of the source.
6. If the document is very short, keep the summary equally simple.
7. Return valid JSON only.
8. Do not add additional keys.

Document source:
{document.source}

Document:
{document.text}
"""

    summary = llm.generate_json(prompt)

    return {
        "source": document.source,
        "data": summary,
    }


def answer_question(
    document: Document,
    question: str,
) -> dict[str, Any]:
    """
    Answer a question using only information contained
    in the supplied document and verify the supporting
    evidence against the original document.
    """

    prompt = f"""
You are a question-answering system for government documents.

Answer the user's question using only information explicitly
supported by the document.

User question:
{question}

Return exactly one JSON object with these keys:

1. "answer"
   - The answer to the question.
   - Return null if the document does not contain enough information.

2. "evidence"
   - The text from the document that supports the answer.
   - Keep it short.
   - Return null if the answer is null.

Rules:
1. Do not use outside knowledge.
2. Do not infer information that is not supported by the document.
3. If the document does not contain the answer, return null.
4. Return valid JSON only.
5. Do not add additional keys.

Document source:
{document.source}

Document:
{document.text}
"""

    llm_result = llm.generate_json(prompt)

    answer = llm_result.get("answer")
    evidence = llm_result.get("evidence")

    provenance = find_evidence(
        document=document,
        evidence=evidence,
    )

    return {
        "answer": answer,
        "evidence": (
            provenance.get("evidence")
            if provenance.get("verified")
            else None
        ),
        "source": document.source,
        "provenance": provenance,
    }