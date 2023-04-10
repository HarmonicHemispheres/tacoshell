
import openai
from typing import List
from rich.table import Table
import datetime

MODEL_DESC = {
    "davinci": "This is one of the most powerful models in the OpenAI lineup, designed to perform a wide range of natural language processing tasks, including text generation, language translation, and text completion. It is capable of handling complex and nuanced language, and is trained on a large and diverse dataset.",

    "babbage": "This is another model in the OpenAI lineup that is designed to perform various language processing tasks, including text generation and language understanding. It is a smaller and less powerful model than davinci, but still capable of generating coherent and natural language.",

    "ada": "This model is designed to focus on the task of text generation, specifically in the context of scientific writing. It is trained on a large corpus of scientific literature and is designed to be able to generate scientifically accurate and coherent text.",

    "curie-instruct-beta": "This model is designed specifically for generating instructional content, such as manuals and tutorials. It is trained on a large dataset of instructional material and is designed to generate clear and concise instructional text.",

    "whisper-1": "This model is an internal OpenAI research project that is not publicly available, so it is difficult to say what specific task it is designed to perform."
}

class AiEngine:
    def __init__(self, openai_key: str, model: str = "gpt-3.5-turbo"):
        self.openai_key = openai_key
        self.model = model

        openai.api_key = self.openai_key

    def get_resp(self, que: str, messages=[]):
        if not self.openai_key:
            raise Exception("No OpenAi Developer Key Found!")
        
        # prepare query
        user_content = {"role": "user", "content": que}
        messages.append(user_content)

        # list models
        # models = openai.Model.list()

        # print the first model's id
        # print(models.data[0].id)

        # create a completion
        completion = openai.ChatCompletion.create(
            model=self.model, 
            messages=messages,
            )
        messages.append({"role": "assistant", "content": completion.choices[0].message.content})
        return messages
    

    def get_code(self, text):
        if "```" in text:
            return text.split("```")[1].split("\n")[1].split("```")[0]
        else:
            return text
        
    
    def get_chat_models(self) -> List[str]:

        models = openai.Model.list()
        model_names = [m.get("id") for m in models.get("data")]

        table = Table(title="OpenAi Models")
        table.add_column("id", style="blue")
        table.add_column("Owner", style="green")
        table.add_column("Allow Fine Tuning", style="green")
        # table.add_column("Allow Create Engine", style="green")
        # table.add_column("Allow Sampling", style="green")
        table.add_column("Created", justify="right", style="cyan")

        for m in models.get("data"):
            date = datetime.datetime.fromtimestamp(float(m.get("created")))
            table.add_row(
                m.get("id"),
                m.get("owned_by"),
                str(m.get("permission")[0].get("allow_fine_tuning")),
                # str(m.get("permission")[0].get("allow_create_engine")),
                # str(m.get("permission")[0].get("allow_sampling")),
                date.strftime('%Y-%m-%d %H:%M:%S'),
            )

        return model_names, table

