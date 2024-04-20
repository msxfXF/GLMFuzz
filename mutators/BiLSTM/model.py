import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch
import logging
import os
import time
import math

logger = logging.getLogger()

def bytes_to_one_hot(byte_array, seq_len=512, input_size=256):
    # 初始化一个全0的张量，形状是 [seq_len, input_size]
    one_hot_tensor = torch.zeros(seq_len, input_size)
    for i, byte in enumerate(byte_array):
        one_hot_tensor[i][byte] = 1.0
    one_hot_tensor = one_hot_tensor.unsqueeze(0)
    return one_hot_tensor

def one_hot_to_bytes_topm(one_hot_tensor, top_m, dim=2):
    # 找出每行one-hot向量中最大的m个值及其索引
    top_m_values, top_m_indices = torch.topk(one_hot_tensor, top_m, dim=dim)
    
    # 将这些索引转换为bytes
    # 因为我们感兴趣的是索引值，因此我们忽略了top_m_values
    batch_size, seq_len, _ = top_m_indices.size()
    results_bytes_topm = []
    
    for b in range(batch_size):
        topm_list = []
        if dim == 2:
            byte_list = [bytes([top_m_indices[b, 0, i].item()]) for i in range(top_m)]
        else:
            byte_list = [top_m_indices[b, i, 0].item() for i in range(top_m)]
        topm_list.append(byte_list)
        results_bytes_topm.append(topm_list)
    
    return results_bytes_topm

class PolicyNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout, nhead, transformer_layers):
        super(PolicyNetwork, self).__init__()
        self.input_size = input_size

        # 双向LSTM
        self.lstm = nn.LSTM(input_size=input_size,
                            hidden_size=hidden_size,
                            num_layers=num_layers,
                            batch_first=True,
                            bidirectional=True,
                            dropout=dropout if num_layers > 1 else 0.0)

        self.dropout = nn.Dropout(dropout)

        # Transformer编码器
        transformer_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size * 2,
            nhead=nhead,
            dropout=dropout
        )
        self.transformer_encoder = nn.TransformerEncoder(
            transformer_layer,
            num_layers=transformer_layers
        )

        # 定义针对原序列每个位置定义的操作敏感位置
        self.action_pos = nn.Linear(hidden_size*2, 1) 

        # 用于预测下一个字符的top M个可能性
        self.action_char = nn.Linear(hidden_size*2, input_size)

    def forward(self, x):
        # BiLSTM层
        lstm_out, (h_n, c_n) = self.lstm(x)
        lstm_out = self.dropout(lstm_out)

        # Transformer层
        transformer_out = self.transformer_encoder(lstm_out.transpose(0, 1)).transpose(0, 1)

        # 预测删除、新增、替换操作敏感位置的概率
        action_pos_out = self.action_pos(transformer_out)  # 这里的输出形状会是 [batch_size, seq_len, 1]
        action_pos_out = F.softmax(action_pos_out, dim=1)
        # torch.Size([1, 512, 1])

        # 预测下一个字符的top M个可能性
        action_char_out = self.action_char(transformer_out[:,-1,:])  # 只取序列最后一个时间步的输出
        action_char_out = action_char_out.view(-1, 1, self.input_size)
        action_char_out = F.softmax(action_char_out, dim=2)  # 在每个可能的下一个字符上应用softmax
        # torch.Size([1, 1, 256])
        return action_pos_out, action_char_out

class BiLSTM():
    def __init__(self, nhead = 8, num_layers = 2, transformer_layers = 1):
        state_size = 256
        hidden_size = 128
        dropout = 0.1
        self.policy_network = PolicyNetwork(state_size, hidden_size, num_layers, dropout, nhead, transformer_layers)
        self.optimizer = optim.Adam(self.policy_network.parameters(), lr=0.01)

    def learn(self, state, action_positions, action_next_char, cov, tbytes, score):
        # 数据处理
        state = b''.join(state)
        state = bytes_to_one_hot(state)
        action_next_char = int.from_bytes(action_next_char, 'big')
        action_position_tensor = torch.tensor([action_positions], dtype=torch.long)
        action_next_char_tensor = torch.tensor([int(action_next_char)], dtype=torch.long)

        self.policy_network.train()  # 设置为训练模式

        # 执行一次前向传播获得模型预测
        sensitive_position_out, next_char_out = self.policy_network(state)

        # 更新函数
        criterion_position = torch.nn.CrossEntropyLoss()
        sensitive_position_out = sensitive_position_out.squeeze(-1)  # 形状现在应该是 [1, 512]
        reward_position = criterion_position(sensitive_position_out, action_position_tensor)

        criterion_next_char = torch.nn.CrossEntropyLoss()
        next_char_out = next_char_out.squeeze(1)  # 结果应该是一个形状为[1]的张量
        reward_next_char = criterion_next_char(next_char_out, action_next_char_tensor)            

        # 归一化 cov、tbytes、score，覆盖率、路径数、AFL Score
        cov_log = math.log10(cov) if cov > 0 else 0.1
        cov = cov / (10 ** math.ceil(cov_log))

        tbytes_log = math.log10(tbytes) if tbytes > 0 else 0.1
        tbytes = tbytes / (10 ** math.ceil(tbytes_log))

        score_log = math.log10(score) if score > 0 else 0.1
        score = score / (10 ** math.ceil(score_log))

        # 最终 reward
        reward_total = (reward_position + 0.1 * reward_next_char) * (cov + tbytes + score)/3

        # 更新模型
        self.optimizer.zero_grad()  # 清空之前的梯度
        reward_total.backward()
        self.optimizer.step()       # 更新模型权重
        logger.info("[Info] Update model, loss: %.5f", reward_total.item())


    def get_mutate_pos_byte(self, input_data):
        input_data = b''.join(input_data)
        example_input = bytes_to_one_hot(input_data)
        # output 表示敏感位置，next_char_output 表示下一个字符的top M个可能性
        output, next_char_output = self.policy_network(example_input)
        result_bytes_topm = one_hot_to_bytes_topm(next_char_output, 3)
        result_pos_topm = one_hot_to_bytes_topm(output, 10, 1)
        for seq in range(len(result_bytes_topm)):
            logger.debug("[Info] Position %d: %s", seq, result_bytes_topm[0][seq])
        logger.info("[Info] Get mutate position and next char, result_pos_topm: %s, result_bytes_topm: %s", str(result_pos_topm), str(result_bytes_topm))
        return result_pos_topm[0][0], result_bytes_topm[0][0]
    


if __name__ == "__main__":
    
    indata = [b'hello']
    # for i in range(10000):
    #     pos, next_char = m.get_mutate_pos_byte(indata)
    #     pos = pos[0]
    #     print(next_char)
    #     m.learn(indata, pos, next_char[0])
    #     m.learn(indata, pos, next_char[1])
    #     m.learn(indata, pos, next_char[2])

    nheads = [1, 2, 4, 8]
    num_layers = [1, 2, 3]
    transformer_layers = [1, 2, 3]
    ret = []
    args = [(i,j,k) for i in nheads for j in num_layers for k in transformer_layers]
    for arg in args:
        print(arg)
        t = time.time()
        m = BiLSTM(nhead=arg[0], num_layers=arg[1], transformer_layers=arg[2])
        for i in range(100):
            pos, next_char = m.get_mutate_pos_byte(indata)
        ret.append((arg, time.time() - t))
    print(ret)
        
