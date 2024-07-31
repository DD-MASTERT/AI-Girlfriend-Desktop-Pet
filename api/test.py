import json
from kimi import kimiapi
from glm4 import glm4api
from deepseek2 import deepseekv2
from chat.baidu import translate_ja_to_zh
from chat.tenxun import txtra
from chat.baidut import translate_text
import azure.cognitiveservices.speech as speechsdk
import asyncio
from colorama import Fore, Style, init
init()

def print1(*args, sep=' ', end='\n', file=None):
    # 将所有参数转换为字符串并拼接
    text = sep.join(map(str, args))
    # 使用绿色打印文本
    print(Fore.BLUE + text + Style.RESET_ALL, end=end, file=file)

def print0(*args, sep=' ', end='\n', file=None):
    # 将所有参数转换为字符串并拼接
    text = sep.join(map(str, args))
    # 使用绿色打印文本
    print(Fore.GREEN + text + Style.RESET_ALL, end=end, file=file)

speech_key = None
service_region = None
async def synthesize_text_to_speech(text: str = '你好', voice: str = 'zh-CN-XiaoxiaoMultilingualNeural',output: str = 'edge/audio.wav'):

    global speech_key,service_region
    try:

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
            print0('语音合成完成，当前测试为多语言晓晓，多语音音色可用')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print0("语音合成已取消: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print0("语音合成失败，当前测试为多语言晓晓，多语音音色不可用，错误详情: {}".format(cancellation_details.error_details))
    except Exception as e:
        # 捕获到异常时执行的代码
        print0("微软azure填写错误或者已失效，多语音音色不可用--错误：", e)                
class test:
    def __init__(self) -> None:
        self.gsv = None
        self.chatglm_refresh_token = None
        self.assistant_id = None
        self.refresh_token = None
        self.usertoken = None
        self.TXSecretId = None
        self.TXSecretKey = None
        self.BDaccess_token = None
        self.APPID = None
        self.SECRET = None
        self.speech_key = None
        self.service_region = None
        self.apiglm4 = glm4api()
        self.apikimi = kimiapi()
        self.apideepseek = deepseekv2()
    def loadjson(self):
        with open('gsv.json', 'r', encoding='utf-8') as f:
            gsv_data = json.load(f)
        self.gsv = gsv_data['gsv'] 
        self.chatglm_refresh_token = gsv_data['chatglm_refresh_token'] 
        self.assistant_id = gsv_data['assistant_id']
        self.refresh_token = gsv_data['refresh_token'] 
        self.usertoken = gsv_data['usertoken']
        with open('api.json', 'r', encoding='utf-8') as f:
            api_data = json.load(f)
        self.TXSecretId = api_data['TXSecretId'] 
        self.TXSecretKey = api_data['TXSecretKey']
        self.BDaccess_token = api_data['BDaccess_token']
        self.APPID = api_data['APPID']
        self.SECRET = api_data['SECRET']
        self.speech_key = api_data['speech_key']
        self.service_region = api_data['service_region']
    def testmodel(self):
        self.apiglm4.chatglm_refresh_token = self.chatglm_refresh_token
        self.apiglm4.assistant_id = self.assistant_id
        self.apikimi.refresh_token = self.refresh_token
        self.apideepseek.usertoken = self.usertoken
        text = '你好'
        if self.apiglm4.chatglm_refresh_token!="" and self.apiglm4.assistant_id!="":
            try:
                # 尝试执行可能引发错误的代码
                self.apiglm4.chatglm_refresh_token, self.apiglm4.token = self.apiglm4.gettoken()
                re = self.apiglm4.talknew()

                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("chatglm_refresh_token和assistant_id填写正确，未失效,glm4模型可用")
                else:
                    print0("没有收到glm4模型回复，其他错误，glm4模型不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("chatglm_refresh_token和assistant_id填写错误或者已失效，glm4模型不可用--错误：", e)
        else:
            print0("chatglm_refresh_token和assistant_id填写为空或者缺一个未填，glm4模型不可用")        
        if self.apikimi.refresh_token!="":
            try:
                # 尝试执行可能引发错误的代码
                self.apikimi.refresh_token, self.apikimi.token = self.apikimi.gettoken()
                self.apikimi.getnewtalk()
                re = self.apikimi.talknext(text)
                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("refresh_token填写正确，未失效，kimi模型可用")
                else:
                    print0("没有收到kimi模型回复，其他错误，kimi模型不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("refresh_token填写错误或者已失效，kimi模型不可用--错误：", e)
        else:
            print0("refresh_token填写为空，kimi模型不可用")
        if self.apideepseek.usertoken!="":
            try:
                # 尝试执行可能引发错误的代码
                self.apideepseek.newtalk()
                re = self.apideepseek.talknext(text)
                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("usertoken填写正确，未失效，deepseek模型可用")
                else:
                    print0("没有收到deepseek模型回复，其他错误，deepseek模型不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("usertoken填写错误或者已失效，deepseek模型不可用--错误：", e)
        else:
            print0("usertoken填写为空，deepseek模型不可用") 
    def testfanyi(self):
        text = "何かレムにお手伝いできることがあれば、いつでも言ってください。"
        TXS = "ja"
        TXT = "zh"
        BDS = "jp"
        BDT = "zh"
        BDTS = "jp"
        BDTT = "zh"        
        if self.TXSecretId!="" and self.TXSecretKey!="":
            try:
                # 尝试执行可能引发错误的代码
                re = txtra(text, self.TXSecretId, self.TXSecretKey, TXS, TXT)
                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("腾讯翻译填写正确，未失效，腾讯翻译可用")
                else:
                    print0("没有收到腾讯翻译回复，其他错误，腾讯翻译不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("腾讯翻译填写错误或者已失效，腾讯翻译不可用--错误：", e)
        else:
            print0("腾讯翻译填写为空或填写缺一，腾讯翻译不可用") 
        if self.APPID!="" and self.SECRET!="":
            try:
                # 尝试执行可能引发错误的代码
                re = translate_text(text, self.APPID, self.SECRET, BDTS, BDTT)
                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("百度翻译填写正确，未失效，百度翻译可用")
                else:
                    print0("没有收到百度翻译回复，其他错误，百度翻译不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("百度翻译填写错误或者已失效，百度翻译不可用--错误：", e)
        else:
            print0("百度翻译填写为空或填写缺一，百度翻译不可用")
        if self.BDaccess_token!="":
            try:
                # 尝试执行可能引发错误的代码
                re = translate_ja_to_zh(text, self.BDaccess_token, BDS, BDT)
                
                # 检查re变量是否为空
                if re:
                    print1("收到的回复", re)
                    print0("百度ai翻译填写正确，未失效，百度ai翻译可用")
                else:
                    print0("没有收到百度ai翻译回复，其他错误，百度ai翻译不可用")
            except Exception as e:
                # 捕获到异常时执行的代码
                print0("百度ai翻译填写错误或者已失效，百度ai翻译不可用--错误：", e)
        else:
            print0("百度ai翻译填写为空或填写缺一，百度ai翻译不可用")
    def azure(self):
        global speech_key,service_region
        speech_key = self.speech_key
        service_region = self.service_region
alltest = test()
alltest.loadjson()
alltest.testmodel()
alltest.testfanyi()
alltest.azure()
if speech_key!="" and service_region!="":
    asyncio.run(synthesize_text_to_speech())
else:
    print0("微软azureAPI填写为空或缺一，多语言语音不可用")  
    
print("程序执行完毕。按任意键退出。")
input()  # 用户按下任意键后，程序会接收到输入并退出           



