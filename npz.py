import glob
import cv2
import numpy as np
import os
import re

def sorted_nicely(l):
    """ Human sorting function """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def npz(input_folder, output_folder):
    # 获取所有jpg文件，并按照人类排序方式排序
    img_paths = sorted_nicely(glob.glob(os.path.join(input_folder, '*.png')))

    for img_path in img_paths:
        # 读入图像
        image = cv2.imread(img_path)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        file_name = os.path.basename(img_path)
        file_name = os.path.splitext(file_name)[0]

        # 创建包含图像数据的字典
        data_dict = {'image': image}

        # 保存npz
        np.savez(os.path.join(output_folder, file_name), **data_dict)
        print('------------', file_name)

    print('------------------npz Data conversion completed---------------')
#
# if __name__ == '__main__':
#     input_folder = r'D:\XiangMu_models\project_1\ceshi4-29'
#     output_folder = r'D:\XiangMu_models\project_1\data\Synapse\test_vol_h5'
#     npz(input_folder, output_folder)
