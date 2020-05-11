from typing import Any, Dict, Optional, Text


def get_provincial_811(province: Optional[str], domain: Dict[Text, Any]) -> str:
    responses = domain.get("responses", {})
    provincial_811 = responses.get(f"provincial_811_{province}") or responses.get(
        "provincial_811_default"
    )

    return provincial_811[0]["text"]
