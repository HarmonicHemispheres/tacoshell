
import openai

class AiEngine:
    def __init__(self, openai_key: str):
        self.openai_key = openai_key

        openai.api_key = self.openai_key

    def get_resp(self, que: str):
        if not self.openai_key:
            raise Exception("No OpenAi Developer Key Found!")
        
        # list models
        # models = openai.Model.list()

        # print the first model's id
        # print(models.data[0].id)

        # create a completion
        # completion = openai.Completion.create(model="ada", prompt="Hello world")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": que}])

        # print the completion
        # for choice in completion.choices: 
        #     print(f"[D] --> {choice.message.content}")

        return completion.choices[0].message.content
    

    def get_code(self, text):
        if "```" in text:
            return text.split("```")[1].split("```")[0]
        else:
            return text