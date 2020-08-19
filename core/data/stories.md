## daily check-in - early opt out - done
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - early opt out - QA
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel worse - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "severe"}
  - slot{"self_assess_done": true}
  - action_severe_symptoms_recommendations

## daily check-in - feel worse - error - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* nlu_fallback
  - utter_ask_daily_ci__feel_error
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "severe"}
  - slot{"self_assess_done": true}
  - action_severe_symptoms_recommendations

## daily check-in - feel worse - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "moderate"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel worse - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "mild"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel worse - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "nothing"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel no change - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* no_change
  - daily_ci_feel_no_change_form
  - form{"name": "daily_ci_feel_no_change_form"}
  - form{"name": null}
  - slot{"symptoms": "moderate"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel no change - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* no_change
  - daily_ci_feel_no_change_form
  - form{"name": "daily_ci_feel_no_change_form"}
  - form{"name": null}
  - slot{"symptoms": "mild"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel no change - error - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* nlu_fallback
  - utter_ask_daily_ci__feel_error
* no_change
  - daily_ci_feel_no_change_form
  - form{"name": "daily_ci_feel_no_change_form"}
  - form{"name": null}
  - slot{"symptoms": "mild"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel no change - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* no_change
  - daily_ci_feel_no_change_form
  - form{"name": "daily_ci_feel_no_change_form"}
  - form{"name": null}
  - slot{"symptoms": "nothing"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel better - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* better
  - daily_ci_feel_better_form
  - form{"name": "daily_ci_feel_better_form"}
  - form{"name": null}
  - slot{"symptoms": "moderate"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel better - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* better
  - daily_ci_feel_better_form
  - form{"name": "daily_ci_feel_better_form"}
  - form{"name": null}
  - slot{"symptoms": "mild"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel better - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* better
  - daily_ci_feel_better_form
  - form{"name": "daily_ci_feel_better_form"}
  - form{"name": null}
  - slot{"symptoms": "nothing"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - feel better - error - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__continue_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* nlu_fallback
  - utter_ask_daily_ci__feel_error
* better
  - daily_ci_feel_better_form
  - form{"name": "daily_ci_feel_better_form"}
  - form{"name": null}
  - slot{"symptoms": "nothing"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - invalid ID - nothing else
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* done
  - utter_daily_checkin__invalid_id__visit_dialogue
  - action_goodbye

## daily check-in - invalid ID - error - nothing else
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* nlu_fallback
  - utter_ask_daily_checkin__invalid_id__want_assessment_error
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* done
  - utter_daily_checkin__invalid_id__visit_dialogue
  - action_goodbye
