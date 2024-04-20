from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer,GenerationConfig
import torch
import gc


model_dir = snapshot_download("baichuan-inc/Baichuan2-7B-Chat", revision='v1.0.4')
tokenizer = AutoTokenizer.from_pretrained(model_dir, device_map="auto", torch_dtype=torch.float16,
                              trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto", torch_dtype=torch.float16, 
                              trust_remote_code=True)
model.generation_config = GenerationConfig.from_pretrained(model_dir)



def chat(input_text):
    messages = []
    messages.append({"role": "user", "content": input_text})
    response = model.chat(tokenizer, messages)
    return response

def unload():
    global model, tokenizer
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()


if __name__ == '__main__':
    print(chat("你是一个精通计算机的专家，用python实现两种算法，求解 斐波那契数列问题，并给出注释和时间复杂度分析"))
    unload()