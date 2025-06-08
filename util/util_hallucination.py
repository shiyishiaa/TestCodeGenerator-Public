from pathlib import Path
from typing import List

from constant import PROMPT_HALLUCINATION
from entity import Detail
from util import chat


def hallucination(image_path: Path) -> List[bool]:
    """
    Detect if the test code is not correct and the hallucination exists in the test code given the screenshot and source code.

    Args:
        image_path: The path to the image file.

    Returns:
        A list of boolean values indicating if the test code is not correct and the hallucination not exists in the test code
        given the screenshot and source code.
    """
    detail = Detail.load(str(image_path) + ".json")
    if not detail.project or not detail.location:
        raise ValueError("Cannot read source code from detail")

    rst = []
    for code in detail.code:
        if code.language.lower() not in {"python", "javascript", "typescript"}:
            rst.append(True)
            continue

        if source_code := Path(detail.project).joinpath(detail.location).read_text():
            system = PROMPT_HALLUCINATION
            text = "Test code: " + code.code + "\nSource code: " + source_code
            image_url = str(image_path)
            if (chat(system=system, text=text, image_url=image_url)).lower() == "true":
                rst.append(True)
            else:
                rst.append(False)
        else:
            rst.append(True)

    return rst
