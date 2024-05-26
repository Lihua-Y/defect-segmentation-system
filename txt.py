import glob
import os

def write_name(input_folder, output_folder):
    npz_files = glob.glob(os.path.join(input_folder, '*.npz'))
    txt_file_path = os.path.join(output_folder, 'test_vol_h5.txt')

    with open(txt_file_path, 'w') as f:
        for npz_file in npz_files:
            file_name = os.path.basename(npz_file)
            file_name = os.path.splitext(file_name)[0] + '\n'
            f.write(file_name)
