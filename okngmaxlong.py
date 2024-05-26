from PIL import Image

def max_long_welding(input_path):
    zero_lengths = []

    img = Image.open(input_path).convert('L')
    width, height = img.size
    for col in range(width):
        zero_length = 0
        max_zero_length = 0
        for row in range(height):
            if img.getpixel((col, row)) == 255:
                zero_length += 1
            else:
                if zero_length > 0:
                    max_zero_length = max(max_zero_length, zero_length)
                    zero_length = 0
        if zero_length > 0:
            max_zero_length = max(max_zero_length, zero_length)
        zero_lengths.append(max_zero_length)

    max_zero_length = max(zero_lengths)

    return max_zero_length
