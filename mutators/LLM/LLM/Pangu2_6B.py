from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import  gc 
import torch

pipeline_ins = pipeline(
		Tasks.text_generation,
		model='OpenICommunity/pangu_2_6B',
        model_revision='v1.0.3',
        device="cuda:0"
)

def chat(input_text):
    return pipeline_ins(input_text, max_length=256)[0]["generated_text"]

def unload():
    global model, tokenizer
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == '__main__':
    print(chat("user:帮我讲个故事\nassistant:"))