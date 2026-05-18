import json
from dataclasses import dataclass
from openai import OpenAI
from src.config import settings

client = OpenAI(api_key=settings.openai_api_key)


@dataclass
class PhotoEvalResult:
    is_true: bool
    prob_true: float 
    prob_false: float 
    reason: str | None
    token_usage: int


def evaluate_photo(prompt: str, image_url: str) -> PhotoEvalResult:
    resp = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        text={"format": {"type": "json_object"}},
    )
    token_usage = resp.usage
    try:
        data = json.loads(resp.output_text)
        return PhotoEvalResult(
            is_true=bool(data.get("is_true")),
            prob_true=data.get("prob_true"),
            prob_false=data.get("prob_false"),
            reason=data.get("reason"),
            token_usage=token_usage
        )
    except Exception as e:
        raise ValueError(f"invalid model response: {e}")
