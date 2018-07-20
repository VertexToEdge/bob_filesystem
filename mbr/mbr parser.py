import sys
import struct

def read_sector(fd, sector, count=1):
    fd.seek(sector*512)
    return fd.read(count*512)

#file_name = sys.argv[1]
file_name = "mbr_128.dd"

filesystem = open(file_name,"rb")

data = read_sector(filesystem,0)

if data[-2] != 0x55 and data[-1] != 0xAA:
    print("부트파티션이 아닙니다.")

partition_header = data[446:446+64]

tables = []
for i in range(4):
    tables.append(partition_header[i*16:(i+1)*16])

partition_list=[]
def dfs_partition(offset, tables):
    for i in tables:
        break_flag = True
        for c in i: #유효성검사
            if c!=0x00:
                break_flag = False
                break
        if(break_flag):
            return

        start_addr = struct.unpack_from("<I",i,8)[0]
        size =  struct.unpack_from("<I",i,12)[0]

        if i[4] == 0x07:
            partition_list.append(  [ "Partition", (start_addr+offset)*512 , size ]  )
        else:
            LBA = int(partition_list[-1][1] / 512) + partition_list[-1][2]

            local_data = read_sector(filesystem,LBA)
            local_partition_header = local_data[446:446+64]
            local_tables = []
            for k in range(4):
                local_tables.append( local_partition_header[k*16:(k+1)*16] )

            dfs_partition(LBA, local_tables)

dfs_partition(0, tables)

for i in range(len(partition_list)):
    print(str(partition_list[i][0])+str(i)+"  ",partition_list[i][1],"  ",partition_list[i][2])