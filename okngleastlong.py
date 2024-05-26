from PIL import Image

def least_long_welding(input_path):
    zero_lengths = []

    img = Image.open(input_path).convert('L')
    width, height = img.size
    for col in range(width):
        zero_length = 0
        min_zero_length = 0
        for row in range(height):
            if img.getpixel((col, row)) == 0:
                zero_length += 1
            elif zero_length > 0:
                min_zero_length = max(min_zero_length, zero_length)
                zero_length = 0
        if zero_length > 0:
            min_zero_length = max(min_zero_length, zero_length)
        zero_lengths.append(min_zero_length)

    min_zero_length = min(zero_lengths)

    return min_zero_length
