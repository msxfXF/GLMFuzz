import math
import logging

logger = logging.getLogger()
def calculate_entropy(data):
    if len(data) == 0:
        return 0.0
    occurrences = [0]*256
    for byte in data:
        occurrences[byte] += 1
    entropy = 0
    for count in occurrences:
        if count > 0:
            p = 1.0*count / len(data)
            entropy -= p * math.log(p, 256)
    return entropy

def annotate_text_binary(data, windowSize=4, entropyThreshold=0.5):
    annotations = [1] * len(data)  
    for i in range(windowSize, len(data)+1):
        segment = data[i-windowSize:i]
        if all(32 <= byte <= 126 for byte in segment) and calculate_entropy(segment) < entropyThreshold:
            annotations[i-windowSize:i] = [0]*windowSize  # 标记为文本
    return annotations

# 测试
def split_text_binary(data, annotations):
    bin_list = []
    str_list = []
    str_buffer, bin_buffer = b"", b""
    for i in range(len(data)):
        if annotations[i] == 0:  # 文本部分
            if bin_buffer:
                bin_list.append(bin_buffer)
                bin_buffer = b""
            str_buffer += bytes([data[i]])
        else:  # 二进制部分
            if str_buffer:
                str_list.append(str_buffer.decode('ascii'))
                str_buffer = b""
            bin_buffer += bytes([data[i]])
    if str_buffer:  # 将缓冲区中最后剩余的部分添加到各自的列表中
        str_list.append(str_buffer.decode('ascii'))
    if bin_buffer:
        bin_list.append(bin_buffer)
    if len(bin_list) == 0:
        bin_list.append(b'')
    if len(str_list) == 0:
        str_list.append('')
        
    return bin_list, str_list

def Split_text_binary(text):
    logger.debug("[Debug] Split_text_binary, text:%s", text)
    annotations = annotate_text_binary(text)
    bin_list, str_list = split_text_binary(text, annotations)
    return annotations, bin_list, str_list

def Restore_text_binary(bin_list, str_list, annotations):
    logger.debug("[Debug] Restore_text_binary, bin_list:%s, str_list:%s, annotations:%s", str(bin_list), str(str_list), str(annotations))
    # 创建两个迭代器，分别用于二进制数据和文本数据
    bin_iter = iter(bin_list)
    str_iter = iter(str_list)
    restored_data = bytearray()
    # 目前的文本值和二进制数据块
    current_str = next(str_iter, '')
    current_bin = next(bin_iter, b'')
    # 遍历annotations，决定接下来使用文本还是二进制数据
    for annotation in annotations:
        if annotation == 0:
            # 如果是文本，确保还有文本可取，然后取出一个字符
            if current_str:
                restored_data.extend(current_str[0].encode())
                current_str = current_str[1:]
            else:
                current_str = next(str_iter, '')
                restored_data.extend(current_str[0].encode())
                current_str = current_str[1:]
        else:
            # 如果是二进制，确保还有二进制数据可取，然后取出一个字节
            if current_bin:
                restored_data.append(current_bin[0])
                current_bin = current_bin[1:]
            else:
                current_bin = next(bin_iter, b'')
                restored_data.append(current_bin[0])
                current_bin = current_bin[1:]
    # 将bytearray转换成bytes类型
    return bytes(restored_data)


if __name__ == "__main__":
    # 测试
    data_test = b'This is text segemnt\x01\x02\x03\x04 And this is another one\x01\x02\x03\x04'
    annotations = annotate_text_binary(data_test)
    bin_list, str_list = split_text_binary(data_test, annotations)
    print('bin_list:', bin_list)
    print('str_list:', str_list)
    print(annotations)
    # 示例用法
    restored_data_test = Restore_text_binary(bin_list, str_list, annotations)
    print('Restored data:', restored_data_test)