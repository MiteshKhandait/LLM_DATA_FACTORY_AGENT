from typing import Any

from app.state import AgentState


def _format_extraction(result: dict[str, Any]) -> str:
    """
    Format an information-extraction result.
    """

    data = result.get("data", {})

    lines = []

    for field, value in data.items():
        display_field = field.replace("_", " ").title()

        if value is None:
            value = "Not available in the document"

        lines.append(
            f"- **{display_field}:** {value}"
        )

    return "\n".join(lines)


def _format_summary(result: dict[str, Any]) -> str:
    """
    Format a document-summary result.
    """

    data = result.get("data", {})

    sections = []

    summary = data.get("summary")

    if summary:
        sections.append(
            f"**Summary:**\n{summary}"
        )

    key_findings = data.get(
        "key_findings",
        []
    )

    if key_findings:
        findings = "\n".join(
            f"- {finding}"
            for finding in key_findings
        )

        sections.append(
            f"**Key Findings:**\n{findings}"
        )

    important_entities = data.get(
        "important_entities",
        []
    )

    if important_entities:
        entities = ", ".join(
            str(entity)
            for entity in important_entities
        )

        sections.append(
            f"**Important Entities:** {entities}"
        )

    return "\n\n".join(sections)


def _format_question_answer(
    result: dict[str, Any],
) -> str:
    """
    Format a question-answering result with verified provenance.
    """

    answer = result.get("answer")

    if answer is None:
        return (
            "The requested information is not available "
            "in the document."
        )

    response = f"**Answer:** {answer}"

    provenance = result.get(
        "provenance",
        {}
    )

    if provenance.get("verified"):

        evidence = provenance.get("evidence")

        if evidence:
            response += (
                f"\n\n**Evidence:** {evidence}"
            )

        location = provenance.get("location")

        if location:
            location_type = location.get("type")

            if location_type == "page":
                location_text = (
                    f"Page {location.get('page')}"
                )

            elif location_type == "paragraph":
                location_text = (
                    f"Paragraph {location.get('paragraph')}"
                )

            elif location_type == "line":
                location_text = (
                    f"Line {location.get('line')}"
                )

            else:
                location_text = str(location)

            response += (
                f"\n\n**Location:** {location_text}"
            )

    else:
        response += (
            "\n\n**Source verification:** "
            "Supporting evidence could not be verified "
            "against the document."
        )

    source = result.get("source")

    if source:
        response += (
            f"\n\n**Source:** `{source}`"
        )

    return response


def format_response(
    state: AgentState,
) -> str:
    """
    Convert the completed AgentState into a deterministic
    user-facing response.

    No LLM is called here.
    """

    if state.status == "failed":
        return (
            "The agent could not complete the request.\n\n"
            f"Error: {state.error}"
        )

    if not state.tool_results:
        return (
            "The agent completed without producing "
            "a tool result."
        )

    formatted_sections = []

    for tool_result in state.tool_results:

        if tool_result.tool_name == "extract_information":

            content = _format_extraction(
                tool_result.result
            )

            formatted_sections.append(content)

        elif tool_result.tool_name == "summarize_document":

            content = _format_summary(
                tool_result.result
            )

            formatted_sections.append(content)

        elif tool_result.tool_name == "answer_question":

            content = _format_question_answer(
                tool_result.result
            )

            formatted_sections.append(content)

    return "\n\n".join(formatted_sections)