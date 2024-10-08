'''
按中英混合识别
按日英混合识别
多语种启动切分识别语种
全部按中文识别
全部按英文识别
全部按日文识别
'''
import os, re, logging
import LangSegment
logging.getLogger("markdown_it").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("charset_normalizer").setLevel(logging.ERROR)
logging.getLogger("torchaudio._extension").setLevel(logging.ERROR)
import pdb
import torch
#import dashscope
from http import HTTPStatus
#from dashscope import Generation
import subprocess
from tools.i18n.i18n import I18nAuto
import numpy as np
import soundfile as sf
import shutil
from chat.kimi import kimiapi
from chat.glm4 import glm4api
from chat.deepseek2 import deepseekv2
from scipy.io import wavfile
import threading
import json
import time

LLM = "glm"

apiglm4 = glm4api()
apikimi = kimiapi()
apideepseek = deepseekv2()
def retoken():
    global apiglm4,apikimi,apideepseek
    with open('GPT_SoVITS/config.json', 'r', encoding='utf-8') as file:
        gsvconfig = json.load(file)  # 加载JSON数据
    apiglm4.chatglm_refresh_token = gsvconfig['chatglm_refresh_token']
    apiglm4.assistant_id = gsvconfig['assistant_id']
    apikimi.refresh_token = gsvconfig['refresh_token']
    apideepseek.usertoken = gsvconfig['usertoken'] 
def newtalk():
    global LLM,apiglm4,apikimi,apideepseek
    if LLM == "glm": 
        apiglm4.talknew()
    elif LLM == "kimi":
        apikimi.getnewtalk()
    elif LLM == "deepseek":  
        apideepseek.newtalk()
    else:
        print("错误")    
def uptoken():
    interval=600
    global apiglm4,apikimi,LLM ,apideepseek   
    with open('GPT_SoVITS/config.json', 'r', encoding='utf-8') as file:
        gsvconfig = json.load(file)  # 加载JSON数据   
    if LLM == "glm":
        interval=1800
        chatglm_refresh_token, token = apiglm4.gettoken()
        gsvconfig['chatglm_refresh_token'] = chatglm_refresh_token
        apiglm4.chatglm_refresh_token = chatglm_refresh_token
        apiglm4.token = token
        with open('GPT_SoVITS/config.json', 'w', encoding='utf-8') as file:
            json.dump(gsvconfig, file, ensure_ascii=False, indent=4)
    elif LLM == "kimi":
        refresh_token, token = apikimi.gettoken()
        gsvconfig['refresh_token'] = refresh_token
        apikimi.refresh_token = refresh_token
        apikimi.token = token
        with open('GPT_SoVITS/config.json', 'w', encoding='utf-8') as file:
            json.dump(gsvconfig, file, ensure_ascii=False, indent=4)  
    else:
        print("deepseek2模型")
    return interval   
stop_event = threading.Event()           
def looptime():
    global stop_event
    i = 1
    while not stop_event.is_set():
        interval = uptoken() 
        if i == 1:
            newtalk()                          
        print(f"Thread is waiting for {interval} seconds")
        if stop_event.wait(interval):
            print("Thread received stop event")
            break
        i+=1    # 等待20分钟
     
retoken()
thread = None
def startalk():   
    global thread    
    thread = threading.Thread(target=looptime)
    thread.daemon = True  # 设置为守护线程，这样当主程序退出时，线程也会退出
    thread.start() 
    return "可以开始对话了" 
def stoptalk():
    global thread,stop_event
    stop_event.set()
    thread.join()  # 等待线程结束
    print("Thread has been terminated.")            
    return "模型已关闭"
i18n = I18nAuto()

if os.path.exists("./gweight.txt"):
    with open("./gweight.txt", 'r', encoding="utf-8") as file:
        gweight_data = file.read()
        gpt_path = os.environ.get(
            "gpt_path", gweight_data)
else:
    gpt_path = os.environ.get(
        "gpt_path", "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt")

if os.path.exists("./sweight.txt"):
    with open("./sweight.txt", 'r', encoding="utf-8") as file:
        sweight_data = file.read()
        sovits_path = os.environ.get("sovits_path", sweight_data)
else:
    sovits_path = os.environ.get("sovits_path", "GPT_SoVITS/pretrained_models/s2G488k.pth")
# gpt_path = os.environ.get(
#     "gpt_path", "pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
# )
# sovits_path = os.environ.get("sovits_path", "pretrained_models/s2G488k.pth")
cnhubert_base_path = os.environ.get(
    "cnhubert_base_path", "GPT_SoVITS/pretrained_models/chinese-hubert-base"
)
bert_path = os.environ.get(
    "bert_path", "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"
)
infer_ttswebui = os.environ.get("infer_ttswebui", 9872)
infer_ttswebui = int(infer_ttswebui)
is_share = os.environ.get("is_share", "False")
is_share = eval(is_share)
if "_CUDA_VISIBLE_DEVICES" in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = os.environ["_CUDA_VISIBLE_DEVICES"]
is_half = eval(os.environ.get("is_half", "True")) and torch.cuda.is_available()
import gradio as gr
from transformers import AutoModelForMaskedLM, AutoTokenizer
import numpy as np
import librosa
from feature_extractor import cnhubert

cnhubert.cnhubert_base_path = cnhubert_base_path

from module.models import SynthesizerTrn
from AR.models.t2s_lightning_module import Text2SemanticLightningModule
from text import cleaned_text_to_sequence
from text.cleaner import clean_text
from time import time as ttime
from module.mel_processing import spectrogram_torch
from my_utils import load_audio
from tools.i18n.i18n import I18nAuto

i18n = I18nAuto()

# os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # 确保直接启动推理UI时也能够设置。

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

tokenizer = AutoTokenizer.from_pretrained(bert_path)
bert_model = AutoModelForMaskedLM.from_pretrained(bert_path)
if is_half == True:
    bert_model = bert_model.half().to(device)
else:
    bert_model = bert_model.to(device)


def get_bert_feature(text, word2ph):
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors="pt")
        for i in inputs:
            inputs[i] = inputs[i].to(device)
        res = bert_model(**inputs, output_hidden_states=True)
        res = torch.cat(res["hidden_states"][-3:-2], -1)[0].cpu()[1:-1]
    assert len(word2ph) == len(text)
    phone_level_feature = []
    for i in range(len(word2ph)):
        repeat_feature = res[i].repeat(word2ph[i], 1)
        phone_level_feature.append(repeat_feature)
    phone_level_feature = torch.cat(phone_level_feature, dim=0)
    return phone_level_feature.T


class DictToAttrRecursive(dict):
    def __init__(self, input_dict):
        super().__init__(input_dict)
        for key, value in input_dict.items():
            if isinstance(value, dict):
                value = DictToAttrRecursive(value)
            self[key] = value
            setattr(self, key, value)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"Attribute {item} not found")

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = DictToAttrRecursive(value)
        super(DictToAttrRecursive, self).__setitem__(key, value)
        super().__setattr__(key, value)

    def __delattr__(self, item):
        try:
            del self[item]
        except KeyError:
            raise AttributeError(f"Attribute {item} not found")


ssl_model = cnhubert.get_model()
if is_half == True:
    ssl_model = ssl_model.half().to(device)
else:
    ssl_model = ssl_model.to(device)


def change_sovits_weights(sovits_path):
    global vq_model, hps
    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = dict_s2["config"]
    hps = DictToAttrRecursive(hps)
    hps.model.semantic_frame_rate = "25hz"
    vq_model = SynthesizerTrn(
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model
    )
    if ("pretrained" not in sovits_path):
        del vq_model.enc_q
    if is_half == True:
        vq_model = vq_model.half().to(device)
    else:
        vq_model = vq_model.to(device)
    vq_model.eval()
    print(vq_model.load_state_dict(dict_s2["weight"], strict=False))
    with open("./sweight.txt", "w", encoding="utf-8") as f:
        f.write(sovits_path)


change_sovits_weights(sovits_path)


def change_gpt_weights(gpt_path):
    global hz, max_sec, t2s_model, config
    hz = 50
    dict_s1 = torch.load(gpt_path, map_location="cpu")
    config = dict_s1["config"]
    max_sec = config["data"]["max_sec"]
    t2s_model = Text2SemanticLightningModule(config, "****", is_train=False)
    t2s_model.load_state_dict(dict_s1["weight"])
    if is_half == True:
        t2s_model = t2s_model.half()
    t2s_model = t2s_model.to(device)
    t2s_model.eval()
    total = sum([param.nelement() for param in t2s_model.parameters()])
    print("Number of parameter: %.2fM" % (total / 1e6))
    with open("./gweight.txt", "w", encoding="utf-8") as f: f.write(gpt_path)


change_gpt_weights(gpt_path)


def get_spepc(hps, filename):
    audio = load_audio(filename, int(hps.data.sampling_rate))
    audio = torch.FloatTensor(audio)
    audio_norm = audio
    audio_norm = audio_norm.unsqueeze(0)
    spec = spectrogram_torch(
        audio_norm,
        hps.data.filter_length,
        hps.data.sampling_rate,
        hps.data.hop_length,
        hps.data.win_length,
        center=False,
    )
    return spec


dict_language = {
    i18n("中文"): "all_zh",#全部按中文识别
    i18n("英文"): "en",#全部按英文识别#######不变
    i18n("日文"): "all_ja",#全部按日文识别
    i18n("中英混合"): "zh",#按中英混合识别####不变
    i18n("日英混合"): "ja",#按日英混合识别####不变
    i18n("多语种混合"): "auto",#多语种启动切分识别语种
}


def clean_text_inf(text, language):
    phones, word2ph, norm_text = clean_text(text, language)
    phones = cleaned_text_to_sequence(phones)
    return phones, word2ph, norm_text

dtype=torch.float16 if is_half == True else torch.float32
def get_bert_inf(phones, word2ph, norm_text, language):
    language=language.replace("all_","")
    if language == "zh":
        bert = get_bert_feature(norm_text, word2ph).to(device)#.to(dtype)
    else:
        bert = torch.zeros(
            (1024, len(phones)),
            dtype=torch.float16 if is_half == True else torch.float32,
        ).to(device)

    return bert


splits = {"，", "。", "？", "！", ",", ".", "?", "!", "~", ":", "：", "—", "…", }


def get_first(text):
    pattern = "[" + "".join(re.escape(sep) for sep in splits) + "]"
    text = re.split(pattern, text)[0].strip()
    return text


def get_phones_and_bert(text,language):
    if language in {"en","all_zh","all_ja"}:
        language = language.replace("all_","")
        if language == "en":
            LangSegment.setfilters(["en"])
            formattext = " ".join(tmp["text"] for tmp in LangSegment.getTexts(text))
        else:
            # 因无法区别中日文汉字,以用户输入为准
            formattext = text
        while "  " in formattext:
            formattext = formattext.replace("  ", " ")
        phones, word2ph, norm_text = clean_text_inf(formattext, language)
        if language == "zh":
            bert = get_bert_feature(norm_text, word2ph).to(device)
        else:
            bert = torch.zeros(
                (1024, len(phones)),
                dtype=torch.float16 if is_half == True else torch.float32,
            ).to(device)
    elif language in {"zh", "ja","auto"}:
        textlist=[]
        langlist=[]
        LangSegment.setfilters(["zh","ja","en","ko"])
        if language == "auto":
            for tmp in LangSegment.getTexts(text):
                if tmp["lang"] == "ko":
                    langlist.append("zh")
                    textlist.append(tmp["text"])
                else:
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
        else:
            for tmp in LangSegment.getTexts(text):
                if tmp["lang"] == "en":
                    langlist.append(tmp["lang"])
                else:
                    # 因无法区别中日文汉字,以用户输入为准
                    langlist.append(language)
                textlist.append(tmp["text"])
        print(textlist)
        print(langlist)
        phones_list = []
        bert_list = []
        norm_text_list = []
        for i in range(len(textlist)):
            lang = langlist[i]
            phones, word2ph, norm_text = clean_text_inf(textlist[i], lang)
            bert = get_bert_inf(phones, word2ph, norm_text, lang)
            phones_list.append(phones)
            norm_text_list.append(norm_text)
            bert_list.append(bert)
        bert = torch.cat(bert_list, dim=1)
        phones = sum(phones_list, [])
        norm_text = ''.join(norm_text_list)

    return phones,bert.to(dtype),norm_text


def merge_short_text_in_array(texts, threshold):
    if (len(texts)) < 2:
        return texts
    result = []
    text = ""
    for ele in texts:
        text += ele
        if len(text) >= threshold:
            result.append(text)
            text = ""
    if (len(text) > 0):
        if len(result) == 0:
            result.append(text)
        else:
            result[len(result) - 1] += text
    return result

def get_tts_wav(ref_wav_path, prompt_text, prompt_language, text, text_language, how_to_cut=i18n("不切"), top_k=20, top_p=0.6, temperature=0.6, interval=0.3, ref_free = False):
    if prompt_text is None or len(prompt_text) == 0:
        ref_free = True
    t0 = ttime()
    prompt_language = dict_language[prompt_language]
    text_language = dict_language[text_language]
    if not ref_free:
        prompt_text = prompt_text.strip("\n")
        if (prompt_text[-1] not in splits): prompt_text += "。" if prompt_language != "en" else "."
        print(i18n("实际输入的参考文本:"), prompt_text)
    text = text.strip("\n")
    if (text[0] not in splits and len(get_first(text)) < 4): text = "。" + text if text_language != "en" else "." + text
    
    print(i18n("实际输入的目标文本:"), text)
    zero_wav = np.zeros(
        int(hps.data.sampling_rate * interval),
        dtype=np.float16 if is_half == True else np.float32,
    )
    with torch.no_grad():
        wav16k, sr = librosa.load(ref_wav_path, sr=16000)
        if (wav16k.shape[0] > 160000 or wav16k.shape[0] < 48000):
            raise OSError(i18n("参考音频在3~10秒范围外，请更换！"))
        wav16k = torch.from_numpy(wav16k)
        zero_wav_torch = torch.from_numpy(zero_wav)
        if is_half == True:
            wav16k = wav16k.half().to(device)
            zero_wav_torch = zero_wav_torch.half().to(device)
        else:
            wav16k = wav16k.to(device)
            zero_wav_torch = zero_wav_torch.to(device)
        wav16k = torch.cat([wav16k, zero_wav_torch])
        ssl_content = ssl_model.model(wav16k.unsqueeze(0))[
            "last_hidden_state"
        ].transpose(
            1, 2
        )  # .float()
        codes = vq_model.extract_latent(ssl_content)
   
        prompt_semantic = codes[0, 0]
    t1 = ttime()

    if (how_to_cut == i18n("凑四句一切")):
        text = cut1(text)
    elif (how_to_cut == i18n("凑50字一切")):
        text = cut2(text)
    elif (how_to_cut == i18n("按。.！!?？切")):
        text = cut3(text)
    elif (how_to_cut == i18n("按英文句号.切")):
        text = cut4(text)
    elif (how_to_cut == i18n("按标点符号切")):
        text = cut5(text)
    elif (how_to_cut == i18n("断句切")):
        text = cut6(text)
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    print(i18n("实际输入的目标文本(切句后):"), text)
    texts = text.split("\n")
    texts = merge_short_text_in_array(texts, 5)
    audio_opt = []
    if not ref_free:
        phones1,bert1,norm_text1=get_phones_and_bert(prompt_text, prompt_language)

    for text in texts:
        # 解决输入目标文本的空行导致报错的问题
        if (len(text.strip()) == 0):
            continue
        if (text[-1] not in splits): text += "。" if text_language != "en" else "."
        print(i18n("实际输入的目标文本(每句):"), text)
        phones2,bert2,norm_text2=get_phones_and_bert(text, text_language)
        print(i18n("前端处理后的文本(每句):"), norm_text2)
        if not ref_free:
            bert = torch.cat([bert1, bert2], 1)
            all_phoneme_ids = torch.LongTensor(phones1+phones2).to(device).unsqueeze(0)
        else:
            bert = bert2
            all_phoneme_ids = torch.LongTensor(phones2).to(device).unsqueeze(0)

        bert = bert.to(device).unsqueeze(0)
        all_phoneme_len = torch.tensor([all_phoneme_ids.shape[-1]]).to(device)
        prompt = prompt_semantic.unsqueeze(0).to(device)
        t2 = ttime()
        with torch.no_grad():
            # pred_semantic = t2s_model.model.infer(
            pred_semantic, idx = t2s_model.model.infer_panel(
                all_phoneme_ids,
                all_phoneme_len,
                None if ref_free else prompt,
                bert,
                # prompt_phone_len=ph_offset,
                top_k=top_k,
                top_p=top_p,
                temperature=temperature,
                early_stop_num=hz * max_sec,
            )
        t3 = ttime()
        # print(pred_semantic.shape,idx)
        pred_semantic = pred_semantic[:, -idx:].unsqueeze(
            0
        )  # .unsqueeze(0)#mq要多unsqueeze一次
        refer = get_spepc(hps, ref_wav_path)  # .to(device)
        if is_half == True:
            refer = refer.half().to(device)
        else:
            refer = refer.to(device)
        # audio = vq_model.decode(pred_semantic, all_phoneme_ids, refer).detach().cpu().numpy()[0, 0]
        audio = (
            vq_model.decode(
                pred_semantic, torch.LongTensor(phones2).to(device).unsqueeze(0), refer
            )
                .detach()
                .cpu()
                .numpy()[0, 0]
        )  ###试试重建不带上prompt部分
        max_audio=np.abs(audio).max()#简单防止16bit爆音
        if max_audio>1:audio/=max_audio
        audio_opt.append(audio)
        audio_opt.append(zero_wav)
        t4 = ttime()
    print("%.3f\t%.3f\t%.3f\t%.3f" % (t1 - t0, t2 - t1, t3 - t2, t4 - t3))
    yield hps.data.sampling_rate, (np.concatenate(audio_opt, 0) * 32768).astype(
        np.int16
    )
    # 指定保存音频的文件路径
    file_path = 'moys/temp/audio.wav'

    # 调用保存音频的函数
    save_audio(hps.data.sampling_rate, np.concatenate(audio_opt, 0), file_path)

# 保存音频数据到文件
def save_audio(sampling_rate, audio_data, file_path):
    # 确保音频数据是16位PCM格式
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    wavfile.write(file_path, sampling_rate, audio_data)



def split(todo_text):
    todo_text = todo_text.replace("……", "。").replace("——", "，")
    if todo_text[-1] not in splits:
        todo_text += "。"
    i_split_head = i_split_tail = 0
    len_text = len(todo_text)
    todo_texts = []
    while 1:
        if i_split_head >= len_text:
            break  # 结尾一定有标点，所以直接跳出即可，最后一段在上次已加入
        if todo_text[i_split_head] in splits:
            i_split_head += 1
            todo_texts.append(todo_text[i_split_tail:i_split_head])
            i_split_tail = i_split_head
        else:
            i_split_head += 1
    return todo_texts


def cut1(inp):
    inp = inp.strip("\n")
    inps = split(inp)
    split_idx = list(range(0, len(inps), 4))
    split_idx[-1] = None
    if len(split_idx) > 1:
        opts = []
        for idx in range(len(split_idx) - 1):
            opts.append("".join(inps[split_idx[idx]: split_idx[idx + 1]]))
    else:
        opts = [inp]
    return "\n".join(opts)



def cut6(inp):
    inp = inp.strip("\n")
    # 调用 call_dashscope 函数并传入用户输入
    inp = call_dashscope(inp)
    # 使用正则表达式分割字符串，匹配中文句号和英文句号
    items = re.split(r'[。.！!?？]', inp.strip())
    # 使用列表推导式去除可能的空字符串元素
    items = [item for item in items if item]
    # 使用换行符连接列表中的元素
    return "\n".join(items)

def cut2(inp):
    inp = inp.strip("\n")
    inps = split(inp)
    if len(inps) < 2:
        return inp
    opts = []
    summ = 0
    tmp_str = ""
    for i in range(len(inps)):
        summ += len(inps[i])
        tmp_str += inps[i]
        if summ > 50:
            summ = 0
            opts.append(tmp_str)
            tmp_str = ""
    if tmp_str != "":
        opts.append(tmp_str)
    # print(opts)
    if len(opts) > 1 and len(opts[-1]) < 50:  ##如果最后一个太短了，和前一个合一起
        opts[-2] = opts[-2] + opts[-1]
        opts = opts[:-1]
    return "\n".join(opts)


def cut3(inp):
    inp = inp.strip("\n")
    # 使用正则表达式分割字符串，匹配中文句号和英文句号
    items = re.split(r'[。.！!?？]', inp.strip())
    # 使用列表推导式去除可能的空字符串元素
    items = [item for item in items if item]
    # 使用换行符连接列表中的元素
    return "\n".join(items)



def cut4(inp):
    inp = inp.strip("\n")
    return "\n".join(["%s" % item for item in inp.strip(".").split(".")])


# contributed by https://github.com/AI-Hobbyist/GPT-SoVITS/blob/main/GPT_SoVITS/inference_webui.py
def cut5(inp):
    # if not re.search(r'[^\w\s]', inp[-1]):
    # inp += '。'
    inp = inp.strip("\n")
    punds = r'[,.;?!、，。？！;：…]'
    items = re.split(f'({punds})', inp)
    mergeitems = ["".join(group) for group in zip(items[::2], items[1::2])]
    # 在句子不存在符号或句尾无符号的时候保证文本完整
    if len(items)%2 == 1:
        mergeitems.append(items[-1])
    opt = "\n".join(mergeitems)
    return opt


def custom_sort_key(s):
    # 使用正则表达式提取字符串中的数字部分和非数字部分
    parts = re.split('(\d+)', s)
    # 将数字部分转换为整数，非数字部分保持不变
    parts = [int(part) if part.isdigit() else part for part in parts]
    return parts


def change_choices():
    SoVITS_names, GPT_names = get_weights_names()
    return {"choices": sorted(SoVITS_names, key=custom_sort_key), "__type__": "update"}, {"choices": sorted(GPT_names, key=custom_sort_key), "__type__": "update"}


pretrained_sovits_name = "GPT_SoVITS/pretrained_models/s2G488k.pth"
pretrained_gpt_name = "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
SoVITS_weight_root = "SoVITS_weights"
GPT_weight_root = "GPT_weights"
os.makedirs(SoVITS_weight_root, exist_ok=True)
os.makedirs(GPT_weight_root, exist_ok=True)


def get_weights_names():
    SoVITS_names = [pretrained_sovits_name]
    for name in os.listdir(SoVITS_weight_root):
        if name.endswith(".pth"): SoVITS_names.append("%s/%s" % (SoVITS_weight_root, name))
    GPT_names = [pretrained_gpt_name]
    for name in os.listdir(GPT_weight_root):
        if name.endswith(".ckpt"): GPT_names.append("%s/%s" % (GPT_weight_root, name))
    return SoVITS_names, GPT_names


# 添加Dashscope的调用函数
def call_dashscope(user_input):
    # 定义助词列表
    particles = ['が', 'を', 'は', 'に']
    
    # 处理字符串，添加逗号
    result_content = user_input
    for particle in particles:
        # 找到每个助词的位置
        start = 0
        while True:
            start = result_content.find(particle, start)
            if start == -1:
                break
            # 在助词后添加逗号
            result_content = result_content[:start + len(particle)] + '、' + result_content[start + len(particle):]
            # 移动开始位置，以避免重复添加逗号
            start += len(particle) + 1
    
    return result_content







def save_model_config(GPT_dropdown, SoVITS_dropdown, inp_ref, prompt_text, prompt_language):
    config_dir = "moys"
    config_dir1 = r"moys\audio"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # 复制参考音频文件到配置目录
    copy_ref_audio_path = os.path.join(config_dir1, os.path.basename(inp_ref))
    shutil.copy(inp_ref, copy_ref_audio_path)
    
    gpt_model_name = os.path.basename(GPT_dropdown).split('-')[0]
    config_file_path = os.path.join(config_dir, f"{gpt_model_name}.txt")
    
    with open(config_file_path, 'w', encoding='utf-8') as f:
        f.write(f"GPT_model_path={GPT_dropdown}\n")
        f.write(f"SoVITS_model_path={SoVITS_dropdown}\n")
        f.write(f"ref_audio_path={copy_ref_audio_path}\n")  # 修改写入的路径为复制文件的路径
        f.write(f"ref_text={prompt_text}\n")
        f.write(f"ref_audio_language={prompt_language}\n")
    
    return f"Configuration saved to {config_file_path}"

def load_model_config(config_file_name):
    config_dir = "moys"
    # 因为 config_file_name 现在是字符串，我们直接使用它来构造文件路径
    config_file_path = os.path.join(config_dir, config_file_name)
    
    with open(config_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    config = {}
    for line in lines:
        key, value = line.strip().split('=')
        config[key] = value
    
    # 返回一个包含所有组件期望值的字典
    return (
        config["GPT_model_path"],
        config["SoVITS_model_path"],
        config["ref_audio_path"],
        config["ref_text"],
        config["ref_audio_language"]
    )
def refresh_config_files():
    # 获取最新的配置文件列表
    config_files = get_config_files()
    # 创建一个新的文件名列表，只包含文件名
    config_file_names = [os.path.basename(path) for path in config_files]
    
    # 返回一个更新的配置，告诉 Gradio 更新下拉菜单的选项
    return {"choices": config_file_names, "__type__": "update"}



    # 辅助函数，用于处理 load_model_config 函数的输出
def handle_load_model_config(config_file_name, GPT_dropdown, SoVITS_dropdown, inp_ref, prompt_text, prompt_language):
    # 调用原始函数获取配置
    config = load_model_config(config_file_name)
    
    # 更新组件的值
    GPT_dropdown.update(value=config.get("GPT_model_path"))
    SoVITS_dropdown.update(value=config.get("SoVITS_model_path"))
    inp_ref.update(value=config.get("ref_audio_path"))
    prompt_text.update(value=config.get("ref_text"))
    prompt_language.update(value=config.get("ref_audio_language"))

def get_config_files():
    config_dir = "moys"
    if not os.path.exists(config_dir):
        return []
    
    return [os.path.join(config_dir, f) for f in os.listdir(config_dir) if f.endswith('.txt')]

def echo(input_text):
    # 直接返回输入的文本
    return input_text


def find_latest_wav(source_dir, dest_dir):
    # 确保目标文件夹存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 初始化找到的wav文件路径
    wav_file_path = None

    # 遍历源文件夹
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.wav'):
                wav_file_path = os.path.join(root, file)
                # 找到第一个wav文件就退出循环
                break
        if wav_file_path:
            break  # 确保找到文件后不再继续遍历

    # 如果找到了wav文件，复制到目标文件夹
    if wav_file_path:
        base_name = os.path.basename(wav_file_path)
        file_name, file_ext = os.path.splitext(base_name)
        dest_file_path = os.path.join(dest_dir, base_name)
        
       # 检查目标文件夹中是否存在同名文件，并添加后缀以避免覆盖
        counter = 1
        while os.path.exists(dest_file_path):
            new_name = f"{file_name}({counter}){file_ext}"
            dest_file_path = os.path.join(dest_dir, new_name)
            counter += 1
        # 复制文件
        shutil.copy2(wav_file_path, dest_file_path)
        print(f"Copied WAV file to {dest_file_path}")
        return dest_file_path  # 返回复制的文件路径
    else:
        print("No WAV files found.")
        return None  # 没有找到 WAV 文件时返回 None




def on_download_click(textq_value):
    source_directory = r'moys/temp'  # 源文件夹路径
    destination_directory = textq_value
   # outputs.update_value(f"开始查找最新的WAV文件...")

    result = find_latest_wav(source_directory, destination_directory)  # 调用函数
  #  outputs.update_value(f"已保存到: {destination_directory}")
    return f"{result}已保存到: {destination_directory}"



def send(input):
    global LLM
    try:
        if LLM == "kimi":
            out = apikimi.talknext(input)
        elif LLM == "glm":
            out= apiglm4.talknext(input)       
        else:    
            out = apideepseek.talknext(input) 
    except Exception as e:
        # 打印异常信息，实际使用中可以根据需要决定是否打印
        print(f"发生错误：{e}")
        out = "报错"
    return "",out
def on_model_change(selected_model):
    global LLM
    LLM = selected_model
    print(f"Selected model: {selected_model}")

def new():
    global LLM    
    try:
        newtalk()
        out = "新对话建立成功"
    except Exception as e:
        # 打印异常信息，实际使用中可以根据需要决定是否打印
        print(f"发生错误：{e}")
        out = "建立失败"
    return out




SoVITS_names, GPT_names = get_weights_names()

with gr.Blocks(title="GPT-SoVITS WebUI") as app:

    gr.Markdown(
        value=i18n("本软件以MIT协议开源, 作者不对软件具备任何控制力, 使用软件者、传播软件导出的声音者自负全责. <br>如不认可该条款, 则不能使用或引用软件包内任何代码和文件. 详见根目录<b>LICENSE</b>.")
    )
    with gr.Group():
        gr.Markdown(value=i18n("模型切换"))
        with gr.Row():
            GPT_dropdown = gr.Dropdown(label=i18n("GPT模型列表"), choices=sorted(GPT_names, key=custom_sort_key), value=gpt_path, interactive=True)
            SoVITS_dropdown = gr.Dropdown(label=i18n("SoVITS模型列表"), choices=sorted(SoVITS_names, key=custom_sort_key), value=sovits_path, interactive=True)
            refresh_button = gr.Button(i18n("刷新模型路径"), variant="primary")
            refresh_button.click(fn=change_choices, inputs=[], outputs=[SoVITS_dropdown, GPT_dropdown])
            SoVITS_dropdown.change(change_sovits_weights, [SoVITS_dropdown], [])
            GPT_dropdown.change(change_gpt_weights, [GPT_dropdown], [])
        
        gr.Markdown(value=i18n("*请上传并填写参考信息"))
        with gr.Row():
            inp_ref = gr.Audio(label=i18n("请上传3~10秒内参考音频，超过会报错！"), type="filepath")
            with gr.Column():
                ref_text_free = gr.Checkbox(label=i18n("开启无参考文本模式。不填参考文本亦相当于开启。"), value=False, interactive=True, show_label=True)
                gr.Markdown(i18n("使用无参考文本模式时建议使用微调的GPT，听不清参考音频说的啥(不晓得写啥)可以开，开启后无视填写的参考文本。"))
                prompt_text = gr.Textbox(label=i18n("参考音频的文本"), value="")
            prompt_language = gr.Dropdown(
                label=i18n("参考音频的语种"), choices=[i18n("中文"), i18n("英文"), i18n("日文"), i18n("中英混合"), i18n("日英混合"), i18n("多语种混合")], value=i18n("中文")
            )

        gr.Markdown(value=i18n("*请填写需要合成的目标文本和语种模式"))
        with gr.Row():
            with gr.Row():
                text = gr.Textbox(label=i18n("需要合成的文本"), value="")
              
                text_language = gr.Dropdown(
                    label=i18n("需要合成的语种"), choices=[i18n("中文"), i18n("英文"), i18n("日文"), i18n("中英混合"), i18n("日英混合"), i18n("多语种混合")], value=i18n("中文")
            )

            how_to_cut = gr.Radio(
                label=i18n("怎么切"),
                choices=[i18n("不切"), i18n("凑四句一切"), i18n("凑50字一切"), i18n("按。.！!?？切"), i18n("按英文句号.切"), i18n("按标点符号切"), i18n("断句切"), ],
                value=i18n("按。.！!?？切"),
                interactive=True,
            )
            with gr.Row():
                gr.Markdown(value=i18n("gpt采样参数："))
                top_k = gr.Slider(minimum=1,maximum=100,step=1,label=i18n("top_k"),value=5,interactive=True)
                top_p = gr.Slider(minimum=0,maximum=1,step=0.05,label=i18n("top_p"),value=1,interactive=True)
                temperature = gr.Slider(minimum=0,maximum=1,step=0.05,label=i18n("temperature"),value=1,interactive=True)
                interval = gr.Slider(minimum=0,maximum=5,step=0.02,label=i18n("interval"),value=0.3,interactive=True)
             

            inference_button = gr.Button(i18n("合成语音"), variant="primary")
            output = gr.Audio(label=i18n("输出的语音"))

            with gr.Row():
                # 创建文本框和下载按钮
                download_button = gr.Button("下载语音", variant="primary")
                textq = gr.Textbox(label="保存的语音路径", value="")
                outputs0 = gr.Textbox(label=i18n("保存状态"), value="", interactive=False)
                # 将事件处理函数绑定到按钮的点击事件
                download_button.click(
                    on_download_click, 
                    inputs=[textq],  # 这里确保 textq 是正确的组件引用
                    outputs=[outputs0]  # 这里确保 outputs 是正确的组件引用
                )
               

        inference_button.click(
            get_tts_wav,
            [inp_ref, prompt_text, prompt_language, text, text_language, how_to_cut, top_k, top_p, temperature, interval, ref_text_free],
            [output],
        )

        # Add new UI elements for saving and loading configurations
        with gr.Row():


            # 初始加载配置文件列表
            config_files = get_config_files()
            # 创建一个新的列表，只包含文件名
            config_file_names = [os.path.basename(path) for path in config_files]

            # 使用文件名列表作为 Dropdown 组件的选项
            config_dropdown = gr.Dropdown(
                label=i18n("加载模型配置"),
                choices=config_file_names,
                value=config_file_names[0] if config_file_names else None
            )

            # Output textbox for displaying save confirmation
            save_output = gr.Textbox(label=i18n("保存配置状态"), value="", interactive=False)

            # 绑定刷新按钮的点击事件
            refresh_button = gr.Button(i18n("刷新配置文件列表"), variant="primary")
            refresh_button.click(
                fn=refresh_config_files,  # 使用新创建的 refresh_config_files 函数
                inputs=[],  # 刷新按钮不需要输入
                outputs=[config_dropdown]  # 指定输出为 config_dropdown 组件，以更新其选项
            )

            # 绑定保存按钮的点击事件
            save_button = gr.Button(i18n("保存模型配置"), variant="primary")
            save_button.click(
                fn=save_model_config,
                inputs=[GPT_dropdown, SoVITS_dropdown, inp_ref, prompt_text, prompt_language],
                outputs=[save_output]
            )

            # 绑定加载按钮的点击事件
            load_button = gr.Button(i18n("加载模型配置"), variant="primary")
            # 绑定加载按钮的点击事件
            # 绑定加载按钮的点击事件
            # 绑定加载按钮的点击事件
            load_button.click(
                fn=load_model_config,  # 直接使用 load_model_config 函数
                inputs=[config_dropdown],  # config_dropdown 组件本身作为输入
                outputs=[GPT_dropdown, SoVITS_dropdown, inp_ref, prompt_text, prompt_language]  # 期望更新的组件列表
            )
        gr.Markdown(value=i18n("文本切分工具。太长的文本合成出来效果不一定好，所以太长建议先切。合成会根据文本的换行分开合成再拼起来。"))
        with gr.Row():
            text_inp = gr.Textbox(label=i18n("需要合成的切分前文本"), value="")
            button1 = gr.Button(i18n("凑四句一切"), variant="primary")
            button2 = gr.Button(i18n("凑50字一切"), variant="primary")
            button3 = gr.Button(i18n("按。.！!?？切"), variant="primary")
            button4 = gr.Button(i18n("按英文句号.切"), variant="primary")
            button5 = gr.Button(i18n("按标点符号切"), variant="primary")
            button6 = gr.Button(i18n("断句切"), variant="primary")
            button7 = gr.Button(i18n("推送"), variant="primary")
            text_opt = gr.Textbox(label=i18n("切分后文本"), value="")
            # 绑定按钮的点击事件，并设置 concurrency_limit
            button1.click(cut1, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511)
            button2.click(cut2, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511)
            button3.click(cut3, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511)
            button4.click(cut4, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511)
            button5.click(cut5, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511)
            button6.click(cut6, inputs=[text_inp], outputs=[text_opt], concurrency_limit=511) 
            button7.click(echo, inputs=[text_opt], outputs=[text], concurrency_limit=511)       
        gr.Markdown(value=i18n("后续将支持转音素、手工修改音素、语音合成分步执行。"))


        with gr.Row():
            text0 = gr.Textbox(label=i18n("大模型对话输入"), value="")
            talkmodel = gr.Dropdown(
                label=i18n("对话模型"), choices=[i18n("glm"), i18n("kimi"), i18n("deepseek")], value=i18n("glm")
        )
            talkmodel.change(fn=on_model_change, inputs=talkmodel, outputs=None)

            button2 = gr.Button(i18n("发送"), variant="primary")
            button3 = gr.Button(i18n("新建对话"), variant="primary")

            button1 = gr.Button(i18n("开启对话"), variant="primary")
            button4 = gr.Button(i18n("关闭对话"), variant="primary")                

            text1 = gr.Textbox(label=i18n("大模型回复"), value="")
            button1.click(startalk, outputs=[text1], concurrency_limit=511)
            button4.click(stoptalk, outputs=[text1], concurrency_limit=511)                        
            button2.click(send, inputs=[text0], outputs=[text0, text1], concurrency_limit=511) 
            button3.click(new, outputs=[text1], concurrency_limit=511)

app.launch(
    server_name="0.0.0.0",
    inbrowser=True,
    share=is_share,
    server_port=infer_ttswebui,
    quiet=True,
    max_threads=511  # 设置最大工作线程数为 511
)
