import os
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile


def txtra(text_to_translate, TXSecretId, TXSecretKey, TXS, TXT):
    # 替换为您的SecretId和SecretKey
    SecretId = TXSecretId
    SecretKey = TXSecretKey

    # 腾讯云翻译服务的endpoint
    endpoint = "tmt.tencentcloudapi.com"

    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
    cred = credential.Credential(SecretId, SecretKey)

    # 实例化要请求产品(以翻译服务为例)的client对象
    httpProfile = HttpProfile()
    httpProfile.endpoint = endpoint

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile

    # 实例化要请求接口的client对象
    client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

    # 实例化一个请求对象，每个接口都会对应一个request类
    req = models.TextTranslateRequest()
    req.SourceText = text_to_translate  # 待翻译的文本
    req.Source = TXS  # 源语言
    req.Target = TXT  # 目标语言
    req.ProjectId = 0  # 添加ProjectId参数

    try:
        # 发起请求
        resp = client.TextTranslate(req)

        # 检查是否是正常响应并且包含TargetText属性
        if hasattr(resp, 'TargetText'):
            # 返回翻译结果
            return resp.TargetText
        else:
            return "翻译结果中没有包含 'TargetText' 字段。"

    except TencentCloudSDKException as err:
        # 返回异常信息
        return f"发生异常：{err}"

# 使用示例
#translated_text = txtra("私はロボットで、夏生さんが海から引き上げてくれたの。主人の残した命令を果たすために、失った記憶を探しています。")
#print(translated_text)