from typing import Tuple

import os
import openai


def parse_connection_and_dataset_name(s: str) -> Tuple[str, str]:
    segments = s.split("/")
    if len(segments) == 2:
        connection, name = segments
    elif len(segments) == 1:
        connection = "file_uploads"
        name = segments[0]
    else:
        raise ValueError(
            f"Got invalid dataset reference {s} - expected either <dataset_name> or "
            f"<connection_name>/<dataset_name>"
        )

    return connection, name


def strip_api_from_gateway_url(url: str) -> str:
    """ Strips 'api.' from the URL if it starts with 'https://api.'"""
    # Check if the URL starts with "https://api"
    if url.startswith("https://api"):
        # Replace "https://api" with "https://"
        return url.replace("https://api.", "https://", 1)
    return url


def validate_openai_base_model_support(base_model: str, client: openai.Client) -> None:
    """Validates that the user specified base model to use for augmentation is a valid OpenAI model
    and one that we support for augmentation.

    Inputs:
    :param base_model: (str) The OpenAI base model.
    :param client: (openai.Client) The authenticated OpenAI client.

    Returns:
    :return: None
    :raises: ValueError if the model is not supported by OpenAI.
    :raises: ValueError if the model isn't supported by Predibase.
    """
    is_valid_model = any(model_info.id == base_model for model_info in client.models.list().data)
    if not is_valid_model:
        raise ValueError(
            f"The model '{base_model}' is not a valid OpenAI model. Please pass a valid model name.",
        )

    supported_openai_models = {"gpt-4-1106-preview", "gpt-4-0125-preview", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"}
    if base_model not in supported_openai_models:
        raise ValueError(
            f"The model '{base_model}' is not supported by Predibase. Choose from {supported_openai_models}.",
        )


def validate_openai_api_key(openai_api_key: str) -> openai.Client:
    """Validates that an OpenAI API key is provided and is valid.

    Inputs:
    :param openai_api_key: (str) The OpenAI API key.

    Returns:
    :return: None
    :raises: ValueError if an invalid OpenAI API key is provided.
    :raises: ValueError if an OpenAI API key is not provided.
    """
    # Validate that an OpenAI API key is provided and is valid
    if openai_api_key is None:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key is None:
            raise ValueError(
                "An OpenAI API key must be provided to augment a dataset. Please pass the key as an argument through "
                "`openai_api_key` or set the OPENAI_API_KEY environment variable.",
            )

    try:
        import openai

        client = openai.Client(api_key=openai_api_key)
        client.models.list()
    except openai.AuthenticationError:
        raise ValueError(
            "An invalid OpenAI API key was provided. Please pass a valid key through `openai_api_key` "
            "or set the OPENAI_API_KEY in your environment",
        )

    return client
