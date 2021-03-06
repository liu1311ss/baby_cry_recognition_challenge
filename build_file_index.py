"""
建立训练文件的索引，并将其存储到字典indexes中
格式为： (file_path, file_label)
"""
import os

filePath = "/home/doubibobo/桌面/婴儿啼哭识别 挑战赛/data/original-data/"


def get_filename(selection):
    """
    获取音频文件
    :param selection: 选择使用哪个文件夹，可选择test和train两个
    :return: 字典列表
    """
    label_directory = os.listdir(filePath + selection)
    dictionary = {}
    for i in range(len(label_directory)):
        son_file_path = filePath + selection + "/" + label_directory[i]
        if selection == "train":
            dictionary[label_directory[i]] = os.listdir(son_file_path)
        elif selection == "test":
            dictionary[son_file_path] = "awake"
    if selection == "test":
        return dictionary

    # 遍历字典列表，字典的key为：文件名称，value为标签
    indexes = {}
    for key, value in dictionary.items():
        for file_name in range(len(value)):
            indexes[value[file_name]] = key

    del dictionary
    return indexes
