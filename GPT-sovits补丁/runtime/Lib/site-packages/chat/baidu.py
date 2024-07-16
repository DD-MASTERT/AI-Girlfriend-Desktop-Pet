# -*- coding: utf-8 -*-

import requests
import json


def translate_ja_to_zh(text, BDaccess_token, BDS, BDT):
    # 您的access_token，需要替换为有效的值
    access_token = BDaccess_token
    
    # 翻译的URL
    url = f'https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token={access_token}'
    
    # 请求的Header
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 请求的Body
    payload = {
        'q': text,
        'from': BDS,  # 源语言为日语
        'to': BDT    # 目标语言为中文
    }
    
    # 发送POST请求
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    
    # 检查是否翻译成功，并返回翻译结果
    if 'trans_result' in response.get('result', {}):
        # 将翻译结果合并为一个字符串并返回
        return ' '.join([item['dst'] for item in response['result']['trans_result']])
    else:
        # 如果翻译失败，返回错误信息
        return f'翻译失败: {response.get("error_msg", "")}'

# 使用示例
#translated_text = translate_ja_to_zh("私はロボットで、夏生さんが海から引き上げてくれたの。主人の残した命令を果たすために、失った記憶を探しています。")
#print(translated_text)