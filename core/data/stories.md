## greet
* greet{"metadata":{}}
  - utter_greet
  - utter_ask_how_may_i_help

## suspect - severe symptoms
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## suspect - moderate symptoms
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_moderate_symptoms_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done
  - action_qa_goodbye

## suspect - moderate symptoms no checkin
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_moderate_symptoms_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## suspect - mild symptoms no checkin
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## suspect - mild symptoms
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## suspect - no symptoms contact risk
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - slot{"has_contact_risk": true}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## suspect - no symptoms contact risk no checkin
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - slot{"has_contact_risk": true}
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_suspect_mild_symptoms_exposure_final_recommendations
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## suspect - no symptoms no contact risk
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_suspect_no_symptoms_recommendations
  - action_visit_package
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
  - action_qa_goodbye

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
  - action_tested_positive_mild_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## tested positive - moderate symptoms
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - action_tested_positive_mild_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## tested positive - mild symptoms worse no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* affirm
  - action_tested_positive_mild_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
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
* done
  - action_qa_goodbye

## tested positive - mild symptoms worse
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* affirm
  - action_tested_positive_mild_moderate_symptoms_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## tested positive - mild symptoms not worse no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* deny
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

## tested positive - mild symptoms not worse
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "mild"}
  - utter_ask_symptoms_worsened
* deny
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

# tested positive - no symptoms tested less than 14 days no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* less
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

# tested positive - no symptoms tested less than 14 days
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* less
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else
* done
  - utter_goodbye

# tested positive - cured
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* more
  - action_tested_positive_maybe_cured_final_recommendations
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
  - action_qa_goodbye

## return for check-in - severe symptoms
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## return for check-in - moderate symptoms worse
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - utter_ask_symptoms_worsened
* affirm
  - utter_contact_healthcare_professional
  - utter_contact_healthcare_professional_options
  - utter_goodbye

## return for check-in - moderate symptoms - with check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - utter_ask_symptoms_worsened
* deny
  - action_returning_symptoms_not_worsened_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
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
  - action_qa_goodbye

## return for check-in - moderate symptoms - no check-in
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "moderate"}
  - utter_ask_symptoms_worsened
* deny
  - action_returning_symptoms_not_worsened_recommendations
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - utter_remind_monitor_symptoms_temperature
  - utter_remind_possible_checkin
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - utter_ask_anything_else
* done
  - utter_goodbye

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
  - utter_ask_anything_else
* done
  - utter_goodbye

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
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done
  - action_qa_goodbye

## return for check-in - no symptoms - first symptoms >= 14 days ago
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_no_symptoms
  - utter_ask_when_first_symptoms
* more
  - utter_social_distancing_leave_home
  - utter_ask_anything_else
* done
  - utter_goodbye

## return for check-in - no symptoms - first symptoms < 14 days ago
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
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
  - action_qa_goodbye

## QA - failure - no assessment after
* greet{"metadata":{}}
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
  - action_qa_goodbye

## QA - success
* greet{"metadata":{}}
  - utter_greet
  - utter_ask_how_may_i_help
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_what_next_after_answer
* done
  - action_qa_goodbye

## QA - success - another question
* greet{"metadata":{}}
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
* done
  - action_qa_goodbye

## QA - need_assessment - no assessment after
* greet{"metadata":{}}
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
  - action_qa_goodbye

## daily check-in - early opt out - done
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - early opt out - QA
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_what_next_after_answer
* done
  - action_qa_goodbye

## daily check-in - feel worse - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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

## daily check-in - feel worse - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done
  - action_qa_goodbye

## daily check-in - feel worse - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - action_qa_goodbye

## daily check-in - feel worse - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* worse
  - daily_ci_feel_worse_form
  - form{"name": "daily_ci_feel_worse_form"}
  - form{"name": null}
  - slot{"symptoms": "none"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - feel no change - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - feel no change - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - utter_ask_anything_else
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done
  - action_qa_goodbye

## daily check-in - feel no change - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* no_change
  - daily_ci_feel_no_change_form
  - form{"name": "daily_ci_feel_no_change_form"}
  - form{"name": null}
  - slot{"symptoms": "none"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - feel better - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - feel better - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
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
  - utter_ask_anything_else
* done
  - utter_goodbye

## daily check-in - feel better - no symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* continue
  - utter_daily_ci__early_opt_out__acknowledge_continue_ci
  - utter_ask_daily_ci__feel
* better
  - daily_ci_feel_better_form
  - form{"name": "daily_ci_feel_better_form"}
  - form{"name": null}
  - slot{"symptoms": "none"}
  - slot{"self_assess_done": true}
  - daily_ci_keep_or_cancel_form
  - form{"name": "daily_ci_keep_or_cancel_form"}
  - form{"name": null}
  - utter_ask_anything_else
* ask_question
  - utter_can_help_with_questions
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye
