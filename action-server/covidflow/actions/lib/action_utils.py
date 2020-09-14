from rasa_sdk import Tracker


def get_intent(tracker: Tracker) -> str:
    return tracker.latest_message.get("intent", {}).get("name", "")
