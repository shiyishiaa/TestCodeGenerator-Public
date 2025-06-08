import re
from typing import List

from entity import CodeBlock


def extract_code_blocks(text: str) -> List[CodeBlock]:
    """
    Extracts all code blocks from the Markdown text, returning CodeBlock named tuples.

    Args:
        text: String containing Markdown text

    Returns:
        List of CodeBlock named tuples with language and code
    """
    regex = re.compile(
        r"```(?P<language>[\w\-]*)\n(?P<code>.*?)\n```",
        re.DOTALL | re.MULTILINE,
    )
    code_blocks = []
    if regex.search(text):
        for match in regex.finditer(text):
            code_blocks.append(CodeBlock(language=match.group("language"), code=match.group("code")))
    else:
        code_blocks.append(CodeBlock(language="text", code=text))
    return code_blocks


def extract_code_from_files(file_paths: List[str]) -> List[CodeBlock]:
    """
    Extracts code blocks from multiple files.

    Args:
        file_paths: List of file paths to process

    Returns:
        List of CodeBlock named tuples with language and code
    """
    all_blocks = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                all_blocks.extend(extract_code_blocks(text))
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return all_blocks
