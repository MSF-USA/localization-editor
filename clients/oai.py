import openai
import json
from typing import Any, Dict, List, Optional


def get_structured_response(
        messages: List[Dict[str, str]],
        model_id: str,
        user: Optional[Dict[str, Any]],
        json_schema: Optional[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 500
) -> Dict[str, Any]:
    content = None  # Initialize content to ensure it's always defined
    try:

        response = openai.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
              "type": "json_schema",
              "json_schema": {
                "name": "StructuredResponse",
                "strict": True,
                "schema": json_schema,
              },
            },
        )


        content = response.choices[0].message.content.strip()
        print(content)
        print(response.json())

        if (isinstance(content, str)):
            output = json.loads(content)
        else:
            output = content
        return output
    except Exception as e:
        print("Failed to parse OpenAI response as JSON:", content)
        print(f"Exception: {str(e)}")
        raise Exception("Failed to parse output") from e


def generate_localization_object(
        phrase: str,
        phrase_locale: str,
        context: Optional[str] = None,
        model_id: str = "gpt-4o",
        user: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    iso_codes = [
        'ar', 'bn', 'ca', 'de', 'en', 'es', 'fi', 'fr', 'he', 'id',
        'it', 'ja', 'ko', 'pl', 'pt', 'ro', 'ru', 'si', 'sv', 'te',
        'tr', 'vi', 'zh'
    ]
    target_languages = iso_codes.copy()
    if phrase_locale in target_languages:
        target_languages.remove(phrase_locale)

    context_str = f"Context: {context}" if context else "No additional context provided."

    codes = '\n'.join([f'  "{code}": "translation in {code}",' for code in target_languages])

    prompt = f"""You are a translation assistant. You are given a phrase in '{phrase_locale}' and you are to translate the phrase into the following target languages: {', '.join(target_languages)}, identified by their ISO 639-1 codes.

Phrase: "{phrase}"

{context_str}

Provide the translations in JSON format, mapping the ISO code to the translation.

Output format:
{{
{codes}
}}
"""

    messages = [
        {
            "role": "system",
            "content": "You are an assistant that provides translations of a given phrase into multiple languages."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    properties = {code: {"type": "string"} for code in target_languages}

    json_schema = {
        "type": "object",
        "properties": properties,
        "required": list(properties.keys()),
        "additionalProperties": False
    }

    response = get_structured_response(
        messages=messages,
        model_id=model_id,
        user=user,
        json_schema=json_schema,
        temperature=0.7,
        max_tokens=None
    )

    return response
