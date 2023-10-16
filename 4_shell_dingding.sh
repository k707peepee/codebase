#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
export PATH

#=================================================
#       System Required: Ubuntu 20.04+
#       Description: EPiK
#       Author: LiangPing
#       BeginDate: 2023-10-10
#       Company: 中康尚德健康管理(北京)有限公司
#       Version: v1.0  钉钉发送脚本模块
#=================================================

#钉钉播报变量
Subject=''
Body=''
URL=''
now_date=`date '+%F'`
now_time=`date '+%T'`
NowDate=`date "+<%Y-%m-%d>%H:%M:%S" `


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

