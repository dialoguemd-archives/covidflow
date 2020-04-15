## greet
* greet
  - utter_greet
  - utter_how_may_i_help

## return for check-in
* checkin_return
  - utter_returning_for_checkin

## tested positive
* tested_positive
 - utter_tested_positive

## severe symptoms
* suspect
 - utter_enquire_severe_symptoms
* affirm
  - utter_call_911

## moderate symptoms
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_long_1
  - utter_monitor_symptoms_long_2
  - utter_offer_checkin
* affirm
  - utter_daily_checkin_enroll

## moderate symptoms no checkin
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_long_1
  - utter_monitor_symptoms_long_2
  - utter_offer_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_goodbye

## mild symptoms no checkin
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_offer_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_goodbye

## no symptoms contact
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* deny
  - utter_enquire_contact
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_offer_checkin
* affirm
  - utter_daily_checkin_enroll

## no symptoms contact no checkin
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* deny
  - utter_enquire_contact
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_offer_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_goodbye

## no symptoms no contact travel
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* deny
  - utter_enquire_contact
* deny
  - utter_enquire_travel
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_offer_checkin
* affirm
  - utter_daily_checkin_enroll

## no symptoms no contact travel no checkin
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* deny
  - utter_enquire_contact
* deny
  - utter_enquire_travel
* affirm
  - utter_self_isolate
  - utter_monitor_symptoms_short
  - utter_offer_checkin
* deny
  - utter_no_checkin_instruction_1
  - utter_no_checkin_instruction_2
  - utter_remind_possible_checkin
  - action_set_risk_level
  - utter_visit_package
  - utter_goodbye

## no symptoms no contact no travel
* suspect
  - utter_enquire_severe_symptoms
* deny
  - province_age_form
  - form{"name": "province_age_form"}
  - form{"name": null}
  - utter_enquire_moderate_symptoms
* deny
  - utter_enquire_mild_symptoms
* deny
  - utter_enquire_contact
* deny
  - utter_enquire_travel
* deny
  - utter_probably_not_covid
  - utter_social_distancing
  - utter_checkin_if_developments
  - action_set_risk_level
  - utter_visit_package
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye
