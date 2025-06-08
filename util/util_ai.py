from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Union, Optional

from anthropic import Anthropic
from loguru import logger
from openai import OpenAI

from entity import ModelProvider, MAX_TOKEN_MAP
from .util_image import encode_image, media_type
from .util_qt import read_model_settings

__DEFAULT_MAX_TOKENS = 8 * 1024


def chat(*,
         system: Optional[str] = None,
         text: Optional[Union[str, List[str]]] = None,
         image_url: Optional[Union[str, List[str]]] = None,
         timeout: int = 120) -> str:
    """
    Generate chat from text and image

    Args:
        system: system message
        text: chat text
        image_url: chat image url (file url or http url)
        timeout: timeout in seconds

    Returns:
        chat response
    """
    try:
        model_settings = read_model_settings()
    except Exception as e:
        logger.error(f"Error loading model settings: {e}")
        raise ValueError(f"Error loading model settings: {e}") from e

    def _task() -> str:
        match model_settings.provider:
            case ModelProvider.OpenAI:
                return chat_openai(system,
                                   text,
                                   image_url,
                                   model_settings.openai_model,
                                   MAX_TOKEN_MAP.get(model_settings.openai_model, __DEFAULT_MAX_TOKENS),
                                   model_settings.openai_api_host,
                                   model_settings.openai_api_key,
                                   model_settings.temperature)
            case ModelProvider.Claude:
                return chat_claude(system,
                                   text,
                                   image_url,
                                   model_settings.claude_model,
                                   MAX_TOKEN_MAP.get(model_settings.claude_model, __DEFAULT_MAX_TOKENS),
                                   model_settings.claude_api_host,
                                   model_settings.claude_api_key,
                                   model_settings.temperature)
            case ModelProvider.SiliconFlow:
                return chat_siliconflow(system,
                                        text,
                                        image_url,
                                        model_settings.siliconflow_model,
                                        MAX_TOKEN_MAP.get(model_settings.siliconflow_model, __DEFAULT_MAX_TOKENS),
                                        model_settings.siliconflow_api_host,
                                        model_settings.siliconflow_api_key,
                                        model_settings.temperature)
            case _:
                raise ValueError(f"Unsupported provider: {model_settings.provider}")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_task)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            future.cancel()
            raise TimeoutError(f"Chat request timed out after {timeout} seconds")


def __build_message(system: Optional[str],
                    text: Union[str, List[str], None],
                    image_url: Union[str, List[str], None],
                    *,
                    provider: ModelProvider) -> List[Dict[str, Any]]:
    """
    Build the message for chat

    Args:
        system: system message
        text: chat text
        image_url: chat image url
        provider: chat provider

    Returns:
        message
    """
    if not text and not image_url:
        raise ValueError("At least chat something...")

    def __build_text(_text: Union[str, List[str], None]):
        """
        Build text for chat

        Args:
            _text: chat text

        Returns:
            text
        """
        if not _text:
            return []

        if isinstance(_text, str):
            return [{"type": "text", "text": _text}]
        elif isinstance(_text, List):
            return [{"type": "text", "text": t} for t in _text]

    def __build_image_url(_image_url: Union[str, List[str], None]):
        """
        Build image url for chat

        Args:
            _image_url: chat image url

        Returns:
            image url
        """
        if not _image_url:
            return []

        if isinstance(_image_url, str):
            match provider:
                case ModelProvider.OpenAI:
                    return [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type(_image_url)};base64,{encode_image(_image_url)}"
                            }
                        }
                    ]
                case ModelProvider.Claude:
                    return [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type(_image_url),
                                "data": encode_image(_image_url)
                            }
                        }
                    ]
                case ModelProvider.SiliconFlow:
                    return [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type(_image_url)};base64,{encode_image(_image_url)}"
                            }
                        }
                    ]
                case _:
                    raise ValueError(f"Unsupported provider: {provider}")
        elif isinstance(_image_url, List):
            match provider:
                case ModelProvider.OpenAI:
                    return [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type(url)};base64,{encode_image(url)}"
                            }
                        }
                        for url in _image_url
                    ]
                case ModelProvider.Claude:
                    return [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type(url),
                                "data": encode_image(url)
                            }
                        }
                        for url in _image_url
                    ]
                case ModelProvider.SiliconFlow:
                    return [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type(url)};base64,{encode_image(url)}"
                            }
                        }
                        for url in _image_url
                    ]
                case _:
                    raise ValueError(f"Unsupported provider: {provider}")

    if system:
        wrapper = [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": [
                ]
            }
        ]
    else:
        wrapper = [
            {
                "role": "user",
                "content": [
                ]
            }
        ]
    content_ = wrapper[-1]["content"]
    assert isinstance(content_, list)
    content_.extend(__build_text(text))
    content_.extend(__build_image_url(image_url))
    return wrapper


def chat_openai(system: Optional[str],
                text: Union[str, List[str], None],
                image_url: Union[str, List[str], None],
                model: str,
                max_tokens: int,
                base_url: str,
                api_key: str,
                temperature: float = 0.7) -> str:
    """
    Chat with OpenAI model
    """
    client = OpenAI(base_url=base_url, api_key=api_key)

    chat_completion = client.chat.completions.create(
        max_tokens=max_tokens,
        messages=__build_message(system, text, image_url, provider=ModelProvider.OpenAI),
        model=model,
        temperature=temperature,
    )

    return chat_completion.choices[0].message.content


def chat_claude(system: Optional[str],
                text: Union[str, List[str], None],
                image_url: Union[str, List[str], None],
                model: str,
                max_tokens: int,
                base_url: str,
                api_key: str,
                temperature: float = 0.7) -> str:
    """
    Chat with Claude model
    """
    client = Anthropic(base_url=base_url, api_key=api_key)

    chat_completion = client.messages.create(
        max_tokens=max_tokens,
        system=system,
        messages=__build_message(None, text, image_url, provider=ModelProvider.Claude),
        model=model,
        temperature=temperature,
    )

    return chat_completion.content[0].text


def chat_siliconflow(system: Optional[str],
                     text: Union[str, List[str], None],
                     image_url: Union[str, List[str], None],
                     model: str,
                     max_tokens: int,
                     base_url: str,
                     api_key: str,
                     temperature: float = 0.7) -> str:
    """
    Chat with SiliconFlow model
    SiliconFlow API is compatible with OpenAI API
    """
    client = OpenAI(base_url=base_url, api_key=api_key)

    chat_completion = client.chat.completions.create(
        max_tokens=max_tokens // 4 * 2,
        messages=__build_message(system, text, image_url, provider=ModelProvider.OpenAI),
        model=model,
        temperature=temperature,
    )

    return chat_completion.choices[0].message.content
