import anthropic
from openai import OpenAI

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.chat import ChatHistory, ChatMessage
from src.comet.adapters.response import ResponseResult, ResponseStatus
from src.comet.ai.models.claude_model import ClaudeModelParams
from src.comet.ai.models.gpt_model import GPTModelParams
from src.comet.utils.decorators.error import handle_ai_service_errors

anthropic_client = anthropic.Anthropic()
openai_client = OpenAI()
logger = parse_args_and_setup_logging()


@handle_ai_service_errors
async def generate_anthropic_response(
    system_prompt: str,
    prompt: list[ChatMessage],
    model_params: ClaudeModelParams,
) -> ResponseResult:
    """Generate a response from the claude model.

    Parameters
    ----------
    system_prompt : str
        The system instruction.

    prompt : list[ChatMessage]
        A list of chat messages forming the conversation history.

    model_params : ClaudeModelParams
        The model parameters.
    """
    convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
    result = anthropic_client.messages.create(
        # mypy(arg-type): expected "Iterable[MessageParam]"
        messages=convo,  # type: ignore
        # mypy(arg-type): expected ModelParam
        # but I specified it as app_commands.Choice[int] | str
        model=model_params.model,  # type: ignore
        max_tokens=model_params.max_tokens,
        system=system_prompt,
        temperature=model_params.temperature,
        top_p=model_params.top_p,
    )
    # mypy(union-attr): has no attribute "text"
    claude_result = result.content[0].text  # type: ignore
    return ResponseResult(status=ResponseStatus.SUCCESS, result=claude_result)


@handle_ai_service_errors
async def generate_openai_response(
    system_prompt: str,
    prompt: list[ChatMessage],
    model_params: GPTModelParams,
) -> ResponseResult:
    """Generate a response from the GPT model.

    Parameters
    ----------
    system_prompt : str
        The system instruction.

    prompt : list[ChatMessage]
        A list of chat messages forming the conversation history.

    model_params : GPTModelParams
        Configuration settings for the model, including parameters like
        max_tokens, temperature and top-p sampling.
    """
    convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
    full_prompt = [{"role": "developer", "content": system_prompt}, *convo]
    completion = openai_client.chat.completions.create(
        # mypy(arg-type): expected loooooooooooooooooong union type
        messages=full_prompt,  # type: ignore
        # mypy(arg-type): expected ChatModel | str
        # but I specified it as app_commands.Choice[int] | str
        model=model_params.model,  # type: ignore
        max_tokens=model_params.max_tokens,
        temperature=model_params.temperature,
        top_p=model_params.top_p,
    )
    completion_result = completion.choices[0].message.content
    return ResponseResult(status=ResponseStatus.SUCCESS, result=completion_result)
