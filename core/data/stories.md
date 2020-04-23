## greet
* greet
  - utter_greet
  - utter_ask_how_may_i_help

## done
* done
  - utter_goodbye

## suspect - severe symptoms
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## suspect - moderate symptoms
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_suspect_moderate_symptoms_recommendations
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_moderate_symptoms_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question

## suspect - moderate symptoms no checkin
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_suspect_moderate_symptoms_recommendations
  - utter_ask_want_checkin
* deny
  - action_suspect_moderate_symptoms_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - mild symptoms no checkin
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - action_suspect_mild_symptoms_exposure_recommendations
  - utter_ask_want_checkin
* deny
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - utter_goodbye

## suspect - no symptoms contact
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_ask_contact
* affirm{"contact": true}
  - action_suspect_mild_symptoms_exposure_recommendations
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms contact no checkin
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_ask_contact
* affirm{"contact": true}
  - action_suspect_mild_symptoms_exposure_recommendations
  - utter_ask_want_checkin
* deny
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms no contact travel
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_ask_contact
* deny{"contact": false}
  - utter_ask_travel
* affirm
  - action_suspect_mild_symptoms_exposure_recommendations
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done
  - utter_please_visit_again
  - utter_goodbye

## suspect - no symptoms no contact travel no checkin
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_ask_contact
* deny{"contact": false}
  - utter_ask_travel
* affirm
  - action_suspect_mild_symptoms_exposure_recommendations
  - utter_ask_want_checkin
* deny
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## suspect - no symptoms no contact no travel
* suspect OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_ask_contact
* deny{"contact": false}
  - utter_ask_travel
* deny
  - action_suspect_no_symptoms_recommendations
  - action_set_risk_level
  - utter_visit_package
  - utter_ask_anything_else

## tested positive - severe symptoms
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - utter_call_911

## tested positive - moderate symptoms no check-in
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - utter_symptoms_worsen_emergency_assistance
  - utter_ask_want_checkin
* deny
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - moderate symptoms
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - utter_symptoms_worsen_emergency_assistance
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms worse no check-in
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* affirm
  - utter_symptoms_worsen_emergency_assistance
  - utter_ask_want_checkin
* deny
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question

## tested positive - mild symptoms worse
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* affirm
  - utter_symptoms_worsen_emergency_assistance
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms not worse no check-in
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* deny
  - utter_ask_want_checkin
* deny
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

## tested positive - mild symptoms not worse
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* deny
  - utter_ask_want_checkin
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

# tested positive - no symptoms tested less than 14 days no check-in
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_tested
* less
  - utter_ask_want_checkin_no_symptoms
* deny
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - utter_goodbye

# tested positive - no symptoms tested less than 14 days
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_tested
* less
  - utter_ask_want_checkin_no_symptoms
* affirm
  - utter_daily_checkin_enroll
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_acknowledge_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_ask_anything_else

# tested positive - cured
* tested_positive
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_tested
* more
  - utter_maybe_cured
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done
  - utter_please_visit_again
  - utter_goodbye

## return for check-in - severe symptoms
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - utter_call_911

## return for check-in - moderate symptoms worse
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_set_risk_level
  - utter_ask_symptoms_worsened
* affirm
  - utter_contact_healthcare_professional
  - utter_contact_healthcare_professional_options
  - utter_goodbye

## return for check-in - moderate symptoms - with check-in
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_set_risk_level
  - utter_ask_symptoms_worsened
* deny
  - utter_symptoms_worsen_emergency
  - utter_ask_want_checkin_acknowledge
* affirm
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done
  - utter_please_visit_again
  - utter_goodbye

## return for check-in - moderate symptoms - no check-in
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_set_risk_level
  - utter_ask_symptoms_worsened
* deny
  - utter_symptoms_worsen_emergency
  - utter_ask_want_checkin_acknowledge
* deny
  - utter_ok
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_visit_package
  - utter_ask_anything_else

## return for check-in - mild symptoms - with check-in
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_want_checkin_acknowledge
* affirm
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_visit_package
  - utter_ask_anything_else

## return for check-in - mild symptoms - no check-in
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_want_checkin_acknowledge
* deny
  - utter_ok
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - utter_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question

## return for check-in - no symptoms - first symptoms >= 14 days ago
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_first_symptoms
* more
  - utter_social_distancing_leave_home
  - utter_ask_anything_else

## return for check-in - no symptoms - first symptoms < 14 days ago
* checkin_return
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_first_symptoms
* less
  - utter_self_isolate_symptom_free
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - utter_goodbye

## QA - failure - no assessment after
* greet
  - utter_greet
  - utter_ask_how_may_i_help
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny
  - utter_try_again_later
  - utter_goodbye

## QA - success
* greet
  - utter_greet
  - utter_ask_how_may_i_help
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_what_next_after_answer

## QA - success - another question
* greet
  - utter_greet
  - utter_ask_how_may_i_help
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_what_next_after_answer
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_what_next_after_answer

## QA - need_assessment - no assessment after
* greet
  - utter_greet
  - utter_ask_how_may_i_help
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* done
  - utter_please_visit_again
  - utter_goodbye

## daily check-in
* daily_checkin{"metadata": "data"}
  - utter_greet_daily_checkin
  - utter_ask_how_do_you_feel
