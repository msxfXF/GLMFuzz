from modelscope import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch
import gc

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-1_8B-Chat", revision='master', torch_dtype=torch.float16 , trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-1_8B-Chat", revision='master', torch_dtype=torch.float16, device_map="auto", trust_remote_code=True).eval()

def chat(input_text):
    response, _ = model.chat(tokenizer, input_text, history=None)
    return response

def unload():
    global model, tokenizer
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == '__main__':
    print(chat("你是一个精通计算机的专家，用python实现两种算法，求解斐波那契数列问题，并给出注释和时间复杂度分析"))