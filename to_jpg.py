"""
Convert the lmdb files to jpg
"""
from __future__ import print_function
import argparse
import cv2
import lmdb
import numpy
import os
from os.path import exists, join

CATEGORIES = ["bedroom",
              "classroom",
              "kitchen",
              "tower",
              "bridge",
              "conference_room",
              "living_room",
              "church_outdoor",
              "dining_room",
              "restaurant"]

PATH_PATTERN = "{}_train_lmdb"


def view(db_path):
    print('Viewing', db_path)
    print('Press ESC to exist or SPACE to advance.')
    window_name = 'LSUN'
    cv2.namedWindow(window_name)
    env = lmdb.open(db_path, map_size=1099511627776,
                    max_readers=100, readonly=True)
    with env.begin(write=False) as txn:
        cursor = txn.cursor()
        for key, val in cursor:
            print('Current key:', key)
            img = cv2.imdecode(
                numpy.fromstring(val, dtype=numpy.uint8), 1)
            cv2.imshow(window_name, img)
            c = cv2.waitKey()
            if c == 27:
                break


def export_images(db_root_path, out_root_dir, flat=False, limit=-1, to_jpg=True):
    for category in CATEGORIES:
        db_path = join(db_root_path, PATH_PATTERN.format(category))
        print('Exporting', db_path, 'to', out_root_dir)
        env = lmdb.open(db_path, map_size=1099511627776,
                        max_readers=100, readonly=True)
        count = 0
        with env.begin(write=False) as txn:
            cursor = txn.cursor()
            for key, val in cursor:
                if not flat:
                    image_out_dir = join(out_root_dir, category)
                else:
                    image_out_dir = out_root_dir
                if not exists(image_out_dir):
                    os.makedirs(image_out_dir)
                image_out_path = join(image_out_dir, str(key.decode()) + '.webp')
                with open(image_out_path, 'wb') as fp:
                    fp.write(val)
                if to_jpg:
                    img = cv2.imread(image_out_path)
                    cv2.imwrite(join(image_out_dir, str(key.decode())+'.jpg'), img)
                    os.remove(image_out_path)
                count += 1
                if count == limit:
                    break
                if count % 1000 == 0:
                    print('Finished', count, 'images')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='?', type=str,
                        choices=['view', 'export'],
                        help='view: view the images in the lmdb database '
                             'interactively.\n'
                             'export: Export the images in the lmdb databases '
                             'to a folder. The images are grouped in subfolders'
                             ' determinted by the prefiex of image key.')
    parser.add_argument('lmdb_path', nargs='+', type=str,
                        help='The path to the lmdb database folder. '
                             'Support multiple database paths.')
    parser.add_argument('--out_dir', type=str, default='')
    parser.add_argument('--flat', action='store_true',
                        help='If enabled, the images are imported into output '
                             'directory directly instead of hierarchical '
                             'directories.')
    args = parser.parse_args()

    command = args.command
    lmdb_paths = args.lmdb_path

    for lmdb_path in lmdb_paths:
        if command == 'view':
            view(lmdb_path)
        elif command == 'export':
            export_images(lmdb_path, args.out_dir, args.flat)


if __name__ == '__main__':
    main()
