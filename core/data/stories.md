## tested positive - severe symptoms
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## tested positive - moderate symptoms no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - moderate symptoms
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - mild symptoms two questions
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* deny OR done
  - action_goodbye

## tested positive - mild symptoms
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - mild symptoms no check-in one question
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - no symptoms tested less than 14 days no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* deny
  - utter_when_tested_less_14_recommendation
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - no symptoms tested less than 14 days error
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* nlu_fallback
  - utter_ask_when_tested_error
* deny
  - utter_when_tested_less_14_recommendation
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - cured
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* affirm
  - action_tested_positive_maybe_cured_final_recommendations
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## tested positive - cured - error
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* nlu_fallback
  - utter_ask_when_tested_error
* affirm
  - action_tested_positive_maybe_cured_final_recommendations
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - severe symptoms
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## return for check-in - moderate symptoms - with check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - moderate symptoms - no check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - mild symptoms - with check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - mild symptoms - no check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - no symptoms - first symptoms >= 14 days ago
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* affirm
  - utter_social_distancing_leave_home
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - no symptoms - first symptoms >= 14 days ago error
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* nlu_fallback
  - utter_ask_when_first_symptoms_error
* affirm
  - utter_social_distancing_leave_home
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - no symptoms - first symptoms < 14 days ago
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* deny
  - utter_self_isolate_symptom_free
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## return for check-in - no symptoms - first symptoms < 14 days ago error
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "nothing"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* nlu_fallback
  - utter_ask_when_first_symptoms_error
* deny
  - utter_self_isolate_symptom_free
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

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
