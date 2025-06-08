ORGANIZATION = "SYSU.SSE"
APPLICATION = "Code Generator"
VERSION = "1.0.0"
DESCRIPTION = "Webpage Test Code Generator Application"

# ----------------------------------------------------------------------------------------------------------------------

PROMPT_CONTENT = """Role: Website screenshot analysis expert
Task: Analyze a website screenshot and give a highly detailed description.

Focus Areas:
1. Layout: Overall structure, section placement.
2. Sections: Content, purpose, hierarchy.
3. Navigation: Menus, buttons, links — their location and function.
4. Media: Images, videos, animations — size, placement, relevance.
5. Text: Headings, paragraphs, lists — font, size, style, position.
6. Visuals: Color scheme, style, distinctive design elements.
7. Unique Features: Special traits that enhance UX.

Constraints:
- Be specific and detailed.
- Only refer to content visible in the screenshot.
- Organize your answer into a paragraph.
- Don't use markdown format.
- Follow a step-by-step approach."""

PROMPT_CODE = """Role: Website test case expert
Task: Generate comprehensive test cases covering all key functionalities and scenarios.

Focus Areas:
1. Components: Test various aspects of website elements.
2. Priority: Emphasize critical properties; skip trivial ones unless important.
3. Data: Validate input, storage, and retrieval.
4. User Actions: Simulate clicks, inputs, navigation.
5. Edge Cases: Handle creative/unexpected scenarios.

Constraints:
- Output test code only, no explanations.
- Use image descriptions and information if provided.
"""

PROMPT_HALLUCINATION = """Role: Expert in frontend test
Task: Detect if the test code is not correct and the hallucination exists in the test code given the screenshot and source code.

Focus Areas:
1. Test code: Test if unknown or irrelevant code snippet is in the test code.
2. Source code: Where test code should align with.
3. Screenshot: The screenshot of the website.

Constraints:
- Output True if hallucination exists, otherwise False.
"""

PROMPT_RELATED = """
- Compare between images because they might be related and can transform to each other.
"""

# ----------------------------------------------------------------------------------------------------------------------

__all__ = [
    # project info
    "ORGANIZATION",
    "APPLICATION",
    "VERSION",
    "DESCRIPTION",

    # prompt
    "PROMPT_CONTENT",
    "PROMPT_CODE",
    "PROMPT_HALLUCINATION",
    "PROMPT_RELATED",
]
