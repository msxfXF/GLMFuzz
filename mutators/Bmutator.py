import logging
import os
from BiLSTM.model import *
import random
import itertools

# 获取当然文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
# 配置日志
logger = logging.getLogger()
bilstm = BiLSTM()

# 求最小编辑距离
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

#  从list中寻找最短编辑距离的字符串
def find_closest_string(target, string_list):
    min_distance = float('inf')
    closest_strings = []

    for s in string_list:
        distance = levenshtein_distance(target, s)
        if distance < min_distance:
            min_distance = distance
            closest_strings = [s]
        elif distance == min_distance:
            closest_strings.append(s)

    return closest_strings, min_distance

# 求两个最小编辑距离，并返回编辑路径
def levenshtein_distance_with_path(s1, s2):
    if isinstance(s1, str):
        s1 = s1.encode()
    if isinstance(s2, str):
        s2 = s2.encode()

    rows = len(s1) + 1
    cols = len(s2) + 1
    dist_matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Initialize matrix
    for i in range(1, rows):
        dist_matrix[i][0] = i
    for j in range(1, cols):
        dist_matrix[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):
            if s1[i-1] == s2[j-1]:
                cost = 0
            else:
                cost = 1
            dist_matrix[i][j] = min(dist_matrix[i-1][j] + 1,      # Deletion
                                    dist_matrix[i][j-1] + 1,      # Insertion
                                    dist_matrix[i-1][j-1] + cost) # Substitution

    # Backtrack to find the path
    i, j = rows - 1, cols - 1
    path = []

    while i > 0 or j > 0:
        current_cost = dist_matrix[i][j]
        if i > 0 and dist_matrix[i-1][j] + 1 == current_cost:
            path.append(('delete', i-1, bytes([s1[i-1]])))  # Deletion
            i -= 1
        elif j > 0 and dist_matrix[i][j-1] + 1 == current_cost:
            path.append(('insert', j-1, bytes([s2[j-1]])))  # Insertion
            j -= 1
        else:
            if s1[i-1] != s2[j-1]:
                # path.append(('substitute', i-1, s1[i-1], s2[j-1]))  # Substitution
                path.append(('substitute', i-1, bytes([s2[j-1]])))  # Substitution
            i -= 1
            j -= 1

    return dist_matrix[-1][-1], list(reversed(path))

def FindEditPath(s1, string_list):
    logger.info("[Info] FindEditPath, s1:%s, string_list:%s", s1, string_list)
    closest_strings, closest_distance = find_closest_string(s1, string_list)
    res = []
    for s2 in closest_strings:
        distance, edits = levenshtein_distance_with_path(s2, s1)
        res.append((s2, distance, edits))
    return res

def Bmutate(bin_list):
    poss, bytes = bilstm.get_mutate_pos_byte(bin_list)
    # logger.info("[Debug] Bmutate, pos:%s, byte:%s, bin_list:%s", str(poss), str(bytes), str(bin_list))
    if len(bin_list) == 0:
        logger.error("[Error] Bmutate, bin_list is empty, %s", str(bin_list))
        return bin_list
    # C10_3，进行10次变异
    combinations = itertools.combinations(poss, 3)
    res = [bin_list]
    for pos in combinations:
        for i in range(10):
            tmp = tiny_havoc(bin_list, pos, random.choice(bytes))
            res.append(tmp)
    logger.info("[Info] Bmutate, res len: %d", len(res))
    return res

def tiny_havoc(bin_list, pos_list, ex_byte):
    all_bytes = b''.join(bin_list)
    if len(all_bytes) == 0:
        # logger.error("[Error] tiny_havoc, all_bytes is empty, %s", str(bin_list))
        return bin_list
    # 确保pos在all_bytes长度范围内
    pos_list = [pos % len(all_bytes) for pos in pos_list]
    logger.debug("[Info] tiny_havoc, bin_list:%s, pos_list:%s, ex_byte:%s", str(bin_list), str(pos_list), str(ex_byte))

    # 变异操作1: 翻转单个位
    def flip_bit(array, position):
        # 计算要翻转的位所在的字节位置和位位置
        byte_pos = position // 8
        bit_pos = position % 8
        # 翻转位
        array[byte_pos] ^= 1 << bit_pos
        return array

    # 变异操作2: 将字节设置为有趣的值
    def set_to_interesting_byte(array, position):
        interesting_values = [0x80, 0xFF, 0x00, 0x01, 0x10, 0x20, 0x40, 0x64, 0x7F]
        array[position] = random.choice(interesting_values)
        return array

    # 变异操作3: 随机减去一个值
    def randomly_subtract(array, position):
        array[position] = (array[position] - random.randint(0, 255)) % 256
        return array

    # 变异操作4: 随机增加一个值
    def randomly_add(array, position):
        array[position] = (array[position] + random.randint(0, 255)) % 256
        return array

    # 变异操作5: 设置一个随机字节为随机值
    def set_random_byte_to_random_value(array, position):
        array[position] = int.from_bytes(ex_byte, 'big')
        return array

    # 转换all_bytes成一个可修改的bytearray
    mutable_bytes = bytearray(all_bytes)

    # 随机选择一个变异操作
    operations = [
        flip_bit,
        set_to_interesting_byte,
        randomly_subtract,
        randomly_add,
        set_random_byte_to_random_value
    ]
    for pos in pos_list:
        operation_to_apply = random.choice(operations)
        mutable_bytes = operation_to_apply(mutable_bytes, pos)

    # 将bytearray转换回不同的部分
    mutated_bin_list = []
    current_pos = 0
    for original_bytes in bin_list:
        length = len(original_bytes)
        mutated_bin_list.append(bytes(mutable_bytes[current_pos:current_pos+length]))
        current_pos += length

    return mutated_bin_list

def Update(state, target_positions, target_next_char, cov, tbytes, score):
    bilstm.learn(state, target_positions, target_next_char, cov, tbytes, score)

if __name__ == "__main__":
    # # Example usage:
    # given_string = "example"
    # string_list = ["axample", "simple", "exmple", "examine"]
    # closest_strings, closest_distance = find_closest_string(given_string, string_list)
    # print("Closest strings:", closest_strings)
    # print("Shortest edit distance:", closest_distance)

    # for s2 in closest_strings:
    #     distance, edits = levenshtein_distance_with_path(given_string, s2)
    #     print(f"Edit distance: {distance}")
    #     print("Edits needed:")
    #     for edit in edits:
    #         print(edit)

    # # 测试最短编辑距离
    # print(FindEditPath(b"example", [b"axample", b"simple", b"exmple", b"examine"]))
    
    
    # # 测试 tiny_havoc
    # bin_list_example = [b'abcd', b'e1100']
    # pos_example = 5
    # byte_example = 42
    # mutated_list = tiny_havoc(bin_list_example, pos_example, byte_example)
    # print(mutated_list)

    # 测试 Bmutate
    Bmutate([b'abcd', b'e1100'])
