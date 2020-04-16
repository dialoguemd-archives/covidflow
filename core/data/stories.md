## greet
* greet
  - utter_greet
  - utter_ask_how_may_i_help

## return for check-in
* checkin_return
  - utter_returning_for_checkin

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye

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
  - utter_goodbye
