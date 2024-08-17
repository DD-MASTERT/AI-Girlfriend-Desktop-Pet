import os
import re
# import pygame
import threading
import json
from pydub import AudioSegment
import uvicorn
from fastapi import FastAPI, Request
from uvicorn import Server, Config
import signal
from typing import Optional
import time
import requests
from gradio_client import Client, handle_file
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from fastapi.middleware.cors import CORSMiddleware
# from chat.utils import talk, click_create_text_element, send_and_update,closedriver
# from chat.kimi import kimitalk, kimiclick_create_text_element, kimisend_and_update
from chat.baidu import translate_ja_to_zh
from chat.tenxun import txtra
from chat.baidut import translate_text
import edge_tts
import asyncio
import azure.cognitiveservices.speech as speechsdk
from kimi import kimiapi
from glm4 import glm4api
from deepseek2 import deepseekv2
from ollama import ollama
from openapikey import openaiapi



LLM = "glm" # 或者 "glm"

OPTIONS = True  # 或者 False，根据需要设置

TOKEN = ''

TXSecretId = ''
TXSecretKey = ''
TXS = "ja"
TXT = "zh"

BDaccess_token = ''
BDS = "jp"
BDT = "zh"


APPID = 123
SECRET = ''
BDTS = "jp"
BDTT = "zh"


TTS = '纳西妲'

MB = '雷姆'

Text_language = "中文"

How_to_cut = "按。.！!?？切"

Interval = 0.5

R = "不翻译"  # 或 "腾讯" 或 “百度”或"不翻译"或"括号翻译"

T = "原文"   # 或 "翻译" 或 "原文"

GSV = True

Edgevoive = 'zh-CN-XiaoxiaoNeural'

Vosyspeaker = '中文女'

speech_key = None

service_region =None

isorder = None
def guolvorder(input_string):
        if isorder:
            pattern0 = re.compile(r'\*\*\{(.*?)\}\*\*')
            # 存储匹配到的 **{...}** 内容和它们的位置
            contents = []
            # 存储替换后的特殊标记
            placeholders = []
            # 替换 **{...}** 为特殊标记，并存储内容
            def replace_with_placeholder(match):
                content = match.group(1)  # 获取匹配到的括号内的内容
                placeholder = f"__{len(contents)}__"  # 创建一个特殊的标记
                contents.append(content)  # 存储内容
                placeholders.append(placeholder)  # 存储特殊标记
                return placeholder
            # 使用正则表达式替换函数
            name_with_placeholders = pattern0.sub(replace_with_placeholder, input_string)          
            # 定义正则表达式模式，匹配 [-需要提取的内容-] 格式
            pattern = r'\[-[^]]*?-\]'              
            # 使用 re.sub 删除所有匹配的项
            modified_string = re.sub(pattern, '', name_with_placeholders, re.DOTALL)               
            # 将删除后的内容赋值给一个新的变量
            return modified_string
        else:
            return input_string
# 读取JSON文件并赋值给全局变量的函数
def load_json_config(filename):
    global LLM, OPTIONS, TOKEN, TXSecretId, TXSecretKey, TXS, TXT, BDaccess_token, BDS, BDT, APPID, SECRET, BDTS, BDTT, TTS, MB, Text_language, How_to_cut, Interval, R, T, GSV, Edgevoive,Vosyspeaker,speech_key,service_region
   
    with open(filename, 'r', encoding='utf-8') as file:
        config_data = json.load(file)  # 加载JSON数据
        
    # 将JSON数据中的值赋给全局变量
    LLM = config_data.get('LLM')
    OPTIONS = config_data.get('OPTIONS')
    TOKEN = config_data.get('TOKEN')
    TXSecretId = config_data.get('TXSecretId')
    TXSecretKey = config_data.get('TXSecretKey')
    TXS = config_data.get('TXS')
    TXT = config_data.get('TXT')
    BDaccess_token = config_data.get('BDaccess_token')
    BDS = config_data.get('BDS')
    BDT = config_data.get('BDT')
    APPID = config_data.get('APPID')
    SECRET = config_data.get('SECRET')
    BDTS = config_data.get('BDTS')
    BDTT = config_data.get('BDTT')
    TTS = config_data.get('TTS')
    MB = config_data.get('MB')
    Text_language = config_data.get('Text_language')
    How_to_cut = config_data.get('How_to_cut')
    Interval = config_data.get('Interval')
    R = config_data.get('R')
    T = config_data.get('T')
    GSV = config_data.get('GSV')
    Edgevoive = config_data.get('Edgevoive')
    Vosyspeaker = config_data.get('Vosyspeaker')
    speech_key = config_data.get('speech_key')    
    service_region = config_data.get('service_region')
# 调用函数并传入JSON文件路径
load_json_config('api/api.json')

def save_globals_to_json(filename):
    # 创建一个包含所有全局变量名的列表
    global_vars = [
        'LLM', 'OPTIONS', 'TOKEN', 'TXSecretId', 'TXSecretKey', 'TXS', 'TXT',
        'BDaccess_token', 'BDS', 'BDT', 'APPID', 'SECRET', 'BDTS', 'BDTT',
        'TTS', 'MB', 'Text_language', 'How_to_cut', 'Interval', 'R', 'T', 'GSV', 'Edgevoive',
        'Vosyspeaker','speech_key','service_region'
    ]
    
    # 创建一个字典，用于存储全局变量的名称和值
    config_data = {var: globals()[var] for var in global_vars}
    
    # 将字典写入JSON文件
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(config_data, file, ensure_ascii=False, indent=4)
def ollamamodel():
    global apiollama
    config_file = 'api/ollama.json'
    with open(config_file, 'r', encoding='utf-8') as json_file:
        config = json.load(json_file) 
    apiollama.model = config['model']          
apiglm4 = glm4api()
apikimi = kimiapi()
apideepseek = deepseekv2()
apiollama = ollama()
apikey = openaiapi()
def retoken():
    global apiglm4,apikimi,apideepseek,apiollama,apikey
    with open('api/gsv.json', 'r', encoding='utf-8') as file:
        gsvconfig = json.load(file)  # 加载JSON数据
    apiglm4.chatglm_refresh_token = gsvconfig['chatglm_refresh_token']
    apiglm4.assistant_id = gsvconfig['assistant_id']
    apikimi.refresh_token = gsvconfig['refresh_token']
    apideepseek.usertoken = gsvconfig['usertoken'] 
    ollamamodel()
    apikey.loadmodel()
def newtalk():
    global LLM,apiglm4,apikimi,apideepseek,apiollama,apikey
    if LLM == "glm": 
        apiglm4.talknew()
    elif LLM == "kimi":
        apikimi.getnewtalk()
    elif LLM == "deepseek":  
        apideepseek.newtalk()
    elif LLM == "ollama":
        apiollama.newtalk()
    elif LLM == "APIkey":
        apikey.newtalk()
    else:
        print("错误")    
def uptoken():
    interval=600
    global apiglm4,apikimi,LLM ,apideepseek,apikey   
    with open('api/gsv.json', 'r', encoding='utf-8') as file:
        gsvconfig = json.load(file)  # 加载JSON数据   
    if LLM == "glm":
        interval=1800
        chatglm_refresh_token, token = apiglm4.gettoken()
        gsvconfig['chatglm_refresh_token'] = chatglm_refresh_token
        apiglm4.chatglm_refresh_token = chatglm_refresh_token
        apiglm4.token = token
        with open('api/gsv.json', 'w', encoding='utf-8') as file:
            json.dump(gsvconfig, file, ensure_ascii=False, indent=4)
    elif LLM == "kimi":
        refresh_token, token = apikimi.gettoken()
        gsvconfig['refresh_token'] = refresh_token
        apikimi.refresh_token = refresh_token
        apikimi.token = token
        with open('api/gsv.json', 'w', encoding='utf-8') as file:
            json.dump(gsvconfig, file, ensure_ascii=False, indent=4)  
    else:
        print("deepseek2模型or其他不需要刷新token的模型")
    return interval           
def looptime():
    i = 1
    while True:
        interval = uptoken() 
        if i == 1:
            newtalk()                          
        time.sleep(interval)
        i+=1    # 等待20分钟
retoken()       
thread = threading.Thread(target=looptime)
thread.daemon = True  # 设置为守护线程，这样当主程序退出时，线程也会退出
thread.start()            


# 读取并解析文本文件中的参数
def read_params(file_path):
    params = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value.strip()
    return params


client = None
sovits_path = None
gpt_path = None
ref_audio_path = None
ref_text = None
ref_audio_language = None
wai = None
nei = None

def clientdata(client):
    global sovits_path, gpt_path, ref_audio_path, ref_text, ref_audio_language, config_file_path  # 声明这些变量是全局的
    # 读取参数
    params = read_params(config_file_path)
    # 使用读取的参数值
    sovits_path = params.get('SoVITS_model_path')
    gpt_path = params.get('GPT_model_path')
    ref_audio_path = params.get('ref_audio_path')
    # ref_audio_path = '..\\' + ref_audio_path
    ref_text = params.get('ref_text')
    ref_audio_language = params.get('ref_audio_language')

    # 调用API更改 SoVITS 权重
    client.predict(
        sovits_path=sovits_path,
        api_name="/change_sovits_weights"
    )

    # 调用API更改 GPT 权重
    client.predict(
        gpt_path=gpt_path,
        api_name="/change_gpt_weights"
    )




# 动态生成文件路径
base_path = 'moys'
file_name = os.path.join('.', f'{TTS}.txt')
config_file_path = os.path.join(base_path, file_name)

# 检查文件路径是否存在
if not os.path.exists(config_file_path):
    print(f"Path does not exist: {config_file_path}")
else:
    if GSV:
        # 使用读取的参数初始化 Gradio 客户端
        client = Client("http://localhost:9872/")
        clientdata(client)
    else:
        pass    





def read_initial_user_input(file_path):
    """从文件中读取初始用户输入内容。"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()
    

def separate_brackets(text):
    # 找到所有括号内的内容
    inner_contents = re.findall(r'（(.*?)）', text)
    # 清理括号中的内容并用“。”连接
    nei = '。'.join(inner_contents)
    
    # 找到所有不在括号内的内容
    outer_contents = re.split(r'（.*?）', text)
    # 清理外部内容并用“。”连接
    wai = '。'.join(outer_contents).replace('。。', '。')

    return wai, nei

edge = False
async def edgetts(text: str, output: str = 'api/edge/audio.mp3', voice: str = Edgevoive):
    global Edgevoive
    voice = Edgevoive
    text = guolvorder(text)    
    if voice == 'zh-CN-XiaoxiaoMultilingualNeural': 
        await synthesize_text_to_speech(text,voice)   
    elif voice == 'zh-CN-XiaochenMultilingualNeural':
        await synthesize_text_to_speech(text,voice)  
    elif voice == 'zh-CN-XiaoyuMultilingualNeural':
        await synthesize_text_to_speech(text,voice)  
    elif voice == 'zh-CN-YunyiMultilingualNeural':                                          
        await synthesize_text_to_speech(text,voice)  
    else:         
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output)
async def synthesize_text_to_speech(text: str, voice: str = '',output: str = 'api/edge/audio.wav'):

    global speech_key,service_region


    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voice
    # text = "你好，这是晓晓 多语言。"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output)
    # 创建语音合成器实例
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config,audio_config=audio_config)

    # 创建一个音频数据流对象
    # 使用 speak_text_async 方法并指定音频数据流
    result = speech_synthesizer.speak_text_async(text).get()

    # 检查结果
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print('完成')
        convert_wav_to_mp3()
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("语音合成已取消: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("错误详情: {}".format(cancellation_details.error_details))
            
def convert_wav_to_mp3(wav_file_path ='api/edge/audio.wav'):
    # 确保传入的是一个wav文件
    if not wav_file_path.lower().endswith('.wav'):
        print("The file is not a WAV file.")
        return

    # 加载WAV文件
    audio = AudioSegment.from_wav(wav_file_path)

    # 构建输出文件的路径（替换原始文件扩展名为mp3）
    mp3_file_path = wav_file_path[:-4] + '.mp3'

    # 导出为MP3格式
    audio.export(mp3_file_path, format="mp3")

    # 删除原始WAV文件
    # os.remove(wav_file_path)
    print(f"Converted {wav_file_path} to {mp3_file_path}")

cosy = False
async def cosytts(text):
    text = guolvorder(text)
    global Vosyspeaker
    vosyspeaker = Vosyspeaker
    # 获取当前工作目录
    current_directory = os.getcwd()

    # 定义子目录和文件名
    sub_directory = "api/cosy"
    file_name = "audio.wav"

    # 使用os.path.join组合路径
    path = os.path.join(current_directory, sub_directory, file_name)
    print(path)    
    headers = {'Content-Type': 'application/json'}

    gpt = {"text":text,"speaker":vosyspeaker,"new":0,"path":path}

    response = requests.post("http://localhost:9880/noaudio/",data=json.dumps(gpt),headers=headers)




def glm4(preset_dialogue_file_path, user_input):
    global wai, nei
    # 检查 user_input 是否以 "发送预设，" 开头
    if user_input.startswith("发送预设，"):
        # 从文件中读取初始用户输入
        initial_user_input = read_initial_user_input(preset_dialogue_file_path)
        if initial_user_input is None:
            return {"error": "Initial user input not found."}
        
        # 使用 initial_user_input 构造消息
        mes = f"设定信息：{initial_user_input}\n(那么开始)：{user_input[len('发送预设，'):]}"
    else:
        # 使用原始 user_input 构造消息
        mes = f"{user_input}"

    # 以下是函数的其他部分，例如发送消息和获取反馈

    dashscope_feedback = ''
    if LLM == "kimi":
        for r in apikimi.talknext(mes):
            dashscope_feedback += r
    elif LLM == "glm":
        for q in apiglm4.talknext(mes):
            dashscope_feedback = q
    elif LLM == "ollama":
        dashscope_feedback = apiollama.chat_with_model(mes)
    elif LLM == "APIkey":
        dashscope_feedback = apikey.talk(mes)                
    else: 
        for d in apideepseek.talknext(mes): 
         dashscope_feedback += d 

    if R == "括号翻译":
        wai, nei = separate_brackets(dashscope_feedback)    
        dashscope_feedback = wai
        # out = play_tts_audio(wai)
        out = asyncio.run(play_tts_audio(wai))
    else:
        out = asyncio.run(play_tts_audio(dashscope_feedback))

    return {"out": out}


def onlyglm4(preset_dialogue_file_path, user_input):
    global wai, nei
    # 检查 user_input 是否以 "发送预设，" 开头
    if user_input.startswith("发送预设，"):
        # 从文件中读取初始用户输入
        initial_user_input = read_initial_user_input(preset_dialogue_file_path)
        if initial_user_input is None:
            return {"error": "Initial user input not found."}
        
        # 使用 initial_user_input 构造消息
        mes = f"设定信息：{initial_user_input}\n(那么开始)：{user_input[len('发送预设，'):]}"
    else:
        # 使用原始 user_input 构造消息
        mes = f"{user_input}"

    dashscope_feedback = ''
    if LLM == "kimi":
        for r in apikimi.talknext(mes):
            dashscope_feedback += r
    elif LLM == "glm":
        for q in apiglm4.talknext(mes):
            dashscope_feedback = q
    elif LLM == "ollama":
        dashscope_feedback = apiollama.chat_with_model(mes)
    elif LLM == "APIkey":
        dashscope_feedback = apikey.talk(mes)                     
    else: 
        for d in apideepseek.talknext(mes): 
         dashscope_feedback += d 
         
    if R == "括号翻译":
        wai, nei = separate_brackets(dashscope_feedback)    
        dashscope_feedback = wai
        out = play(wai)
        if edge:
            asyncio.run(edgetts(wai))
        if cosy:
            asyncio.run(cosytts(wai))            
    else:
        out = play(dashscope_feedback)
        if edge:
            asyncio.run(edgetts(dashscope_feedback))
        if cosy:
            asyncio.run(cosytts(dashscope_feedback))       
    return {"out": out}

def play(dashscope_feedback):
 
    # 初始化翻译结果变量
    translated_text = None

    # 根据 R 的值决定是否调用翻译函数
    if R == "百度ai":
        translated_text = translate_ja_to_zh(dashscope_feedback, BDaccess_token, BDS, BDT)
    elif R == "腾讯":
        translated_text = txtra(dashscope_feedback, TXSecretId, TXSecretKey, TXS, TXT)
    elif R == "百度":
        translated_text = translate_text(dashscope_feedback, APPID, SECRET, BDTS, BDTT)
    elif R == "括号翻译":
        translated_text = nei
    # 如果 R 是 "不翻译"和其他，则不调用翻译函数

    # 根据 T 的值决定最终输出
    if T == "翻译":
        final_output = translated_text if translated_text else dashscope_feedback
    elif T == "原文加翻译":
        final_output = f"{translated_text}\n原文：{dashscope_feedback}" if translated_text else dashscope_feedback
    elif T == "原文":
        final_output = dashscope_feedback
    else:
        final_output = "输出选项无效。"

 
    return final_output



async def play_tts_audio(dashscope_feedback):
    global ref_audio_path, ref_text, ref_audio_language
    tuili = guolvorder(dashscope_feedback)
    # 调用API获取 TTS 音频
    ref_audio_handled = handle_file(ref_audio_path)
    result = client.predict(
        ref_wav_path=ref_audio_handled,
        prompt_text=ref_text,
        prompt_language=ref_audio_language,
        text=tuili,  # 使用Dashscope反馈结果
        text_language=Text_language,
        how_to_cut=How_to_cut,
        top_k=5,
        top_p=1,
        temperature=1,
        interval=Interval,
        ref_free=False,
        api_name="/get_tts_wav"
    )

    # # result 是从 Gradio 客户端接收的本地文件路径
    # local_normalized = os.path.normpath(result)

    # # 读取音频文件内容
    # try:
    #     with open(local_normalized, 'rb') as audio_file:
    #         audio_data = audio_file.read()
    # except IOError as e:
    #     print(f"An error occurred while reading the audio file: {e}")
    #     return None, None
    
    # 初始化翻译结果变量
    translated_text = None

    # 根据 R 的值决定是否调用翻译函数
    if R == "百度ai":
        translated_text = translate_ja_to_zh(dashscope_feedback, BDaccess_token, BDS, BDT)
    elif R == "腾讯":
        translated_text = txtra(dashscope_feedback, TXSecretId, TXSecretKey, TXS, TXT)
    elif R == "百度":
        translated_text = translate_text(dashscope_feedback, APPID, SECRET, BDTS, BDTT)
    elif R == "括号翻译":
        translated_text = nei
    # 如果 R 是 "不翻译"和其他，则不调用翻译函数

    # 根据 T 的值决定最终输出
    if T == "翻译":
        final_output = translated_text if translated_text else dashscope_feedback
    elif T == "原文加翻译":
        final_output = f"{translated_text}\n原文：{dashscope_feedback}" if translated_text else dashscope_feedback
    elif T == "原文":
        final_output = dashscope_feedback
    else:
        final_output = "输出选项无效。"

 
    return final_output

# def calculate_interval(local_normalized, f):
#     # 初始化pygame mixer
#     pygame.mixer.init()

#     # 使用pygame加载音频文件，获取时长
#     sound = pygame.mixer.Sound(local_normalized)
#     audio_duration = sound.get_length()

#     # 确保f是一个字符串
#     if not isinstance(f, str):
#         raise ValueError("Expected f to be a string, but got: {}".format(f))

#     # 计算字符串长度
#     f_length = len(f)

#     # 计算播放一次音频所需的间隔时间（秒）
#     interval = audio_duration / f_length

#     return interval

# FastAPI部分
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str
    order: bool


# 假设你的音频文件存储在
AUDIO_FILES_DIRECTORY = r'api/audio'

@app.post("/multi_round_conversation/")
def api_multi_round_conversation(input: TextInput):
    global isorder
    isorder = input.order
       

    # 这里是人物模版文件路径
    preset_dialogue_file_path = os.path.join('moban', f'{MB}.txt')

    
    result = None  # 初始化result变量
    audio_data = None  # 初始化audio_data变量
    temp_audio_path = None  # 初始化临时文件路径变量

    # 判断输入文本是否为“新建对话”
    if input.text == "新建对话":
        # 执行新建对话的逻辑

        newtalk()
        # # 读取音频文件
        # with open("audio.wav", "rb") as audio_file:
        #     audio_data = audio_file.read()
        # # 创建一个临时文件来存储音频数据，并指定文件存放的目录
        # with NamedTemporaryFile(dir=AUDIO_FILES_DIRECTORY, delete=False, suffix='.wav') as temp_audio_file:
        #     temp_audio_file.write(audio_data)
        #     temp_audio_path = temp_audio_file.name
    else:
        # 执行原始逻辑
        result = glm4(preset_dialogue_file_path, input.text)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # # 假设 result['audio'] 是音频数据
        # audio_data = result['audio']
        
        # # 创建一个临时文件来存储音频数据，并指定文件存放的目录
        # with NamedTemporaryFile(dir=AUDIO_FILES_DIRECTORY, delete=False, suffix='.wav') as temp_audio_file:
        #     temp_audio_file.write(audio_data)
        #     temp_audio_path = temp_audio_file.name

    # 构建 URL
    # audio_url = f"http://localhost:8000/audio/{os.path.basename(temp_audio_path)}"
    
    # 根据条件返回不同的结果
    if input.text == "新建对话":
        return {"out": "开始新对话了"}
    else:
        return {"out": result['out']}
    
class TextInput1(BaseModel):
    text: str
    weiruan: int
    order: bool


@app.post("/onlyglm4/")
def api_onlyglm4(input: TextInput1):
    global edge,cosy,isorder
    isorder = input.order
    if input.weiruan == 1:
        edge = True
        cosy = False
    elif  input.weiruan == 2:
        edge = False
        cosy = False
    elif input.weiruan == 3:
        edge = False
        cosy = True        
    else:
        pass
    # 这里是人物模版文件路径
    preset_dialogue_file_path = os.path.join('moban', f'{MB}.txt')
    
    result = None  # 初始化result变量

    # 判断输入文本是否为“新建对话”
    if input.text == "新建对话":
        # 执行新建对话的逻辑
        newtalk()
    elif input.text == "这是一条测试信息":
           result = "api启动成功" 
    else:
        # 执行原始逻辑
        result = onlyglm4(preset_dialogue_file_path, input.text)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
    
    # 根据条件返回不同的结果
    if input.text == "新建对话":
        return {"out": "开始新对话了"}
    elif input.text == "这是一条测试信息":
        return {"out": "api启动成功"}
    else:
        return {"out": result['out']}
    


# 定义用于更新配置的请求模型
class UpdateConfigRequest(BaseModel):
    TTS: str
    MB: str
    Text_language: str
    Interval: float
    R: str
    T: str
    GSV: bool
    Edgevoive: str
    Vosyspeaker: str
@app.post("/update_config/")
async def update_config(config_update: UpdateConfigRequest):
    # 直接使用从请求体中解析出的属性更新全局变量
    global TTS, MB, Text_language, Interval, R, T, client, config_file_path ,GSV, Edgevoive,Vosyspeaker
    
    # 更新全局配置参数

    MB = config_update.MB
    Text_language = config_update.Text_language
    Interval = config_update.Interval
    R = config_update.R
    T = config_update.T
    oldgsv = GSV
    GSV = config_update.GSV
    Edgevoive = config_update.Edgevoive
    Vosyspeaker = config_update.Vosyspeaker
    if oldgsv:
        if GSV:
            pass
        else:
            del client
    else:
        if GSV:
            base_path = 'moys'
            file_name = os.path.join('.', f'{TTS}.txt')
            config_file_path = os.path.join(base_path, file_name)
            client = Client("http://localhost:9872/")
            clientdata(client) 
        else:
            pass

    if config_update.TTS != TTS:
        TTS = config_update.TTS
        if GSV:
            # 重新计算 config_file_path 以反映新的 TTS 值
            base_path = 'moys'
            file_name = os.path.join('.', f'{TTS}.txt')
            config_file_path = os.path.join(base_path, file_name)
            client = Client("http://localhost:9872/")
            clientdata(client)
    # 调用函数保存全局变量
    save_globals_to_json('api/api.json')        
    
    return {
        "message": "Configuration updated successfully.",
        "updated_config": {
            "TTS": TTS,
            "MB": MB,
            "Text_language": Text_language,
            "Interval": Interval,
            "R": R,
            "T": T,
            "GSV": GSV,
            "Edgevoive": Edgevoive,
            "Vosyspeaker":Vosyspeaker
        }
    }

# 修改 get_audio_file 函数以支持从临时文件流式传输音频数据
@app.get("/audio/{filename}", response_class=FileResponse)
def get_audio_file(filename: str):
    # 构建完整的文件路径
    audio_file_path = os.path.join(AUDIO_FILES_DIRECTORY, filename)
    
    # 如果文件在 AUDIO_FILES_DIRECTORY 中，直接返回 FileResponse
    if os.path.exists(audio_file_path):
        return FileResponse(audio_file_path, media_type='audio/wav')
    
    # 如果文件不在 AUDIO_FILES_DIRECTORY 中，尝试从临时文件中流式传输
    try:
        with open(audio_file_path, 'rb') as audio_file:
            return StreamingResponse(audio_file, media_type='audio/wav')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found")

# 用于关闭服务的路由
@app.post("/shutdown")
async def shutdown(request: Request):


    # 获取Uvicorn的实例
    server = request.app.state.server
    # 关闭服务器
    server.should_exit = True
    # 返回一个响应，表示服务器正在关闭
    return {"message": "Shutting down server."}

# 主函数，用于启动Uvicorn服务器
if __name__ == "__main__":
    # 将Uvicorn服务器实例存储在应用程序状态中
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))
    app.state.server = server
    # 启动服务器
    server.run()
# server = None

# def apistar():
#     global server
#     web()
#     config = Config(app=app, host='0.0.0.0', port=8000)
#     server = Server(config=config)
#     server.run()  # run() 方法会阻塞执行，直到服务器关闭

# def apiclose():
#     global server, driver
#     closedriver(driver)
#     if server:
#         # 停止服务器
#         server.should_exit = True

# if __name__ == '__main__':
#     apistar()
