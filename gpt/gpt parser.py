import sys
import struct

def read_sector(fd, sector, count=1):
    fd.seek(sector*512)
    return fd.read(count*512)

#file_name = sys.argv[1]
file_name = "gpt_128.dd"

filesystem = open(file_name,"rb")

data = read_sector(filesystem,0)

if data[-2] != 0x55 and data[-1] != 0xAA:
    print("부트파티션이 아닙니다.")

partition_header = data[446:446+64]

gpt_start = struct.unpack_from("<I",partition_header,8)[0]

gpt_header = read_sector(filesystem,gpt_start)

if struct.unpack_from("<8s",gpt_header,0)[0]!= b'EFI PART' :
    print("GPT가 아닙니다.")

PartEntry_start = struct.unpack_from("<Q",gpt_header,72)[0]
PartEntry_count = struct.unpack_from("<I",gpt_header,80)[0]

Partition_list = []
for idx in range(PartEntry_count):
    PartEntry = read_sector(filesystem, PartEntry_start+idx)
    for Entry_idx in range(4):
        Entry = PartEntry[Entry_idx*128:(Entry_idx+1)*128]
        EntryStart = struct.unpack_from("<Q", Entry, 32)[0]
        EntryLast = struct.unpack_from("<Q", Entry, 40)[0]

        flag = False
        if EntryStart == 0:
            flag =True
            break
        Partition_list.append([EntryStart,EntryLast-EntryStart+1])
        Partition_list[-1] = [i*512 for i in Partition_list[-1]]
    if flag:
        break
for i in range(len(Partition_list)):
    print("Partition" + str(i+1) + "    StartAt:" + str(Partition_list[i][0]) + "      Size:" + str(Partition_list[i][1]))