
import time
import io, os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('{}/third_party/AcademiCodec'.format(ROOT_DIR))
sys.path.append('{}/third_party/Matcha-TTS'.format(ROOT_DIR))

import numpy as np
from flask import Flask, request, Response
import torch
import torchaudio

from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
import torchaudio
import ffmpeg

from flask_cors import CORS

import json

cosyvoice = CosyVoice('./pretrained_models/CosyVoice-300M')

spk_new = []

for name in os.listdir("./voices/"):
    print(name.replace(".py",""))
    spk_new.append(name.replace(".py",""))

print("默认音色",cosyvoice.list_avaliable_spks())
print("自定义音色",spk_new)

app = Flask(__name__)

CORS(app, cors_allowed_origins="*")

CORS(app, supports_credentials=True)


def speed_change(input_audio: np.ndarray, speed: float, sr: int):
    # 检查输入数据类型和声道数
    if input_audio.dtype != np.int16:
        raise ValueError("输入音频数据类型必须为 np.int16")


    # 转换为字节流
    raw_audio = input_audio.astype(np.int16).tobytes()

    # 设置 ffmpeg 输入流
    input_stream = ffmpeg.input('pipe:', format='s16le', acodec='pcm_s16le', ar=str(sr), ac=1)

    # 变速处理
    output_stream = input_stream.filter('atempo', speed)

    # 输出流到管道
    out, _ = (
        output_stream.output('pipe:', format='s16le', acodec='pcm_s16le')
        .run(input=raw_audio, capture_stdout=True, capture_stderr=True)
    )

    # 将管道输出解码为 NumPy 数组
    processed_audio = np.frombuffer(out, np.int16)

    return processed_audio
@app.route("/noaudio/", methods=['POST'])
def sft_post1():
    question_data = request.get_json()

    text = question_data.get('text')
    speaker = question_data.get('speaker')
    new = question_data.get('new', False)  # 使用布尔值而不是整数

    speed = request.args.get('speed', 1.0)
    speed = float(speed)
    path = question_data.get('path')  # 确保请求体中包含 path 字段

    if not text:
        return {"error": "文本不能为空"}, 400

    if not speaker:
        return {"error": "角色名不能为空"}, 400

    if not path:
        return {"error": "路径不能为空"}, 400

    start = time.process_time()
    try:
        if not new:
            output = cosyvoice.inference_sft(text, speaker, "无")
        else:
            output = cosyvoice.inference_sft(text, speaker, speaker)
    except Exception as e:
        return {"error": f"推理过程中发生错误: {e}"}, 500

    end = time.process_time()
    print("推理时间:", end - start)

    if speed != 1.0:
        try:
            numpy_array = output['tts_speech'].numpy()
            audio = (numpy_array * 32768).astype(np.int16)
            audio_data = speed_change(audio, speed=speed, sr=22050)
            audio_data = torch.from_numpy(audio_data)
            audio_data = audio_data.reshape(1, -1)
        except Exception as e:
            return {"error": f"改变音频速度时发生错误: {e}"}, 500
    else:
        audio_data = output['tts_speech']

    try:
        # 保存音频到指定路径
        torchaudio.save(path, audio_data, 22050, format="wav")
        return {"message": "音频已保存到指定路径"}, 200
    except Exception as e:
        return {"error": f"保存音频时发生错误: {e}"}, 500

@app.route("/", methods=['POST'])
def sft_post():
    question_data = request.get_json()

    text = question_data.get('text')
    speaker = question_data.get('speaker')
    new = question_data.get('new',0)

    speed = request.args.get('speed',1.0)
    speed = float(speed)
    

    if not text:
        return {"error": "文本不能为空"}, 400

    if not speaker:
        return {"error": "角色名不能为空"}, 400

    start = time.process_time()
    if not new:
        output = cosyvoice.inference_sft(text,speaker,"无")
    else:
        output = cosyvoice.inference_sft(text,speaker,speaker)
    end = time.process_time()
    print("infer time:", end - start)
    buffer = io.BytesIO()
    if speed != 1.0:
        try:
            numpy_array = output['tts_speech'].numpy()
            audio = (numpy_array * 32768).astype(np.int16) 
            audio_data = speed_change(audio, speed=speed, sr=int(22050))
            audio_data = torch.from_numpy(audio_data)
            audio_data = audio_data.reshape(1, -1)
        except Exception as e:
            print(f"Failed to change speed of audio: \n{e}")
    else:
        audio_data = output['tts_speech']

    torchaudio.save(buffer,audio_data, 22050, format="wav")
    buffer.seek(0)
    return Response(buffer.read(), mimetype="audio/wav")


@app.route("/", methods=['GET'])
def sft_get():

    text = request.args.get('text')
    speaker = request.args.get('speaker')
    new = request.args.get('new',0)
    speed = request.args.get('speed',1.0)
    speed = float(speed)

    if not text:
        return {"error": "文本不能为空"}, 400

    if not speaker:
        return {"error": "角色名不能为空"}, 400

    start = time.process_time()
    if not new:
        output = cosyvoice.inference_sft(text,speaker,"无")
    else:
        output = cosyvoice.inference_sft(text,speaker,speaker)
    end = time.process_time()
    print("infer time:", end - start)
    buffer = io.BytesIO()

    if speed != 1.0:
        try:
            numpy_array = output['tts_speech'].numpy()
            audio = (numpy_array * 32768).astype(np.int16) 
            audio_data = speed_change(audio, speed=speed, sr=int(22050))
            audio_data = torch.from_numpy(audio_data)
            audio_data = audio_data.reshape(1, -1)
        except Exception as e:
            print(f"Failed to change speed of audio: \n{e}")
    else:
        audio_data = output['tts_speech']

    torchaudio.save(buffer,audio_data, 22050, format="wav")
    buffer.seek(0)
    return Response(buffer.read(), mimetype="audio/wav")




@app.route("/tts_to_audio/", methods=['POST'])
def tts_to_audio():

    import speaker_config
    
    question_data = request.get_json()

    text = question_data.get('text')
    speaker = speaker_config.speaker
    new = speaker_config.new

    speed = speaker_config.speed
    

    if not text:
        return {"error": "文本不能为空"}, 400

    if not speaker:
        return {"error": "角色名不能为空"}, 400

    start = time.process_time()
    if not new:
        output = cosyvoice.inference_sft(text,speaker,"无")
    else:
        output = cosyvoice.inference_sft(text,speaker,speaker)
    end = time.process_time()
    print("infer time:", end - start)
    buffer = io.BytesIO()
    if speed != 1.0:
        try:
            numpy_array = output['tts_speech'].numpy()
            audio = (numpy_array * 32768).astype(np.int16) 
            audio_data = speed_change(audio, speed=speed, sr=int(22050))
            audio_data = torch.from_numpy(audio_data)
            audio_data = audio_data.reshape(1, -1)
        except Exception as e:
            print(f"Failed to change speed of audio: \n{e}")
    else:
        audio_data = output['tts_speech']

    torchaudio.save(buffer,audio_data, 22050, format="wav")
    buffer.seek(0)
    return Response(buffer.read(), mimetype="audio/wav")



@app.route("/speakers", methods=['GET'])
def speakers():

    response = app.response_class(
        response=json.dumps([{"name":"default","vid":1}]),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/speakers_list", methods=['GET'])
def speakers_list():
    # 获取实际的扬声器列表
    available_spks = cosyvoice.list_avaliable_spks()
    
    # 将列表转换为 JSON 格式的字符串
    response_data = json.dumps(available_spks)
    
    # 创建并返回 Response 对象
    response = Response(response=response_data, status=200, mimetype='application/json')
    return response
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9880)
