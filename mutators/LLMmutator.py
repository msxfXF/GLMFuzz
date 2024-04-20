import logging
import os
import chatglm_cpp
import time
import json

logger = logging.getLogger()

# get os envrionment variable
model_path = os.environ['GLM']
pipeline = chatglm_cpp.Pipeline(model_path)
# TOOLS = [
#     {
#         "name": "report_mutation",
#         "description": "Report the mutation result",
#         "parameters": {
#             "type": "object",
#             "properties": {"result": {"description": "The mutation result to report", "type": "string"}},
#             "required": ["result"],
#         },
#     },
# ]
system_prompt = '''
# 角色
你是一位测试人员。给定的输入格式，根据格式，保留key，将value进行改变，构造可能触发错误的输入。

## 规则
- 分析每种数据类型的边界值。对于整数，考虑其最大值、最小值和零等。
- 对于字符串，考虑空字符串、特别长的字符串、单字符的字符串等。
- 尝试替换为错误的数据类型。

## 限制
- 只需返回一条满足条件的测试用例。
- key的名称保持不变，但是value的值可以进行修改。
- 返回json格式，不要返回代码！
- 注意：不要输出任何解释，不要输出其他内容!

## 例子1
### 输入
{"raw_content": {"name":"test"}}
### 输出
{"raw_content": {"name":"testtesttesttest"}}

## 例子2
### 输入
{"raw_content": "test"}
### 输出
{"raw_content": ""}

## 例子2
### 输入
{"raw_content": "name: jack\nnumbers:\n\t- 1\n\t- 2\n\t- 3\nage: 30"}
### 输出
{"raw_content": "name: jackjackjackjack\nnumbers:\n\t- -1\n\t- 0\n\t- 999\nage: -1"}
'''


from itertools import combinations

def generate_combinations(list1, list2):
    if len(list1) != len(list2):
        raise ValueError("Lists must have the same length")

    length = len(list1)
    all_combinations = []

    # 枚举从第一个列表中取出元素的所有可能性
    for r in range(length + 1):
        for indices in combinations(range(length), r):
            combo = []
            for i in range(length):
                if i in indices:
                    combo.append(list1[i])
                else:
                    combo.append(list2[i])
            all_combinations.append(combo)

    return all_combinations

def LLMmutator(str_list):
    tmp = []
    for t in str_list:
        text = t
        if isinstance(t, bytes):
            text = t.decode()
        start = time.time()
        history = []
        res = chat(text, history)
        end = time.time()
        logger.info("[Info] Chat: %s Time: %f", res, end - start)

        if isinstance(t, bytes):
            tmp.append(res.encode())
        else:
            tmp.append(res)
    res = generate_combinations(tmp, str_list)
    logger.info("[Info] LLMmutator result: %s", res)
    return res

def chat(text, history=[]):
    h = [chatglm_cpp.ChatMessage(role="system", content=system_prompt)]
    if history != []:
        h.extend(history)
    
    text = json.dumps({"raw_content": text})
    h.append(chatglm_cpp.ChatMessage(role="user", content=text))
    res = pipeline.chat(h, max_new_tokens=max(50, len(text)*2), temperature=1.2)
    try:
        logger.info("[Info] Chat result: %s", res.content)
        r = json.loads(res.content)
        return r["raw_content"]
    except:
        return text


# test
if __name__ == "__main__":
    a = [0] * 5

    a[0] = ""
    a[1] = "提醒：请仔细分析问题要求，给出最为恰当和准确的答案，准确回答问题你将得到奖励，否则你将受到惩罚。我们对你的专业能力充满信心，期待你的答案！"
    a[2] = "提醒：请深入思考问题要求，给出最恰当和精准的答案，准确回答问题的你将获得研究奖励，否则你将需承担研究失误的后果。我们对你专业的研究能力抱有高度期待，等待你的答案！"
    a[3] = "请注意，你需要仔细分析每个选项，以做出最合适的决定。"
    a[4] = "请注意，你需要对每个选项进行深入的思考，以便做出最佳的选择。我们相信你的判断力和决策能力，期待你的答案！"
    rres = []
    for i in range(5):
        t = time.time()
        succ = 0
        resset = set()
        for j in range(30):
            res = LLMmutator([(json.dumps({"name":"jack", "age": 20})+a[i]).encode()])
            try:
                if len(res) > 1 and json.loads(res[1][0].decode()):
                    succ += 1
                    resset.add(res[1][0].decode())
            except:
                pass
        rres.append((succ, time.time() - t, len(resset)))
    print(rres)


