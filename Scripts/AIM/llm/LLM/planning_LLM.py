
from datetime import datetime
from BaseLLM import BaseLLM


class PlanningLLM(BaseLLM):

    def __init__(self, model_name, prompts):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompts"]["planning"],
            user_prompt=prompts["user_prompt_templates"]["planning"]
        )

        self.user_prompt = prompts["user_prompt_templates"]["planning"]

    def build_prompt(self, data):

        return self.user_prompt.format(
            planning_data=data['planning_data'],
            datetime=data['datetime'],
            satellite_passages=data['satellite_passages'],
            sequence_of_events=data['soe'],
            conversation_history=self.session_history
        )

if __name__ == '__main__':


    xml = XMLPlanningCleaner()
    path = "C:\\Users\\anton\\Documents\\python projects\\FUNES\\Funes\\data examples\\planning example\\IME01_10022026152801829_TIME_TAGGED.xml"

    plan = xml.xml_plan_filter(path, ['Mission', 'PlanValidityTimeWindow', 'Satellite', 'Action'], limit = 30)
    print("PLANNING DATA: \n", xml.get_text_from_xml(plan), "\n\n")

    my_data = {"planning_data": xml.get_text_from_xml(plan), "datetime": datetime.now().strftime('%Y:%m:%d_%H:%M:%S')}

    planning_model = 'llama-3.1-8b-instant' #'llama-3.3-70b-versatile'
    planningLLM = PlanningLLM(model_name=planning_model)
    planningLLM.load_data(my_data)

    user_input = ''
    while user_input != '0':
        print("\n- FUNES:", planningLLM.speak())
        planningLLM.add_user_response(input('\n- YOU:'))
