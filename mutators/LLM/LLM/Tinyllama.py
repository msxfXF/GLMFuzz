from modelscope import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch
import gc
import re

tokenizer = AutoTokenizer.from_pretrained("AI-ModelScope/TinyLlama-1.1B-Chat-v1.0",  trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("AI-ModelScope/TinyLlama-1.1B-Chat-v1.0", trust_remote_code=True).eval()

def chat(input_text):
    # call model.generate()
    text = f"<|user|>\n{input_text} </s>\n<|assistant|>\n"
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    output = model.generate(input_ids)
    ret = tokenizer.decode(output[0])
    return get_assistant(ret)

def get_assistant(input_text):
    extracted_txt = re.findall('<\|assistant\|\>(.*?)<\/s>', input_text, re.S)
    extracted_txt = ''.join(extracted_txt)
    if extracted_txt.strip() == '':
        print(input_text)
    return extracted_txt

def unload():
    global model, tokenizer
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == '__main__':
    for i in range(100):
        chat("Tell me a story")