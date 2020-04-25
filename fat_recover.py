#!/usr/bin/env python3
# coding: utf-8


import struct


BYTES_IN_SECTOR_OFFSET = 11
BYTES_IN_SECTOR_SIZE = 2

SECTORS_IN_CLUSTER_OFFSET = 13
SECTORS_IN_CLUSTER_SIZE = 1

RESERVED_REGION_SIZE_IN_SECTORS_OFFSET = 14
RESERVED_REGION_SIZE_IN_SECTORS_SIZE = 2


FAT_BOOT_SECTOR = {
    'bytes_in_sector': {
        'offset': 11,
        'size': 2,
        'value': 0
    },
    'sectors_in_cluster': {
        'offset': 13,
        'size': 1,
        'value': 0
    },
    'reserved_region_size_in_sectors': {
        'offset': 14,
        'size': 2,
        'value': 0
    }
}


STRUCT_UNPACK_FORMAT_LETTERS = {
    1: 'B',
    2: 'H'
}


def read_field_from_dump(dump, field_info):
    dump.seek(field_info['offset'])
    field_raw = dump.read(field_info['size'])
    field_info['value'] = struct.unpack(
        STRUCT_UNPACK_FORMAT_LETTERS[field_info['size']], field_raw
    )[0]


def read_boot_sector(fat_dump_file):
    # read bytes_in_sector
    read_field_from_dump(fat_dump_file, FAT_BOOT_SECTOR['bytes_in_sector'])

    # read sectors_in_cluster
    read_field_from_dump(fat_dump_file, FAT_BOOT_SECTOR['sectors_in_cluster'])

    # read reserved_region_size_in_sectors
    read_field_from_dump(
        fat_dump_file, FAT_BOOT_SECTOR['reserved_region_size_in_sectors']
    )


if __name__ == "__main__":
    fat_dump_file = open('fat32.dd', 'rb')

    read_boot_sector(fat_dump_file)
    # DEBUG
    print(FAT_BOOT_SECTOR)


    fat_dump_file.close()
