import os
import shutil
import json


from glob import glob

def update_and_copy_folders(root_dir=os.curdir):
    # 由于os.curdir是一个路径名字符串'.'，代表当前目录，
    # 我们使用os.path.abspath来获取它的绝对路径
    root_dir = os.path.abspath(root_dir)

    resources_dir = os.path.join(root_dir, 'Resources')
    folders = [f for f in os.listdir(resources_dir) if os.path.isdir(os.path.join(resources_dir, f))]

    # 遍历每个文件夹
    for folder in folders:
        folder_path = os.path.join(resources_dir, folder)
        
        # 遍历找到.model3.json结尾的文件
        json_files = glob(os.path.join(folder_path, '*.model3.json'))
        for json_file in json_files:
            # 调用update_motions_json函数，这里假设该函数已经定义
            update_motions_json(json_file)
        # 遍历找到.model3.json结尾的文件
        json_files = glob(os.path.join(folder_path, '*.model.json'))
        for json_file in json_files:
            # 调用update_motions_json函数，这里假设该函数已经定义
            update_motions_json2(json_file)            
        
        # 复制sounds和motions文件夹
        source_sounds_dir = os.path.join(root_dir, 'json', 'sounds')
        source_motions_dir = os.path.join(root_dir, 'json', 'motions')
        
        target_sounds_dir = os.path.join(folder_path, 'sounds')
        target_motions_dir = os.path.join(folder_path, 'motions')
        
        # 复制sounds文件夹
        shutil.copytree(source_sounds_dir, target_sounds_dir, dirs_exist_ok=True)
        
        # 复制motions文件夹
        shutil.copytree(source_motions_dir, target_motions_dir, dirs_exist_ok=True)

def dicts_equal(dict1, dict2):
    if len(dict1) != len(dict2):
        return False
    for key in dict1:
        if key not in dict2 or dict1[key] != dict2[key]:
            return False
    return True

def update_motions_json(json_file_path):
    try:
        # 打开并读取json文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 检查是否存在'FileReferences'键，并处理'Motions'
        if 'FileReferences' not in data:
            data['FileReferences'] = {}
        if 'Motions' not in data['FileReferences']:
            data['FileReferences']['Motions'] = {}
        # 创建新的'Motions'条目
        new_motions = [
            {
                "File": "motions/mytalk0.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,                
                "Sound": "sounds/mytalk0.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk1.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,  
                "Sound": "sounds/mytalk1.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk2.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,                 
                "Sound": "sounds/mytalk2.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk3.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,  
                "Sound": "sounds/mytalk3.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk4.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,  
                "Sound": "sounds/mytalk4.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk5.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,  
                "Sound": "sounds/mytalk5.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk6.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5,  
                "Sound": "sounds/mytalk6.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk7.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5, 
                "Sound": "sounds/mytalk7.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk8.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5, 
                "Sound": "sounds/mytalk8.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk9.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5, 
                "Sound": "sounds/mytalk9.wav",
                "Text": ""
            },
            {
                "File": "motions/mytalk10.json",
                "FadeInTime": 0.5,
                "FadeOutTime": 0.5, 
                "Sound": "sounds/mytalk10.wav",
                "Text": ""
            }
        ]
        key = 'mytalk'
        if key not in data['FileReferences']['Motions']:
            data['FileReferences']['Motions'][key] = new_motions
        elif not all(dicts_equal(m, new_motions[i]) for i, m in enumerate(data['FileReferences']['Motions'][key])):
            # 只有当data['FileReferences']['Motions'][key]中不存在与new_motions完全相同的字典时才执行扩展操作
            data['FileReferences']['Motions'][key].extend(new_motions)

        # 检查并更新'Groups'列表
        group_to_add = {
            "Target": "Parameter",
            "Name": "LipSync",
            "Ids": ["ParamMouthOpenY"]
        }
        # 检查是否存在具有相同Target和Name的group
        group_exists = False
        for group in data.get('Groups', []):
            if group['Target'] == group_to_add['Target'] and group['Name'] == group_to_add['Name']:
                                # 检查ParamMouthOpenY是否已经存在于group['Ids']中
                        if group_to_add['Ids'][0] not in group['Ids']:
                            group['Ids'].append(group_to_add['Ids'][0])  # 添加ParamMouthOpenY
                        group_exists = True
                        break 
                    
        # 如果没有找到，则添加新的group
        if not group_exists:
            data.setdefault('Groups', []).append(group_to_add)
        
        # 将更新后的数据写回文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)  # 设置ensure_ascii=False以支持中文字符输出
        
        print(f"JSON file '{json_file_path}' updated successfully.")
    
    except Exception as e:
        print(f"'{json_file_path}'：An error occurred: {e}")


def update_motions_json2(json_file_path):
    try:
        # 打开并读取json文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 检查是否存在'FileReferences'键，并处理'Motions'
        if 'motions' not in data:
            data['motions'] = {}
        # if 'Motions' not in data['FileReferences']:
        #     data['FileReferences']['Motions'] = {}
        # 创建新的'Motions'条目
        new_motions = [
            {
                "file": "motions/mytalk0.mtn",
                "sound": "sounds/mytalk0.wav",
                "msg_id": "1"
            },
            {
                "file": "motions/mytalk1.mtn",
                "sound": "sounds/mytalk1.wav",
                "msg_id": "2"
            },
            {
                "file": "motions/mytalk2.mtn",
                "sound": "sounds/mytalk2.wav",
                "msg_id": "3"
            },
            {
                "file": "motions/mytalk3.mtn",
                "sound": "sounds/mytalk3.wav",
                "msg_id": "4"
            },
            {
                "file": "motions/mytalk4.mtn",
                "sound": "sounds/mytalk4.wav",
                "msg_id": "5"
            },
            {
                "file": "motions/mytalk5.mtn",
                "sound": "sounds/mytalk5.wav",
                "msg_id": "6"
            },
            {
                "file": "motions/mytalk6.mtn",
                "sound": "sounds/mytalk6.wav",
                "msg_id": "7"
            },
            {
                "file": "motions/mytalk7.mtn",
                "sound": "sounds/mytalk7.wav",
                "msg_id": "8"
            },
            {
                "file": "motions/mytalk8.mtn",
                "sound": "sounds/mytalk8.wav",
                "msg_id": "9"
            },
            {
                "file": "motions/mytalk9.mtn",
                "sound": "sounds/mytalk9.wav",
                "msg_id": "10"
            },
            {
                "file": "motions/mytalk10.mtn",
                "sound": "sounds/mytalk10.wav",
                "msg_id": "11"
            }
        ]
        key = 'mytalk'
        if key not in data['motions']:
            data['motions'][key] = new_motions
        elif not all(dicts_equal(m, new_motions[i]) for i, m in enumerate(data['motions'][key])):
            # 只有当data['FileReferences']['Motions'][key]中不存在与new_motions完全相同的字典时才执行扩展操作
            data['motions'][key].extend(new_motions)
        
        # 将更新后的数据写回文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)  # 设置ensure_ascii=False以支持中文字符输出
        
        print(f"JSON file '{json_file_path}' updated successfully.")
    
    except Exception as e:
        print(f"'{json_file_path}'：An error occurred: {e}")        



# 使用示例
#root_directory = 'test'  # 替换为实际的根目录路径
#update_and_copy_folders(root_directory)