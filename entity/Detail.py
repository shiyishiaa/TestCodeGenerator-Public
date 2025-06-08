from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from .CodeBlock import CodeBlock


class Detail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    project: Optional[str] = None
    location: Optional[str] = None
    framework: Optional[str] = None
    language: Optional[str] = None
    tool: Optional[str] = None
    content: Optional[str] = None

    code: List[CodeBlock] = []
    code_no_desc: List[CodeBlock] = []

    @classmethod
    def load(cls, path: str) -> "Detail":
        return cls.model_validate_json(Path(path).read_text(), strict=False)

    def save(self, path: str) -> None:
        Path(path).write_text(self.model_dump_json(indent=4))
