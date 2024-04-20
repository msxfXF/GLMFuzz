# export PYTHONPATH="/Users/xf/实验改进/mutators"
# export AFL_PYTHON_MODULE="main"
# /usr/local/bin/afl-fuzz -i afl_in -o afl_out ./target @@ 
import os
import random
import logging
import time

from mutator import Mutator

# 获取当然文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
# 配置日志
logging.basicConfig(
    filename=os.path.join(current_dir, 'mutator.log'),
    filemode='a', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()
mutator = Mutator()

# 初始化函数，当AFL++启动时被调用（可选）
def init(seed):
    # 可以在这里初始化你的mutator
    random.seed(seed)  # 使用seed来初始化随机数生成器
    logger.debug("[Debug] Init mutator: %s", seed)

# 描述当前变异的函数（可选）
def describe(max_description_length):
    description = "LLM and BiLSTM"
    return description

# 这个函数会执行你的自定义变异
def fuzz(buf, add_buf, max_size):
    logger.debug("[Debug] Start mutator, buf:%s, add_buf:%s, max_size:%d", buf, add_buf, max_size)
    
    # time.sleep(10)
    if max_size <= len(buf):
        logger.error("[Debug] Raw input length is too long, return directly")
        return buf

    mutator.mutate(buf)
    buf = buf[:max_size]

    logger.debug("[Debug] End mutator, res:%s", buf)
    return buf

def fuzz_count(buf):
    return mutator.get_mutate_times(buf)

# 当变异完成后，运行 target 前调用
def post_process(buf):
    mutator.before_run(buf)
    return buf

# # 当AFL++结束时被调用（可选）
def post_run(trace_bits, cov, tbytes):
    mutator.post_run(trace_bits, cov, tbytes)

# # havoc变异和它的概率（可选）
# def havoc_mutation(buf, max_size):
#     return fuzz(buf, None, max_size)

# def havoc_mutation_probability():
#     # 返回havoc变异被调用的概率，默认为6%
#     return 6
