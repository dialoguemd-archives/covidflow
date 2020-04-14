from rasa_sdk import Action


class ActionCheerUp(Action):
    def name(self):
        return "action_cheer_up"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(image="https://i.imgur.com/nGF1K8f.jpg")
