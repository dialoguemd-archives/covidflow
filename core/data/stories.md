## greet
* greet{"metadata":{}}
  - action_greeting_messages

## suspect - severe symptoms
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## suspect - moderate symptoms question
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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
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
  - utter_ask_anything_else_with_test_navigation
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* done
  - utter_test_navigation__come_back
  - action_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## suspect - no symptoms no contact risk
* get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_suspect_no_symptoms_recommendations
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
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
  - daily_ci_enroll_form
  - form{"name": "daily_ci_enroll_form"}
  - form{"name": null}
  - action_tested_positive_not_cured_final_recommendations
  - home_assistance_form
  - form{"name": "home_assistance_form"}
  - form{"name": null}
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

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
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* deny
  - action_test_navigation__anything_else
* done
  - utter_test_navigation__come_back
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
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## tested positive - no symptoms tested less than 14 days no check-in
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* less
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
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## tested positive - no symptoms tested less than 14 days
* tested_positive
  - tested_positive_form
  - form{"name": "tested_positive_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* less
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
  - slot{"symptoms": "none"}
  - action_tested_positive_no_symptoms_recommendations
  - utter_ask_when_tested
* more
  - action_tested_positive_maybe_cured_final_recommendations
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
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
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

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
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* continue OR affirm
  - utter_test_navigation__acknowledge_continue
  - test_navigation_form
  - form{"name": "test_navigation_form"}
  - form{"name": null}
  - action_test_navigation__anything_else
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
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## return for check-in - no symptoms - first symptoms >= 14 days ago
* checkin_return
  - checkin_return_form
  - form{"name": "checkin_return_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* more
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
  - slot{"symptoms": "none"}
  - utter_returning_no_symptoms
  - utter_ask_when_first_symptoms
* less
  - utter_self_isolate_symptom_free
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## QA - failure - no assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny OR done OR fallback
  - utter_try_again_later
  - action_qa_goodbye

## QA - failure - assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* affirm OR get_assessment
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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## QA - failure - test navigation
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* continue OR affirm
  - utter_test_navigation__acknowledge_continue
  - test_navigation_form
  - form{"name": "test_navigation_form"}
  - form{"name": null}
  - action_test_navigation__anything_else
* done OR deny
  - action_goodbye

## QA - success
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## QA - out of distribution
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## QA - success - another question
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## QA - success - assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## QA - out of distribution - another question - test navigation
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* done
  - utter_test_navigation__come_back
  - action_goodbye

## QA - need assessment - no assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## QA - need assessment - assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* affirm OR get_assessment
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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## fallback QA - failure
* greet{"metadata":{}}
  - action_greeting_messages
* fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_ask_how_may_i_help_fallback

## fallback QA - success
* greet{"metadata":{}}
  - action_greeting_messages
* fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## fallback QA - out of distribution
* greet{"metadata":{}}
  - action_greeting_messages
* fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_ask_how_may_i_help_fallback

## fallback QA - no assessment after
* greet{"metadata":{}}
  - action_greeting_messages
* fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## daily check-in - early opt out - done
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else_without_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - early opt out - QA
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* opt_out
  - action_daily_ci_early_opt_out
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## daily check-in - feel worse - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - utter_daily_ci__greet
  - utter_ask_daily_ci__early_opt_out__cancel_ci
* continue OR affirm
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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
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
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* continue OR affirm
  - utter_test_navigation__acknowledge_continue
  - test_navigation_form
  - form{"name": "test_navigation_form"}
  - form{"name": null}
  - action_test_navigation__anything_else
* done OR deny
  - action_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
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
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

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
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

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
* fallback
  - utter_ask_daily_checkin__invalid_id__want_assessment_error
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* done
  - utter_daily_checkin__invalid_id__visit_dialogue
  - action_goodbye

## daily check-in - invalid ID - wants assessment - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm OR get_assessment
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## daily check-in - invalid ID - wants assessment - severe symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* fallback
  - utter_ask_daily_checkin__invalid_id__want_assessment_error
* affirm
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "severe"}
  - action_severe_symptoms_recommendations

## daily check-in - invalid ID - wants assessment - moderate symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm
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
  - utter_ask_anything_else_with_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## daily check-in - invalid ID - wants assessment - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm
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
  - utter_ask_anything_else_with_test_navigation
* done OR deny
  - action_goodbye

## daily check-in - invalid ID - wants assessment - mild symptoms
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_suspect_no_symptoms_recommendations
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment_already_done
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## daily check-in - invalid ID - wants assessment - no symptoms no contact
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm
  - assessment_form
  - form{"name": "assessment_form"}
  - form{"name": null}
  - slot{"self_assess_done": true}
  - slot{"symptoms": "none"}
  - action_suspect_no_symptoms_recommendations
  - action_visit_package
  - utter_ask_anything_else_without_test_navigation
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## daily check-in - invalid ID - wants assessment - no symptoms contact risk
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* affirm
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
  - utter_ask_anything_else_with_test_navigation
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* deny
  - action_test_navigation__anything_else
* done OR deny
  - utter_test_navigation__come_back
  - action_goodbye

## daily check-in - invalid ID - ask question - failure example
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny
  - utter_try_again_later
  - action_qa_goodbye

## daily check-in - invalid ID - ask question - ood two questions
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_try_again_later
  - action_qa_goodbye

## daily check-in - invalid ID - ask question - need assessment
* daily_checkin{"metadata":{}}
  - action_initialize_daily_checkin
  - slot{"invalid_reminder_id": true}
  - utter_ask_daily_checkin__invalid_id__want_assessment
* deny
  - utter_ask_daily_checkin__invalid_id__anything_else
* ask_question
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## Test navigation - done
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* done
  - utter_test_navigation__come_back
  - action_goodbye

## Test navigation - no nothing else
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* deny
  - action_test_navigation__anything_else
* done OR deny
  - utter_test_navigation__come_back
  - action_goodbye

## Test navigation - no ask question
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* deny
  - action_test_navigation__anything_else
* affirm OR ask_question OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "out_of_distribution"}
  - utter_cant_answer
  - utter_ask_different_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## Test navigation - continue fallback come back later
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* fallback
  - action_ask_test_navigation__continue_error
* done
  - utter_test_navigation__come_back
  - action_goodbye

## Test navigation - early ask question - failure
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* fallback
  - action_ask_test_navigation__continue_error
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny OR done OR fallback
  - utter_try_again_later
  - action_qa_goodbye

## Test navigation - early ask question - need assessment
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* fallback
  - action_ask_test_navigation__continue_error
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "need_assessment"}
  - utter_need_assessment
  - utter_ask_assess_to_answer
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## Test navigation - early ask question - success
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* fallback
  - action_ask_test_navigation__continue_error
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* done OR deny
  - utter_please_visit_again
  - action_qa_goodbye

## Test navigation - early ask question - two questions
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* fallback
  - action_ask_test_navigation__continue_error
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "success"}
  - utter_ask_another_question
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny OR done OR fallback
  - utter_try_again_later
  - action_qa_goodbye

## Test navigation - navigate tests - nothing else
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* continue OR affirm
  - utter_test_navigation__acknowledge_continue
  - test_navigation_form
  - form{"name": "test_navigation_form"}
  - form{"name": null}
  - action_test_navigation__anything_else
* done OR deny
  - action_goodbye

## Test navigation - navigate tests - question
* greet{"metadata":{}}
  - action_greeting_messages
* navigate_test_locations
  - action_test_navigation_explanations
  - utter_ask_test_navigation__continue
* continue OR affirm
  - utter_test_navigation__acknowledge_continue
  - test_navigation_form
  - form{"name": "test_navigation_form"}
  - form{"name": null}
  - action_test_navigation__anything_else
* ask_question OR affirm OR fallback
  - question_answering_form
  - form{"name": "question_answering_form"}
  - form{"name": null}
  - slot{"question_answering_status": "failure"}
  - utter_question_answering_error
  - utter_ask_assess_after_error
* deny OR done OR fallback
  - utter_try_again_later
  - action_qa_goodbye
