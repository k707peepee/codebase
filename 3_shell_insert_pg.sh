#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
export PATH

#=================================================
#       System Required: Ubuntu 
#       Description: Filecoin
#       Author: LiangPing
#       BeginDate: 2023-10-9
#       Company: 中康尚德健康管理(北京)有限公司
#       Version: v1.0  将miner每日信息存入pg数据库
#=================================================  

#钉钉播报变量
Subject=''
Body=''
URL=''
now_date=`date '+%F'`
now_time=`date '+%T'`
NowDate=`date "+<%Y-%m-%d>%H:%M:%S" `

# 发送钉钉函数
function SendMessageToDingding(){
  Dingding_Url="https://oapi.dingtalk.com/robot/send?access_token=d3c1a76b849582a4cd98336a165c2e26e4a4ef219ec62eda15662b4df5104038"
        curl -s "${Dingding_Url}" -H 'Content-Type: application/json' -d "
        {
                \"actionCard\": {
                \"title\": \"$1\",
                \"text\": \"$2\",
                \"hideAvatar\": \"0\",
                \"btnOrientation\": \"0\",
                \"btns\": [
                        {
                                \"title\": \"$1\",
                                \"actionURL\": \"$3\"
                        }
                        ]
                },
                \"msgtype\": \"actionCard\"  
        }"
}

# 生成日期变量
date_file=`date "+%Y%m%d" `

echo -e "`date '+%F %T'` ${Info} 每日数据存入数据库脚本开始执行！"

# 获取miner机的每日信息
echo -e "`date '+%F %T'` ${Info} 开始获取各miner机数据！"
echo -e "`date '+%F %T'` ${Info} 开始获取f01180639数据！"
sshpass -p 019806 ssh -o StrictHostKeyChecking=no psdz@192.168.0.12 'cat /tmp/f01180639_miner_info.tmp' > /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp
echo -e "`date '+%F %T'` ${Info} 开始获取f019806数据！"
sshpass -p 019806 ssh -o StrictHostKeyChecking=no txys@192.168.0.72 'cat /tmp/f019806_miner_info.tmp' > /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp
echo -e "`date '+%F %T'` ${Info} 开始获取f01769576数据！"
sshpass -p 019806 ssh -o StrictHostKeyChecking=no psdz@192.168.0.110 'cat /tmp/f01769576_miner_info.tmp' > /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp
echo -e "`date '+%F %T'` ${Info} 开始获取f02146033数据！"
sshpass -p admin@123 ssh -o StrictHostKeyChecking=no psdz@192.168.0.78 'cat /tmp/f02146033_miner_info.tmp' > /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp
echo -e "`date '+%F %T'` ${Info} 获取各miner机数据结束！"

# Docker 容器名称或 ID，用于连接到正确的容器
CONTAINER_NAME="filecoin-pg"

# PostgreSQL 连接信息
# 数据库主机地址
DB_HOST="localhost"
# 数据库端口
DB_PORT="5432"
# 数据库名称
DB_NAME="filecoindata"
# 数据库用户名
DB_USER="txys"
# 数据库密码
DB_PASS="txys2023"

# 表单相关信息
# 表单名称
DB_TABLE="base_statistics"

echo -e "`date '+%F %T'` ${Info} 开始对获取数据进行整理！"
echo -e "`date '+%F %T'` ${Info} 整理理论幸运值数据！"
# 表单字段：
# 超参数：官网幸运值
# 这部分无法从服务器端获取，需要从网页端获取数据进行计算
# 每隔一段时间这个参数都需要调整
filecoin_luck=6.5
luck=$filecoin_luck

echo -e "`date '+%F %T'` ${Info} 整理节点号数据！"
# 节点号，文本类型
node_id1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Miner:" | awk '{print $2}'`
node_id2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Miner:" | awk '{print $2}'`
node_id3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Miner:" | awk '{print $2}'`
node_id4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Miner:" | awk '{print $2}'`

echo -e "`date '+%F %T'` ${Info} 整理算力数据！"
# 当前算力，精确数字类型
power1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Raw:" | awk '{print $2}'`
power2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Raw:" | awk '{print $2}'`
power3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Raw:" | awk '{print $2}'`
power4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Raw:" | awk '{print $2}'`

echo -e "`date '+%F %T'` ${Info} 整理总余额数据！"
# 总余额，精确数字类型
total_balance1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Miner Balance:" | awk '{print $3}'`
total_balance2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Miner Balance:" | awk '{print $3}'`
total_balance3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Miner Balance:" | awk '{print $3}'`
total_balance4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Miner Balance:" | awk '{print $3}'`

echo -e "`date '+%F %T'` ${Info} 整理质押余额数据！"
# 质押余额，精确数字类型
ini_pledge1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Pledge:" | awk '{print $2}'`
ini_pledge2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Pledge:" | awk '{print $2}'`
ini_pledge3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Pledge:" | awk '{print $2}'`
ini_pledge4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Pledge:" | awk '{print $2}'`

echo -e "`date '+%F %T'` ${Info} 整理锁仓余额数据！"
# 锁仓余额，精确数字类型
lock_balance1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Vesting:" | awk '{print $2}'`
lock_balance2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Vesting:" | awk '{print $2}'`
lock_balance3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Vesting:" | awk '{print $2}'`
lock_balance4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Vesting:" | awk '{print $2}'`

echo -e "`date '+%F %T'` ${Info} 整理可用余额数据！"
# 可用余额，精确数字类型
ava_balance1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Available:" | head -n 1 | awk '{print $2}'`
ava_balance2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Available:" | head -n 1 | awk '{print $2}'`
ava_balance3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Available:" | head -n 1 | awk '{print $2}'`
ava_balance4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Available:" | head -n 1 | awk '{print $2}'`

echo -e "`date '+%F %T'` ${Info} 整理owner余额数据！"
# owner余额，精确数字类型
owner_balance1=`cat /space/filecoin_pg_data/data/${date_file}_f01180639_miner_info.tmp | grep "Worker Balance:" | awk '{print $3}'`
owner_balance2=`cat /space/filecoin_pg_data/data/${date_file}_f019806_miner_info.tmp | grep "Worker Balance:" | awk '{print $3}'`
owner_balance3=`cat /space/filecoin_pg_data/data/${date_file}_f01769576_miner_info.tmp | grep "Worker Balance:" | awk '{print $3}'`
owner_balance4=`cat /space/filecoin_pg_data/data/${date_file}_f02146033_miner_info.tmp | grep "Worker Balance:" | awk '{print $3}'`

echo -e "`date '+%F %T'` ${Info} 获取日期数据！"
# 获取数据的时间，日期和时间类型
time=`$(date +%Y-%m-%d)`

echo -e "`date '+%F %T'` ${Info} 数据整理结束！"
echo -e "`date '+%F %T'` ${Info} 开始将数据存入数据库"

# 获取数据插入语句
INSERT_SQL="INSERT INTO $DB_TABLE (time, node_id, total_balance, ava_balance, ini_pledge, lock_balance, owner_balance, power, luck) VALUES"

# 数据行，每一行的格式
DATA_ROWS=(
  "('$time', '$node_id1', '$total_balance1', '$ava_balance1', '$ini_pledge1', '$lock_balance1', '$owner_balance1', '$power1', '$luck')",
  "('$time', '$node_id2', '$total_balance2', '$ava_balance2', '$ini_pledge2', '$lock_balance2', '$owner_balance2', '$power2', '$luck')",
  "('$time', '$node_id3', '$total_balance3', '$ava_balance3', '$ini_pledge3', '$lock_balance3', '$owner_balance3', '$power3', '$luck')",
  "('$time', '$node_id4', '$total_balance4', '$ava_balance4', '$ini_pledge4', '$lock_balance4', '$owner_balance4', '$power4', '$luck')"
)

# 构建完整的插入语句
INSERT_STATEMENT="$INSERT_SQL ${DATA_ROWS[@]}"

# 使用 psql 命令执行插入语句，通过 Docker 容器连接
docker exec filecoin-pg psql "dbname=$DB_NAME host=$DB_HOST port=$DB_PORT user=$DB_USER password=$DB_PASS" -c "$INSERT_STATEMENT"

# 钉钉发送文档整理
Subject1='数据库-pg数据存入'
time_task="####\t【存入时间】：\t$NowDate\n"
Task1="---\n####\t【$node_id1】今日数据\n"
detail="#####\t当前算力：$power1\n#####\t节点总额：$total_balance1\n#####\t质押余额：$ini_pledge1\n#####\t锁仓余额：$lock_balance1\n#####\t可用余额：$ava_balance1\n#####\t钱包余额：$owner_balance1\n"
Task2="---\n####\t【$node_id2】今日数据\n"
detai2="#####\t当前算力：$power2\n#####\t节点总额：$total_balance2\n#####\t质押余额：$ini_pledge2\n#####\t锁仓余额：$lock_balance2\n#####\t可用余额：$ava_balance2\n#####\t钱包余额：$owner_balance2\n"
Task3="---\n####\t【$node_id3】今日数据\n"
detai3="#####\t当前算力：$power3\n#####\t节点总额：$total_balance3\n#####\t质押余额：$ini_pledge3\n#####\t锁仓余额：$lock_balance3\n#####\t可用余额：$ava_balance3\n#####\t钱包余额：$owner_balance3\n"
Task4="---\n####\t【$node_id4】今日数据\n"
detai4="#####\t当前算力：$power4\n#####\t节点总额：$total_balance4\n#####\t质押余额：$ini_pledge4\n#####\t锁仓余额：$lock_balance4\n#####\t可用余额：$ava_balance4\n#####\t钱包余额：$owner_balance4\n"
luck_task="---\n####\t【理论幸运值】：\t$luck\n"
Body1=${time_task}${Task1}${detail}${Task2}${detai2}${Task3}${detai3}${Task4}${detai4}${luck_task}

Subject2='数据库-出现故障'
Body2="####\t数据插入失败\n####\t请管理员及时查看情况"

# 检查插入是否成功
if [ $? -eq 0 ]; then
  echo "数据插入时间：$time "
  echo "数据插入成功"
  SendMessageToDingding $Subject1 $Body1

else
  echo "数据插入失败"
  SendMessageToDingding $Subject2 $Body2

fi

echo -e "`date '+%F %T'` ${Info} 数据存入数据库结束！"
echo -e "`date '+%F %T'` ${Info} 本次数据库脚本结束！"
