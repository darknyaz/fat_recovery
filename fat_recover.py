#!/usr/bin/env python3
# coding: utf-8

# fat32.dd info
#
# Offsets:
# FAT1          4000 
# FAT2          c9000
# ROOT_DIR      18e000
# 


import struct
import copy


FAT_ENTRY_SIZE = 32
ROOT_DITECTORY_CLUSTER_NUMBER = 2
FIRST_CLUSTER_OFFSET = 0

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
    },
    'number_of_fat_copies': {
        'offset': 16,
        'size': 1,
        'value': 0
    },
    'fat_size_in_sectors': {
        'offset': 36,
        'size': 4,
        'value': 0
    }
}


DIRECROTY_ENTRY = {
    'allocation_flag': {
        'offset': 0,
        'size': 1,
        'value': 0
    },
    'filename': {
        'offset': 1,
        'size': 10,
        'value': '',
        'enc': 'ascii'
    },
    'attributes': {
        'offset': 11,
        'size': 1,
        'value': 0
    },
    'first_2_bytes_of_start_cluster_number': {
        'offset': 20,
        'size': 2,
        'value': 0
    },
    'second_2_bytes_of_start_cluster_number': {
        'offset': 26,
        'size': 2,
        'value': 0
    },
    'filesize': {
        'offset': 28,
        'size': 4,
        'value': 0
    }
}


LONG_FILENAME_DIRECTORY_ENTRY = {
    'allocation_flag': {
        'offset': 0,
        'size': 1,
        'value': 0
    },
    '1_5_letters_of_filename': {
        'offset': 1,
        'size': 10,
        'value': '',
        'enc': 'utf-16'
    },
    'attributes': {
        'offset': 11,
        'size': 1,
        'value': 0
    },
    '6_11_letters_of_filename': {
        'offset': 14,
        'size': 12,
        'value': '',
        'enc': 'utf-16'
    },
    '12_13_letters_of_filename': {
        'offset': 28,
        'size': 4,
        'value': '',
        'enc': 'utf-16'
    },
}


STRUCT_UNPACK_FORMAT_LETTERS = {
    1: 'B',
    2: 'H',
    4: 'I'
}


def read_field_from_dump(dump, field_info):
    dump.seek(field_info['offset'])
    field_raw = dump.read(field_info['size'])
    if 'enc' in field_info:
        field_info['value'] = struct.unpack(
            '{}s'.format(field_info['size']), field_raw
        )[0].decode(field_info['enc'])
    else:
        field_info['value'] = struct.unpack(
            STRUCT_UNPACK_FORMAT_LETTERS[field_info['size']], field_raw
        )[0]


def read_fields_from_dump(dump, fields_info):
    for field_info in fields_info.values():
        read_field_from_dump(dump, field_info)


def read_boot_sector(fat_dump_file):
    global FIRST_CLUSTER_OFFSET

    # read bytes_in_sector
    read_field_from_dump(fat_dump_file, FAT_BOOT_SECTOR['bytes_in_sector'])

    # read sectors_in_cluster
    read_field_from_dump(fat_dump_file, FAT_BOOT_SECTOR['sectors_in_cluster'])

    # read reserved_region_size_in_sectors
    read_field_from_dump(
        fat_dump_file, FAT_BOOT_SECTOR['reserved_region_size_in_sectors']
    )

    # read number_of_fat_copies
    read_field_from_dump(
        fat_dump_file, FAT_BOOT_SECTOR['number_of_fat_copies']
    )

    # read fat_size_in_sectors
    read_field_from_dump(
        fat_dump_file, FAT_BOOT_SECTOR['fat_size_in_sectors']
    )

    FIRST_CLUSTER_OFFSET = (
        FAT_BOOT_SECTOR['reserved_region_size_in_sectors']['value'] +
        FAT_BOOT_SECTOR['number_of_fat_copies']['value'] *
            FAT_BOOT_SECTOR['fat_size_in_sectors']['value']
    ) * FAT_BOOT_SECTOR['bytes_in_sector']['value']


def get_cluster_offset(cluster_number):
    return FIRST_CLUSTER_OFFSET + (
        cluster_number - ROOT_DITECTORY_CLUSTER_NUMBER
    ) * FAT_BOOT_SECTOR['sectors_in_cluster']['value'] * \
        FAT_BOOT_SECTOR['bytes_in_sector']['value']


def read_cluster_fat_entry(dump, cluster_number):
    fat_entry = {
        'offset': FAT_BOOT_SECTOR['reserved_region_size_in_sectors']['value'] +
                  cluster_number * FAT_ENTRY_SIZE,
        'size': FAT_ENTRY_SIZE // 8,
        'value': 0
    }

    read_field_from_dump(dump, fat_entry)

    return fat_entry['value']


def is_end_cluster(dump, cluster_number):
    return read_cluster_fat_entry(dump, cluster_number) > 0x0ffffff8


def get_next_cluster_number(dump, cluster_number):
    return read_cluster_fat_entry(dump, cluster_number)


def get_shifted_copy_of_fields_info(fields_info, shift):
    result = copy.deepcopy(fields_info)

    for field_info in result.values():
        field_info['offset'] += shift
        
    return result


def read_directory(dump, first_cluster_number):
    cluster_number = first_cluster_number
    cluster_size_in_bytes = FAT_BOOT_SECTOR['bytes_in_sector']['value'] * \
        FAT_BOOT_SECTOR['sectors_in_cluster']['value']

    result = []

    while True:
        # cycle by clusters

        # get cluster offset
        cluster_offset = get_cluster_offset(cluster_number)

        dir_entry_offset = 0
        lfn_entries = []
        
        while dir_entry_offset < cluster_size_in_bytes:
            # cycle by directory entries

            attribute = {
                'offset': cluster_offset + dir_entry_offset + 11,
                'size': 1,
                'value': 0
            }
            read_field_from_dump(dump, attribute)

            if attribute['value'] == 0x0f:
                lfn_entry = get_shifted_copy_of_fields_info(
                    LONG_FILENAME_DIRECTORY_ENTRY,
                    cluster_offset + dir_entry_offset
                )
                read_fields_from_dump(dump, lfn_entry)

                lfn_entries.append(lfn_entry)
            else:
                file_entry = get_shifted_copy_of_fields_info(
                    DIRECROTY_ENTRY,
                    cluster_offset + dir_entry_offset
                )
                read_fields_from_dump(dump, file_entry)

                result.append(lfn_entries + [file_entry])

                lfn_entries = []

            dir_entry_offset += 32


        if is_end_cluster(dump, cluster_number):
            break

        cluster_number = get_next_cluster_number(dump, cluster_number)

    return result


if __name__ == "__main__":
    fat_dump_file = open('fat32.dd', 'rb')

    read_boot_sector(fat_dump_file)
    # DEBUG
    #print(FAT_BOOT_SECTOR)
    print(read_directory(fat_dump_file, 2))

    fat_dump_file.close()
