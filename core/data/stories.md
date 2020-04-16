## greet
* greet
  - utter_greet
  - utter_ask_how_may_i_help

## done
* done
  - utter_goodbye

## suspect - severe symptoms
* suspect
 - utter_ask_severe_symptoms
* affirm
  - utter_call_911

## suspect - moderate symptoms
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_long_1
  - utter_monitor_symptoms_long_2
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - moderate symptoms no checkin
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_long_1
  - utter_monitor_symptoms_long_2
  - utter_ask_want_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - mild symptoms no checkin
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_ask_want_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms contact
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_ask_contact
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms contact no checkin
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_ask_contact
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_ask_want_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms no contact travel
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_ask_contact
* deny
  - utter_ask_travel
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms no contact travel no checkin
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_ask_contact
* deny
  - utter_ask_travel
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_ask_want_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms no contact no travel
* suspect
  - utter_ask_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_ask_contact
* deny
  - utter_ask_travel
* deny
  - utter_probably_not_covid
  - utter_social_distancing
  - utter_checkin_if_developments
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## tested positive - severe symptoms
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* affirm
  - utter_call_911

## tested positive - moderate symptoms no check-in
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* affirm
  - utter_moderate_worsen
  - utter_ask_want_checkin
* deny
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - moderate symptoms
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* affirm
  - utter_moderate_worsen
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms worse no check-in
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_did_symptoms_worsen
* affirm
  - utter_moderate_worsen
  - utter_ask_want_checkin
* deny
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms worse
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_did_symptoms_worsen
* affirm
  - utter_moderate_worsen
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms not worse no check-in
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_did_symptoms_worsen
* deny
  - utter_ask_want_checkin
* deny
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms not worse
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_did_symptoms_worsen
* deny
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

# tested positive - no symptoms tested less than 14 days no check-in
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_no_symptoms
  - utter_ask_when_tested
* less
  - utter_ask_want_checkin_no_symptoms
* deny
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

# tested positive - no symptoms tested less than 14 days
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_no_symptoms
  - utter_ask_when_tested
* less
  - utter_ask_want_checkin_no_symptoms
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_checkin_instructions_tested_positive
  - utter_remind_possible_checkin
  - utter_ask_anything_else

# tested positive - cured
* tested_positive
  - utter_self_isolate_tested_positive_1
  - utter_self_isolate_tested_positive_2
  - utter_self_isolate_tested_positive_3
  - utter_self_isolate_tested_positive_4
  - utter_ask_severe_symptoms
* deny
  - utter_ask_moderate_symptoms
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_no_symptoms
  - utter_ask_when_tested
* more
  - utter_maybe_cured
  - utter_ask_anything_else

## QA - failure - ENDS LIKE IF ASSESSMENT ALREADY DONE
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_goodbye

## QA - success - ENDS LIKE IF ASSESSMENT ALREADY DONE
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question

## return for check-in - severe symptoms
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* affirm
  - utter_call_911

## return for check-in - moderate symptoms worse
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* affirm
  - action_set_risk_level
  - utter_ask_symptoms_worsen_returning
* affirm
  - utter_symptoms_worsened_instruction_1_returning
  - utter_symptoms_worsened_instruction_2_returning
  - utter_ask_anything_else

## return for check-in - moderate symptoms - with check-in
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* affirm
  - action_set_risk_level
  - utter_ask_symptoms_worsen_returning
* deny
  - utter_monitor_symptoms_long_1
  - utter_ask_want_checkin_returning
* affirm
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_monitor_symptoms_returning
  - utter_remind_possible_checkin
  - utter_visit_package_returning
  - utter_ask_anything_else

## return for check-in - moderate symptoms - no check-in
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* affirm
  - action_set_risk_level
  - utter_ask_symptoms_worsen_returning
* deny
  - utter_monitor_symptoms_long_1
  - utter_ask_want_checkin_returning
* deny
  - utter_ok
  - utter_monitor_symptoms_returning
  - utter_remind_possible_checkin
  - utter_visit_package_returning
  - utter_ask_anything_else

## return for check-in - mild symptoms - with check-in
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_want_checkin_returning
* affirm
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_monitor_symptoms_returning
  - utter_remind_possible_checkin
  - utter_visit_package_returning
  - utter_ask_anything_else

## return for check-in - mild symptoms - no check-in
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* deny
  - utter_ask_mild_symptoms
* affirm
  - utter_ask_want_checkin_returning
* deny
  - utter_ok
  - utter_monitor_symptoms_returning
  - utter_remind_possible_checkin
  - utter_visit_package_returning
  - utter_ask_anything_else

## return for check-in - no symptoms - first symptoms >= 14 days ago
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_no_symptoms
  - utter_ask_when_first_symptoms
* more
  - utter_not_recent_first_symptoms_instructions
  - utter_ask_anything_else

## return for check-in - no symptoms - first symptoms < 14 days ago
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* deny
  - utter_ask_mild_symptoms
* deny
  - utter_no_symptoms
  - utter_ask_when_first_symptoms
* less
  - utter_recent_first_symptoms_instructions
  - utter_ask_anything_else

## return for check-in - moderate symptoms worse
* checkin_return
  - utter_returning_for_checkin
  - utter_ask_severe_symptoms
* deny
  - utter_no_checkin_instruction_1_returning
  - utter_no_checkin_instruction_2_returning
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_ask_moderate_symptoms_returning
* affirm
  - action_set_risk_level
  - utter_ask_symptoms_worsen_returning
* affirm
  - utter_symptoms_worsened_instruction_1_returning
  - utter_symptoms_worsened_instruction_2_returning
  - utter_ask_anything_else
