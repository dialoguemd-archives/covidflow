import json
import logging
import os
from typing import Any, List, Optional, Text

import rasa.utils.io
from rasa.core.actions.action import ACTION_LISTEN_NAME
from rasa.core.domain import Domain
from rasa.core.events import ActionExecuted
from rasa.core.policies.policy import Policy
from rasa.core.trackers import DialogueStateTracker

logger = logging.getLogger(__name__)

MAIN_INTENTS = [
    "done",
    "get_assessment",
    "ask_question",
    "navigate_test_locations",
    "nlu_fallback",
]

AFFIRM_DENY_INTENTS = [
    "deny",
    "affirm",
]

FALLBACK_INTENT = "nlu_fallback"

SUPPORTED_INTENTS_BY_ACTION = {
    "action_greeting_messages": [
        "ask_question",
        "checkin_return",
        "get_assessment",
        "tested_positive",
        "navigate_test_locations",
    ],
    "utter_ask_test_navigation__continue": ["done", "get_assessment", "ask_question"]
    + AFFIRM_DENY_INTENTS,
    "action_test_navigation__anything_else": ["done", "get_assessment", "ask_question"]
    + AFFIRM_DENY_INTENTS,
    "utter_ask_another_question": MAIN_INTENTS + AFFIRM_DENY_INTENTS,
    "utter_ask_different_question": MAIN_INTENTS + AFFIRM_DENY_INTENTS,
    "utter_ask_assess_to_answer": ["done", "get_assessment", "ask_question",]
    + AFFIRM_DENY_INTENTS,
    "utter_ask_assess_after_error": [
        "done",
        "get_assessment",
        "navigate_test_locations",
    ]
    + AFFIRM_DENY_INTENTS,
    "utter_ask_daily_checkin__invalid_id__want_assessment": MAIN_INTENTS
    + AFFIRM_DENY_INTENTS,
    "utter_ask_daily_checkin__invalid_id__anything_else": MAIN_INTENTS
    + AFFIRM_DENY_INTENTS,
    "utter_ask_anything_else_with_test_navigation": MAIN_INTENTS + AFFIRM_DENY_INTENTS,
    "utter_ask_anything_else_without_test_navigation": MAIN_INTENTS
    + AFFIRM_DENY_INTENTS,
    "utter_ask_daily_ci__feel": ["better", "worse", "no_change"],
    "utter_ask_when_tested": AFFIRM_DENY_INTENTS,
    "utter_ask_when_first_symptoms": AFFIRM_DENY_INTENTS,
}

GET_ASSESSMENT_INTENT = "get_assessment"
SELF_ASSESS_DONE_SLOT = "self_assess_done"


class UnsupportedIntentPolicy(Policy):
    """Policy which predicts a fallback action when an unsupported intent is received. """

    @staticmethod
    def _standard_featurizer() -> None:
        return None

    def __init__(
        self,
        priority: int = 6,
        fallback_action_name: Text = "action_unsupported_intent",
    ) -> None:
        """Create a new Unsupported Intent policy.
        Args:
            fallback_action_name: name of the action to execute as a fallback
        """
        super().__init__(priority=priority)

        self.fallback_action_name = fallback_action_name

    def train(
        self,
        training_trackers: List[DialogueStateTracker],
        domain: Domain,
        **kwargs: Any,
    ) -> None:
        """Does nothing. This policy is deterministic."""

        pass

    def fallback_scores(
        self, domain: Domain, fallback_score: float = 1.0
    ) -> List[float]:
        """Prediction scores used if a fallback is necessary."""

        result = self._default_predictions(domain)
        idx = domain.index_for_action(self.fallback_action_name)
        result[idx] = fallback_score
        return result

    def predict_action_probabilities(
        self, tracker: DialogueStateTracker, domain: Domain
    ) -> List[float]:
        """Predicts a fallback action if an unsupported intent is received.
        """

        if tracker.latest_action_name == self.fallback_action_name:
            logger.debug(
                "Predicted 'action_listen' after fallback action '{}'".format(
                    self.fallback_action_name
                )
            )
            result = self._default_predictions(domain)
            idx = domain.index_for_action(ACTION_LISTEN_NAME)
            result[idx] = 1.0

            return result

        if tracker.latest_action_name == ACTION_LISTEN_NAME:
            action_name = _get_previous_action_name(tracker)

            if action_name is None or not action_name in SUPPORTED_INTENTS_BY_ACTION:
                logger.debug("Skipping unsupported intent check")
                return self._default_predictions(domain)

            supported_intents = SUPPORTED_INTENTS_BY_ACTION[action_name]

            intent = _get_intent(tracker)

            if intent in supported_intents or intent == FALLBACK_INTENT:
                if (
                    tracker.get_slot(SELF_ASSESS_DONE_SLOT) is True
                    and intent == GET_ASSESSMENT_INTENT
                ):
                    logger.debug(
                        "Received {} intent but assessment is already done".format(
                            GET_ASSESSMENT_INTENT
                        )
                    )
                    return self.fallback_scores(domain, 1.0)

                logger.debug(
                    "No unexpected intent after action '{}'".format(action_name)
                )
                return self._default_predictions(domain)

            logger.debug(
                "Unexpected intent '{}' after action '{}'".format(intent, action_name)
            )
            return self.fallback_scores(domain, 1.0)

        logger.debug("Skipping unsupported intent check")
        return self._default_predictions(domain)

    def persist(self, path: Text) -> None:
        """Persists the policy to storage."""

        config_file = os.path.join(path, "unsupported_intent_policy.json")
        meta = {
            "priority": self.priority,
            "fallback_action_name": self.fallback_action_name,
        }
        rasa.utils.io.create_directory_for_file(config_file)
        rasa.utils.io.dump_obj_as_json_to_file(config_file, meta)

    @classmethod
    def load(cls, path: Text) -> "UnsupportedIntentPolicy":
        meta = {}
        if os.path.exists(path):
            meta_path = os.path.join(path, "unsupported_intent_policy.json")
            if os.path.isfile(meta_path):
                meta = json.loads(rasa.utils.io.read_file(meta_path))

        return cls(**meta)


def _get_previous_action_name(tracker: DialogueStateTracker) -> Optional[str]:
    previous_action_event = tracker.get_last_event_for(
        ActionExecuted, action_names_to_exclude=[ACTION_LISTEN_NAME]
    )

    return (
        previous_action_event.action_name if previous_action_event is not None else None
    )


def _get_intent(tracker: DialogueStateTracker) -> str:
    return tracker.latest_message.parse_data.get("intent", {}).get("name", "")
