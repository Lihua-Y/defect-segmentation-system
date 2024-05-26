# 基于UNet的缺陷分割系统
使用pyqt5写的缺陷分割系统。效果如下，左侧展示是原始图片，在左侧窗口缩放鼠标滚轮可放大缩小图片，右侧上半部分是分割结果在原图中高亮显示，下半部分是根据缺陷面积计算出的OK/NG结果，若缺陷面积超过阈值，则判定图片为NG,反之为OK。系统的代码在project.py

![image-20220213204047803](https://github.com/LihuaYang404/images/blob/main/image/image1.png)

## 关于数据集/模型
可以使用公开的数据集，也可以使用自建数据集，模型部分代码在networks/vit_seg_modeling,训练部分代码可以使用TransUnet官方的训练代码，训练完之后将权重文件放在model文件夹下即可。
