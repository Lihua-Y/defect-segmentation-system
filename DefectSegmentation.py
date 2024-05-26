from PIL import Image, ImageDraw, ImageFont
import os
from okngleastlong import least_long_welding
from okngmaxlong import max_long_welding
from openpyxl import Workbook

def SegmentationResults(folder_A_path,folder_B_path,folder_C_path,folder_D_path,excel_path):
    # 创建excel表
    wb = Workbook()
    ws = wb.active
    ws.append(["Result", "Cause", "FileName", "ShortestSequenceW", "DMaximumLength", 'Mark'])
    file_names_B = os.listdir(folder_B_path)

    for file_name_B in file_names_B:
        file_path_B = os.path.join(folder_B_path, file_name_B)
        file_path_A = os.path.join(folder_A_path, file_name_B)

        image_A = Image.open(file_path_A)
        image_B = Image.open(file_path_B)

        image_B_gray = image_B.convert('L')
        least_long=least_long_welding(file_path_B)
        max_long=max_long_welding(file_path_B)

        if least_long / 43 >= 3:
            if max_long / 43 <= 2:
                ws.append(["OK", "", file_name_B, f'{round(least_long / 43, 3)}mm',
                           f'{round(max_long / 43, 3)}mm'])
            elif max_long / 43 > 2:
                ws.append(["NG", "最大缺陷尺寸大于2mm", file_name_B, f'{round(least_long / 43, 3)}mm',
                           f'{round(max_long / 43, 3)}mm'])
        elif least_long / 43 < 3:
            if max_long / 43 <= 2:
                ws.append(["NG", "最短长度小于3mm", file_name_B, f'{round(least_long / 43, 3)}mm',
                           f'{round(max_long / 43, 3)}mm'])
            elif max_long / 43 > 2:
                ws.append(["NG", "最短长度小于3mm，最大缺陷尺寸大于2mm", file_name_B,
                           f'{round(least_long / 43, 3)}mm',
                           f'{round(max_long / 43, 3)}mm'])

        for x in range(image_B_gray.width):
            for y in range(image_B_gray.height):
                if image_B_gray.getpixel((x, y)) == 255:
                    image_A.putpixel((x, y), (255, 0, 0))  # (R, G, B)

        save_path = os.path.join(folder_D_path, file_name_B)
        image_A.save(save_path)

        draw = ImageDraw.Draw(image_A)
        font_size1 = 15
        font_size2 = 30
        font1 = ImageFont.truetype("arial.ttf", font_size1)
        font2 = ImageFont.truetype("arial.ttf", font_size2)
        draw.text((10, 30), f'Minimum Length: {round(least_long/43,3)}mm', fill='green', font=font1)
        draw.text((10, 60), f'Defect Length: {round(max_long/43,3)}mm', fill='green', font=font1)
        # draw.text((10, 90), f'Projection rate: {round(ratio, 3)}', fill='green', font=font1)

        if least_long/43 < 3 or max_long/43>2:
            draw.text((image_A.width/2, image_A.height/2), f'NG', fill='blue', font=font2)
        else:
            draw.text((image_A.width/2, image_A.height/2), f'OK', fill='blue', font=font2)

        save_path = os.path.join(folder_C_path, file_name_B)
        image_A.save(save_path)

    wb.save(excel_path)
    print(f"Excel file generated at {excel_path}")

