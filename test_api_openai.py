from openai import OpenAI
import os

os.environ["OPENAI_API_KEY"] = ""
client = OpenAI()



def analise(text):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": "You extract specified data into JSON data. If no information provided leave empty. If the price in description is estimated, the car might be damaged, if not really sure leave empty. Spell country names correct in polish"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "info_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "Import_Country": {
                            "description": "Country (country name) from which the car was imported from if so",
                            "type": "string"
                        },
                        "Running": {
                            "description": "Is the car running?",
                            "type": "boolean"
                        },
                        "Damaged": {
                            "description": "Is the car damaged?",
                            "type": "boolean"
                        },
                        "additionalProperties": False
                    }
                }
            }
        }
    )

    # print(response.choices[0].message.content)
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    print(f"used {prompt_tokens} prompt tokens generating {prompt_tokens/1000000 * 0.125 * 20_000} $ ")
    print(f"used {completion_tokens} output tokens generating {prompt_tokens/1000000 * 0.6*20_000} $ ")
 # ok 2 dolary na ourput i 0. 8 dolara na input
    return response.choices[0].message.content




#trzeba sprawdzić skuteczność