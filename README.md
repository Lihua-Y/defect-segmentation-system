# Defect segmentation system based on UNet
Defect segmentation system written using pyqt5. The effect is as follows. The left side shows the original image, the upper part on the right is the segmentation result highlighted in the original image, and the lower part is the OK/NG result calculated based on the defect area. If the defect area exceeds the threshold, the image is judged to be NG. Otherwise it is OK. Zoom the mouse wheel on the left window to zoom in and out of the picture, press the A key on the keyboard to view the previous picture, and press the D key on the keyboard to view the next picture. The system code is in project.py

![image-20220213204047803](https://github.com/LihuaYang404/images/blob/main/image/image1.png)

## About the dataset/model
You can use public datasets or self-built datasets. The model part of the code is in networks/vit_seg_modeling. The training part of the code can use the official training code of TransUnet. After training, create a new folder named model in the project, and then Just place the weight file in the model folder.
 ## Requirements
Code was tested with Python 3.9. pytorch 1.12.1. cuda113. To install the required dependencies simply run pip install -r requirements.txt.

```python
numpy
tqdm
tensorboard
tensorboardX
ml-collections
medpy
SimpleITK
scipy
h5py
```
