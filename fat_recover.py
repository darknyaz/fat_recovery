#!/usr/bin/env python3
# coding: utf-8


import struct


BYTES_IN_SECTOR_OFFSET = 11
BYTES_IN_SECTOR_SIZE = 2

SECTORS_IN_CLUSTER_OFFSET = 13
SECTORS_IN_CLUSTER_SIZE = 1

FAT_BOOT_SECTOR = {
    'bytes_in_sector': 0,
    'sectors_in_cluster': 0
}


def read_boot_sector(fat_dump_file):
    # read bytes_in_sector
    fat_dump_file.seek(BYTES_IN_SECTOR_OFFSET)
    bytes_in_sector_raw = fat_dump_file.read(BYTES_IN_SECTOR_SIZE)
    FAT_BOOT_SECTOR['bytes_in_sector'] = struct.unpack(
        'H', bytes_in_sector_raw
    )[0]

    # read sectors_in_cluster
    fat_dump_file.seek(SECTORS_IN_CLUSTER_OFFSET)
    sectors_in_cluster_raw = fat_dump_file.read(SECTORS_IN_CLUSTER_SIZE)
    FAT_BOOT_SECTOR['sectors_in_cluster'] = struct.unpack(
        'B', sectors_in_cluster_raw
    )[0]


if __name__ == "__main__":
    fat_dump_file = open('fat32.dd', 'rb')

    read_boot_sector(fat_dump_file)
    # DEBUG
    print(FAT_BOOT_SECTOR)


    fat_dump_file.close()