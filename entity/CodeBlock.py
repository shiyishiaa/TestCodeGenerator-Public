from typing import Optional

from pydantic import BaseModel, Field


class CodeBlock(BaseModel):
    """Represents a code block extracted from Markdown"""
    language: str = Field(default="text", description="The language of the code block")
    code: Optional[str] = Field(default=None, description="The code inside the code block")
