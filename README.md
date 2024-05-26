# Defect segmentation system based on UNet
Defect segmentation system written using pyqt5. The effect is as follows. The left side shows the original image, the upper part on the right is the segmentation result highlighted in the original image, and the lower part is the OK/NG result calculated based on the defect area. If the defect area exceeds the threshold, the image is judged to be NG. Otherwise it is OK. Zoom the mouse wheel on the left window to zoom in and out of the picture, press the A key on the keyboard to view the previous picture, and press the D key on the keyboard to view the next picture. The system code is in project.py

![image-20220213204047803](https://github.com/LihuaYang404/images/blob/main/image/image1.png)

## About the dataset/model
You can use public datasets or self-built datasets. The model part of the code is in networks/vit_seg_modeling. The training part of the code can use the official training code of TransUnet. After training, create a new folder named model in the project, and then Just place the weight file in the model folder.
 ## Requirements
Code was tested with Python 3.9. To install the required dependencies simply run pip install -r requirements.txt.

```python
tensorboard==2.16.2
tensorboardX==2.6.2.2
MedPy==0.5.1
ml_collections==0.1.1
h5py==3.11.0
numpy==1.25.2
opencv-python==4.9.0.80
pandas==2.0.3
PyQt5==5.15.10
scipy==1.13.0
torch==1.12.1
torchaudio==0.12.1
torchvision==0.13.1
tqdm==4.66.4
```
