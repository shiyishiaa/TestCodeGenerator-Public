from enum import Enum, unique
from typing import Dict, Union

from pydantic import BaseModel, Field


@unique
class OpenAIModel(str, Enum):
    """
    OpenAI Vision-Capable Models supporting multimodal input (text + images) as of April 2025
    """

    O1 = "o1"
    """OpenAI's flagship reasoning model with 34% performance improvement and 60% cost reduction. Supports: 
    - Function calling
    - Structured JSON outputs
    - Visual recognition
    - Multi-modal integration (text+images)"""

    GPT_4_5_PREVIEW = "gpt-4.5-preview"
    """Enhanced version of GPT-4 with expanded unsupervised learning (code-name 'Orion'). Features:
    - Reduced hallucinations
    - Improved emotional nuance
    - 32k token context window
    - Vision API integration"""

    GPT_4O = "gpt-4o"
    """Optimized variant for mobile/web integration. Key capabilities:
    - Real-time search augmentation
    - Map visualization support
    - Voice search compatibility
    - Free tier availability"""

    GPT_4O_MINI = "gpt-4o-mini"
    """Cost-efficient version with STEM specialization. Specifications:
    - 24% faster response time
    - Multi-language processing
    - Limited to text-only outputs
    - Three intensity tiers (Low/Medium/High)"""

    GPT_4_TURBO = "gpt-4-turbo"
    """Legacy model with extended context handling. Maintains:
    - September 2021 knowledge cutoff
    - Backward compatibility
    - 32k token processing
    - Basic vision capabilities"""


@unique
class ClaudeModel(str, Enum):
    """
    Anthropic Claude Model Family
    Latest models as of April 2025 with vision and multilingual capabilities
    """

    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    """Most intelligent model with toggleable extended thinking"""

    CLAUDE_3_5_SONNET_UPGRADED = "claude-3-5-sonnet-20241022"
    """High intelligence model with 200K context window (Oct 2024 version)"""

    CLAUDE_3_5_SONNET_ORIGINAL = "claude-3-5-sonnet-20240620"
    """Previous generation Sonnet model (June 2024 version)"""

    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    """Fastest model with July 2024 knowledge cutoff"""

    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    """Powerful model for complex tasks (Feb 2024 release)"""

    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    """Compact model with near-instant responsiveness"""


@unique
class SiliconFlowModel(str, Enum):
    """
    SiliconFlow Vision-Capable Models supporting multimodal input (text + images) as of April 2025

    Ref: https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions#vlm
    """

    DEEPSEEK_AI_DEEPSEEK_VL2 = "deepseek-ai/deepseek-vl2"

    QWEN_QVQ_72B_PREVIEW = "Qwen/QVQ-72B-Preview"

    QWEN_QWEN2_VL_72B_INSTRUCT = "Qwen/Qwen2-VL-72B-Instruct"

    PRO_QWEN_QWEN2_VL_7B_INSTRUCT = "Pro/Qwen/Qwen2-VL-7B-Instruct"

    QWEN_QWEN2_5_VL_32B_INSTRUCT = "Qwen/Qwen2.5-VL-32B-Instruct"

    QWEN_QWEN2_5_VL_72B_INSTRUCT = "Qwen/Qwen2.5-VL-72B-Instruct"

    PRO_QWEN_QWEN2_5_VL_7B_INSTRUCT = "Pro/Qwen/Qwen2.5-VL-7B-Instruct"


@unique
class ModelProvider(str, Enum):
    OpenAI = 'OpenAI',
    Claude = 'Claude',
    SiliconFlow = 'SiliconFlow',


__GROUP_PROPERTY__ = "qsettings_group"

MAX_TOKEN_MAP: Dict[str, int] = {
    OpenAIModel.O1: 10_0000,
    OpenAIModel.GPT_4_5_PREVIEW: 16 * 1024,
    OpenAIModel.GPT_4O: 16 * 1024,
    OpenAIModel.GPT_4O_MINI: 16 * 1024,
    OpenAIModel.GPT_4_TURBO: 4 * 1024,

    ClaudeModel.CLAUDE_3_7_SONNET: 8 * 1024,
    ClaudeModel.CLAUDE_3_5_SONNET_UPGRADED: 8 * 1024,
    ClaudeModel.CLAUDE_3_5_SONNET_ORIGINAL: 8 * 1024,
    ClaudeModel.CLAUDE_3_5_HAIKU: 8 * 1024,
    ClaudeModel.CLAUDE_3_OPUS: 4 * 1024,
    ClaudeModel.CLAUDE_3_HAIKU: 4 * 1024,

    SiliconFlowModel.DEEPSEEK_AI_DEEPSEEK_VL2: 4 * 1024,
    SiliconFlowModel.QWEN_QVQ_72B_PREVIEW: 16 * 1024,
    SiliconFlowModel.QWEN_QWEN2_VL_72B_INSTRUCT: 4 * 1024,
    SiliconFlowModel.PRO_QWEN_QWEN2_VL_7B_INSTRUCT: 4 * 1024,
    SiliconFlowModel.QWEN_QWEN2_5_VL_32B_INSTRUCT: 8 * 1024,
    SiliconFlowModel.QWEN_QWEN2_5_VL_72B_INSTRUCT: 4 * 1024,
    SiliconFlowModel.PRO_QWEN_QWEN2_5_VL_7B_INSTRUCT: 4 * 1024,
}


class ModelSettings(BaseModel):
    # Provider Configuration
    provider: ModelProvider = Field(
        default=ModelProvider.OpenAI,
        description="Active AI service provider",
        json_schema_extra={__GROUP_PROPERTY__: "Provider"}
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default='',
        description="API key for OpenAI services",
        json_schema_extra={__GROUP_PROPERTY__: "OpenAI"}
    )
    openai_api_host: str = Field(
        default='',
        description="Custom API endpoint host",
        json_schema_extra={__GROUP_PROPERTY__: "OpenAI"}
    )
    openai_model: Union[OpenAIModel, str] = Field(
        default=OpenAIModel.O1,
        description="Selected OpenAI model variant",
        json_schema_extra={__GROUP_PROPERTY__: "OpenAI"}
    )

    # Claude Configuration
    claude_api_key: str = Field(
        default='',
        description="API key for Anthropic services",
        json_schema_extra={__GROUP_PROPERTY__: "Claude"}
    )
    claude_api_host: str = Field(
        default='',
        description="Custom Claude API endpoint",
        json_schema_extra={__GROUP_PROPERTY__: "Claude"}
    )
    claude_model: Union[ClaudeModel, str] = Field(
        default=ClaudeModel.CLAUDE_3_7_SONNET,
        description="Selected Claude model variant",
        json_schema_extra={__GROUP_PROPERTY__: "Claude"}
    )

    # SiliconFlow Configuration
    siliconflow_api_key: str = Field(
        default='',
        description="API key for SiliconFlow services",
        json_schema_extra={__GROUP_PROPERTY__: "SiliconFlow"}
    )
    siliconflow_api_host: str = Field(
        default='',
        description="Custom SiliconFlow endpoint",
        json_schema_extra={__GROUP_PROPERTY__: "SiliconFlow"}
    )
    siliconflow_model: Union[SiliconFlowModel, str] = Field(
        default=SiliconFlowModel.DEEPSEEK_AI_DEEPSEEK_VL2,
        description="Selected SiliconFlow model",
        json_schema_extra={__GROUP_PROPERTY__: "SiliconFlow"}
    )

    # Context Management
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model creativity temperature",
        json_schema_extra={__GROUP_PROPERTY__: "Context"}
    )
