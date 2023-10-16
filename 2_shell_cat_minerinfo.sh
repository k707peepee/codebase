#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
export PATH

#=================================================
#       System Required: Ubuntu 
#       Description: Filecoin
#       Author: LiangPing
#       BeginDate: 2023-10-9
#       Company: 中康尚德健康管理(北京)有限公司
#       Version: v1.0  协助数据库截取当前miner机的信息
#=================================================

# miner机的ID号
minerID='f02146033'

# 循环时间（秒），24小时循环是 86400
Time=60

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


# 循环程序
while true
do
    # 生成临时文件名
    temp_file="/tmp/${minerID}_miner_info.tmp"

    rm -rf "$temp_file"
    `echo lotus-miner info` > "$temp_file"

    # 进行判断，发送钉钉报告
    miner_info_ok=`ls /tmp | grep ${minerID} | wc -l`
    if [ "$miner_info_ok" -eq "1" ]
    then
        echo -e "`date '+%F %T'` ${Info} 【$minerID】的今日PG基础数据已生成！"
        # 调用钉钉脚本模块
        # source dingding.sh
        Subject1='数据库-miner数据生成'
        Body1="####\t【$minerID】\n####\t的今日PG基础数据已生成！\n"
        SendMessageToDingding $Subject1 $Body1

    else
        echo -e "`date '+%F %T'` ${Error} 【$minerID】的今日PG基础数据未能生成！"
        # 调用钉钉脚本模块
        # source dingding.sh
        Subject2='数据库-miner数据生成'
        Body2="####\t【$minerID】\n####\t今日PG基础数据未能生成！\n####\t请管理员及时查看原因！\n"
        SendMessageToDingding $Subject2 $Body2

    fi

    #设置休眠时间
	sleep $Time

done
