

# pcap文件目录路径
pcap_dir = '/Users/xf/实验改进/mutators/SplitBinText/pcap'
import pyshark
import os
from split import Split_text_binary, Restore_text_binary

s = set()
succ = {}
fail = {}
# Traverse all .pcap files in the directory
for filename in os.listdir(pcap_dir):
    if filename.endswith('.pcap') or filename.endswith(".pcapng"):  # Check for .pcap files
    # if "mqtt3.pcap" in filename:
        filepath = os.path.join(pcap_dir, filename)  # Full path for the file
        cap = pyshark.FileCapture(filepath, include_raw=True, use_json=True)

        # Read each packet in the file
        for packet in cap:
            protocol = packet.highest_layer  # Get the highest layer protocol
            s.add(protocol)
            # print(f"Protocol: {protocol}")

            # Attempt to print the packet bytes by accessing the raw layer.
            try:
                raw_data = packet.get_raw_packet()
                if raw_data:
                    packet_bytes = raw_data
                    a,b,c = Split_text_binary(raw_data)
                    if len(b[0]) > 0 and len(c[0]) >0:
                        if protocol not in succ:
                            succ[protocol] = 1
                        else:
                            succ[protocol] += 1
                    else:
                        if protocol not in fail:
                            fail[protocol] = 1
                        else:
                            fail[protocol] += 1
            except AttributeError as e:
                pass
        cap.close()
print(len(s))
for i in succ.keys():
    if i not in fail:
        fail[i] = 0
    print(i, succ[i]/(succ[i]+fail[i])*100, succ[i]+fail[i])