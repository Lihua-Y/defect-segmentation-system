import copy

import numpy as np
import torch
from PIL import Image
from medpy import metric
from scipy.ndimage import zoom
import torch.nn as nn
import torch.nn.functional as F
import SimpleITK as sitk

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.9, gamma=2):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        # Compute cross-entropy loss
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')

        # Compute the focal loss
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()

class DiceLoss(nn.Module):
    def __init__(self, n_classes):
        super(DiceLoss, self).__init__()
        self.n_classes = n_classes

    def _one_hot_encoder(self, input_tensor):
        tensor_list = []
        for i in range(self.n_classes):
            temp_prob = input_tensor == i  # * torch.ones_like(input_tensor)
            tensor_list.append(temp_prob.unsqueeze(1))
        output_tensor = torch.cat(tensor_list, dim=1)
        return output_tensor.float()

    def _dice_loss(self, score, target):
        target = target.float()
        smooth = 1e-5
        intersect = torch.sum(score * target)
        y_sum = torch.sum(target * target)
        z_sum = torch.sum(score * score)
        loss = (2 * intersect + smooth) / (z_sum + y_sum + smooth)
        loss = 1 - loss
        return loss

    def forward(self, inputs, target, weight=None, softmax=False):
        if softmax:
            inputs = torch.softmax(inputs, dim=1)
        target = self._one_hot_encoder(target)
        if weight is None:
            weight = [1] * self.n_classes
        assert inputs.size() == target.size(), 'predict {} & target {} shape do not match'.format(inputs.size(), target.size())
        class_wise_dice = []
        loss = 0.0
        for i in range(0, self.n_classes):
            dice = self._dice_loss(inputs[:, i], target[:, i])
            class_wise_dice.append(1.0 - dice.item())
            loss += dice * weight[i]
        return loss / self.n_classes


def calculate_metric_percase(pred, gt):
    pred[pred > 0] = 1
    gt[gt > 0] = 1
    if pred.sum() > 0 and gt.sum()>0:
        dice = metric.binary.dc(pred, gt)
        hd95 = metric.binary.hd95(pred, gt)
        iou=metric.binary.iou_score(pred,gt)
        pre=metric.binary.precision(pred,gt)
        recall=metric.binary.recall(pred,gt)
        mcc=metric.binary.mcc(pred,gt)

        return dice, hd95,iou,pre,recall,mcc
    elif pred.sum() > 0 and gt.sum()==0:
        return 0, 0,0,0,0,0
    else:
        return 0, 0,0,0,0,0

def test_single_volume(image, net,patch_size=[384, 384], test_save_path=None, case=None):
    image= image.squeeze(0).cpu().detach().numpy()
    _,x, y = image.shape
    if x != patch_size[0] or y != patch_size[1]:
        #缩放图像符合网络输入
        image = zoom(image, (1,patch_size[0] / x, patch_size[1] / y), order=3)
    input = torch.from_numpy(image).unsqueeze(0).float().cuda()
    net.eval()
    with torch.no_grad():
        out=net(input)
        out = torch.argmax(torch.softmax(out, dim=1), dim=1).squeeze(0)
        out = out.cpu().detach().numpy()
        if x != patch_size[0] or y != patch_size[1]:
            #缩放图像至原始大小
            prediction = zoom(out, (x / patch_size[0], y / patch_size[1]), order=0)
        else:
            prediction = out

    if test_save_path is not None:
        a1 = copy.deepcopy(prediction)
        a2 = copy.deepcopy(prediction)
        a3 = copy.deepcopy(prediction)
        # r通道
        a1[a1 == 1] = 255
        # g通道
        a2[a2 == 1] = 255
        # b通道
        a3[a3 == 1] = 255
        a1 = Image.fromarray(np.uint8(a1)).convert('L')
        a2 = Image.fromarray(np.uint8(a2)).convert('L')
        a3 = Image.fromarray(np.uint8(a3)).convert('L')
        prediction = Image.merge('RGB', [a1, a2, a3])
        prediction.save(test_save_path + '/' + case + '.png')



