import pandas as pd
import re
import json
import time
import typing

def load_data()->pd.DataFrame:
    prompt = '''
    As a deep learning model, your task is to assist me in performing some fuzz testing and creating test cases. Given that our goal is to unearth potential errors, you need to intentionally mutate the input text and provide a matched-format output. It's important to note that "intentional mutation" does not mean random mutation - you need to use your experience and creativity to speculate which mutations are more likely to trigger underlying errors.

No matter if the input text is JSON, YAML, plain text, or any other format, you must return a mutated version of the text that matches the input format. That is to say, if the input is JSON, then the output should also be JSON; if the input is simple text, then the output should also be simple text, and so forth.

Consider the following example, where the input is a JSON object:

```json
{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com"
}
```

A potential mutated output could be:

```json
{
  "name": "John Doe1",
  "age": -1,
  "email": "john.doe@example"
}
```

In this case, we have made three mutations: added a numeric character to the "name" field, set the "age" field to a possibly unreasonable value -1, and modified the email address to an invalid email address.

Methods:
- Change certain values.
- Introduce new fields.
- Confuse data types. 
- Use an unusual long string.
- Insert special characters
- Change the expected format.

Now, regardless of the format of the input text, I need you to make some meaningful mutations in a similar way to assist us in fuzz testing.
NOTE: Ensure randomness, Mix up a variety of Methods! Please return only the changed results. DO NOT Provide ANY additional explanation or output.
'''

    data = '```json \n {"product": "Apple", "price": 1.20, "stock": 100}\n ```'
    df = pd.DataFrame([data])
    return df, prompt

def test_qwen():
    from modelscope import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-1_8B-Chat", revision='master', trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-1_8B-Chat", device_map="auto", trust_remote_code=True).eval()

    response, history = model.chat(tokenizer, "", history=None, system="")
    print(response)

def find_json(data:str, prefix:str="json")->list:
    pattern = rf'```({prefix})?\n((?:.|\n)*?)```'
    matches = re.findall(pattern, data, re.DOTALL)
    res = [i[1] for i in matches]
    return res

# ret: success, fail, success_rate, time_cost
def cacluate_vaild(chat:typing.Callable, prompt:str, times:int=10)->(int, int, float, float):
   # 统计有效 json 数 和 无效 json数
    vailed_json = 0
    invailed_json = 0
    # 统计时间
    start = time.time()

    for _ in range(times):
        res = chat(prompt)
        res_list = find_json(res)
        for j in res_list:
            # print(j)
            if is_json(j):
                vailed_json += 1
            else:
                invailed_json += 1
                # print(j)
    end = time.time()

    # 统计百分比
    print(f"vailed_json: {vailed_json}")
    print(f"invailed_json: {invailed_json}")
    print(f"vailed_json: {vailed_json/(vailed_json+invailed_json)}")
    print(f"time_cost: {end-start}")
    return vailed_json, invailed_json, vailed_json/(vailed_json+invailed_json), end-start

def is_json(myjson):
  try:
    _ = json.loads(myjson)
  except ValueError as e:
    return False
  return True

if __name__ == '__main__':
    find_json("```\n{\"product\": \"Apple\", \"price\": 1.20, \"stock\": 100}\n```\n"*2)