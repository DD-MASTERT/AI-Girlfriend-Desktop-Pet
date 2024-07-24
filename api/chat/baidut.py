import hashlib
import requests
import random

def translate_text(query, appid, secret, from_lang, to_lang):
    # 随机生成一个salt值
    salt = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    # 按照文档要求生成签名
    sign_str = f'{appid}{query}{salt}{secret}'
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    # 构建请求参数
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    
    # 发送请求并获取结果
    response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=params)
    result = response.json()
    
    # 检查是否有错误
    if 'error_code' in result:
        return f"Error: {result['error_msg']}"
    
    # 返回翻译结果
    return result['trans_result'][0]['dst']

# 使用示例
#appid = '你的appid'
#secret = '你的密钥'
#query = 'apple'
#from_lang = 'en'
#to_lang = 'zh'

#translated_text = translate_text(query, appid, secret, from_lang, to_lang)
#print(f"The translation of '{query}' is '{translated_text}'")