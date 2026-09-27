from typing import Any

from pydantic import BaseModel, Field


class DocumentSegment(BaseModel):
    """
    A portion of a document together with its source location.
    """

    segment_id: str = Field(
        ...,
        description="Unique identifier for this document segment",
    )

    text: str = Field(
        ...,
        description="Text contained in this segment",
    )

    location: dict[str, Any] = Field(
        default_factory=dict,
        description="Location of this segment in the original source",
    )


class Document(BaseModel):
    """
    Standard representation of a document loaded into the system.
    """

    text: str = Field(
        ...,
        description="Full extracted text from the document",
    )

    source: str = Field(
        ...,
        description="Original file name or source path",
    )

    file_type: str = Field(
        ...,
        description="Type of the source document",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional information about the document",
    )

    segments: list[DocumentSegment] = Field(
        default_factory=list,
        description="Document segments with source locations",
    )