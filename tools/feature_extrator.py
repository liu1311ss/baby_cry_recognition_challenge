import librosa
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import pandas as pd

import data.code.tools.build_file_index as bf

"建立训练时的标签和语音类别的映射关系"
classes_labels = ["awake", "diaper", "hug", "hungry", "sleepy", "uncomfortable"]

types = 'awake diaper hug hungry sleepy uncomfortable'.split()


def extract_spectrogram(indexes, selection):
    """
    Extracting the Spectrogram for every video
    提取每条音频的频谱特征图
    :param indexes: 文件索引
    :param selection: 选择train文件或者test文件
    :return: 无返回值，生成频谱图之后直接存储到文件中
    """
    c_map = plt.get_cmap('inferno')
    plt.figure(figsize=(10, 10))
    # 创建对应类的频谱图文件夹
    for label in types:
        if not os.path.exists(selection + '/image_data/'):
            os.makedirs(selection + '/image_data/')
        if (selection == "train") and (not os.path.exists(selection + '/image_data/' + label)):
            os.makedirs(selection + '/image_data/' + label)
            print("the dir of" + selection + "/image_data/" + label + "is created!")
        else:
            print("the dir is exists!")

    for key, value in indexes.items():
        # 加载15s的音频，转换为单声道（mono）
        wav, sample_rate = librosa.load(((bf.filePath + selection + "/" + value + "/" + key) if selection == "train"
                                         else key), mono=True, duration=15)
        plt.specgram(wav, NFFT=2048, Fs=2, Fc=0, noverlap=128, cmap=c_map,
                     sides='default', mode='default', scale='dB')
        plt.axis("off")
        if selection == "train":
            plt.savefig(selection + '/image_data/' + value + "/" + key[: -3].replace(".", "") + ".png")
        elif selection == "test":
            plt.savefig(selection + '/image_data/' + os.path.split(key[:-3])[1] + "png")
        plt.clf()


def framing(signal, sample_rate, frame_window, shift_window, signal_window):
    """
    进行语音的分帧操作
    :param signal: 原始语音信号
    :param sample_rate: 采样率
    :param frame_window: 帧窗口，单位为ms
    :param shift_window: 步长窗口，单位为ms
    :param signal_window: 语音窗口，单位为ms
    :return: 经过分帧处理以后的数据帧
    """
    # 每一帧包含的样本数目，以及每隔多少个样本到下一帧
    frame_length, step_length = int(round(frame_window * sample_rate)), int(round(shift_window * sample_rate))
    # 整段语音中包含的样本数目
    signal_length = int(round(signal_window * sample_rate))
    # 计算一段语音中包含的帧数
    frame_numbers = int(np.ceil(float(np.abs(signal_length - frame_length)) / step_length))
    # 对不足signal_window长度的语音数据进行填充
    if len(signal) < signal_length:
        signal = np.append(signal, np.zeros(signal_length - len(signal)))
    # 对不足一帧的语音进行填充
    padding_signal_length = np.append(signal, np.zeros((frame_numbers * step_length + frame_length - signal_length)))
    # 计算每一个数据帧的索引
    indexes = np.tile(np.arange(0, frame_length), (frame_numbers, 1)) + np.tile(
        np.arange(0, frame_numbers * step_length, step_length), (frame_length, 1)).T
    return padding_signal_length[indexes.astype(np.int32, copy=False)]


def extract_features(to_frame=False):
    """
    Extracting features form Spectrogram
    We will extract
        MFCC (20 in number)
        Spectral Centroid (光谱质心)
        Zero Crossing Rate (过零率)
        Chroma Frequencies (色度频率)
        Spectral Roll-off (光谱衰减)
    :param to_frame: 是否进行分帧
    :return: csv文件头
    """
    header = 'filename chroma_stft rms spectral_centroid spectral_bandwidth rolloff zero_crossing_rate'
    for i in range(1, 21):
        header += f' mfcc{i}'
    header += ' label'
    if to_frame:
        header += ' frame_number'
    return header.split()


def write_data_to_csv_file(header, indexes, filename, selection, to_frame=False):
    """
    将特征数据写入csv文件夹
    :param header: csv头部
    :param indexes: 文件的索引
    :param filename: csv文件名称
    :param selection: train或者test选择
    :param to_frame: 是否选择分帧
    :return: 无返回值
    """
    file = open(filename, 'w', newline='')
    with file:
        writer = csv.writer(file)
        writer.writerow(header)
        file.close()
        for key, value in indexes.items():
            wav, sample_rate = librosa.load(bf.filePath + selection + "/" + (value if selection == "train" else "") +
                                            "/" + (key if selection == "train" else os.path.split(key)[1]),
                                            mono=True, duration=15)
            if to_frame:
                frames = framing(wav, sample_rate, 0.02, 0.01, 15)
            else:
                frames = [wav]
            for i in range(len(frames)):
                chroma_stft = librosa.feature.chroma_stft(y=frames[i], sr=sample_rate)
                rms = librosa.feature.rms(y=frames[i])
                spec_cent = librosa.feature.spectral_centroid(y=frames[i], sr=sample_rate)
                spec_bw = librosa.feature.spectral_bandwidth(y=frames[i], sr=sample_rate)
                rolloff = librosa.feature.spectral_rolloff(y=frames[i], sr=sample_rate)
                zcr = librosa.feature.zero_crossing_rate(y=frames[i])
                mfcc = librosa.feature.mfcc(y=frames[i], sr=sample_rate)
                to_append = f'{(key if selection == "train" else os.path.split(key)[1])} {np.mean(chroma_stft)} ' \
                            f'{np.mean(rms)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)} '
                for e in mfcc:
                    to_append += f' {np.mean(e)}'
                to_append += f' {value}'
                if to_frame:
                    to_append += f' {i}'
                file = open(filename, 'a', newline='')
                with file:
                    writer = csv.writer(file)
                    writer.writerow(to_append.split())
                    file.close()


def write_result_to_csv(data_file, filename, results):
    """
    输出测试集合的结果到csv
    :param filename: 文件名称
    :param data_file: 测试集
    :param results: 识别结果
    :return:
    """
    file = open(filename, 'w', newline='')
    with file:
        writer = csv.writer(file)
        writer.writerow('id label'.split())
        file.close()
        data = pd.read_csv(data_file)
        wav_paths = data.iloc[:, [0]].T
        wav_paths = np.matrix.tolist(wav_paths)[0]

        print(wav_paths)

        dictionary = {}
        print(len(results))
        print(results)
        for i in range(len(results)):
            dictionary[wav_paths[i]] = results[i]
            # to_append = f'{wav_paths[i]} {classes_labels[results[i].data.numpy()]} '
            to_append = f'{wav_paths[i]} {classes_labels[results[i]]} '
            file = open(filename, 'a', newline='')
            with file:
                writer = csv.writer(file)
                writer.writerow(to_append.split())
                file.close()