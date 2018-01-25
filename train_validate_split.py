"""
split downloaded mapillary photos into train and validation folders
"""
import os
import shutil
import random


def train_validation_split(download_folder, data_folder):
    # create TRAIN_DIR and VALIDATION_DIR
    create_dir(data_folder)
    create_dir(os.path.join(data_folder, 'TRAIN_DIR'))
    create_dir(os.path.join(data_folder, 'VALIDATION_DIR'))

    for folder in os.listdir(download_folder):
        print('Split folder {}...'.format(folder), end='')

        # create polygon folder in train and validation
        train_folder = os.path.join(data_folder, 'TRAIN_DIR', folder)
        val_folder = os.path.join(data_folder, 'VALIDATION_DIR', folder)

        # select and copy validation dataset
        cur_folder = os.path.join(download_folder, folder)
        cur_photos = os.listdir(cur_folder)
        if len(cur_photos) == 0:  # if it's an empty folder, skip
            print('Empty folder, pass')
            continue

        create_dir(val_folder)
        val_counts = int(len(cur_photos) * 0.2)  # select 20% for validation
        for val_photo in random.sample(cur_photos, k=val_counts):
            src = os.path.join(cur_folder, val_photo)  # .jpg
            dest = os.path.join(val_folder)  # val_folder
            shutil.move(src, dest)  # move validation photos

        # move the rest of the files into train folder
        shutil.copytree(cur_folder, train_folder)
        shutil.rmtree(cur_folder)
        print('Done')

    print('')
    # create labels.txt file
    print('create label file...', end='')
    label_file = os.path.join(data_folder, 'labels.txt')
    with open(label_file, 'w') as outfile:
        for folder in os.listdir(os.path.join(data_folder, 'TRAIN_DIR')):
            outfile.write('{}:{}\n'.format(folder, folder))
    print('Done')


def create_dir(base_path):
    if not os.path.exists(base_path):
        os.mkdir(base_path)


if __name__ == '__main__':
    train_validation_split('mapillary', 'mapillary_data')
