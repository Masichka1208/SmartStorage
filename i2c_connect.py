#!/usr/bin/env python
# coding: utf8

from smbus2 import SMBus


leds_order = [7, 6, 5, 4, 0, 1, 2, 3]

def pre_select(cell_id):
    with SMBus(2) as bus:
        data = [247, 255, 0]
        bus.write_i2c_block_data(8, leds_order[cell_id-1], data)
    print(f"led: {cell_id-1}, rgb color: [247, 255, 0]")


def select(cell_id):
    with SMBus(2) as bus:
        data = [0, 255, 0]
        bus.write_i2c_block_data(8, leds_order[cell_id-1], data)
    print(f"led: {cell_id-1}, rgb color: [0, 255, 0]")


def search_res(cell_id):
    with SMBus(2) as bus:
        data = [188, 0, 255]
        bus.write_i2c_block_data(8, leds_order[cell_id-1], data)
    print(f"led: {cell_id - 1}, rgb color: [188, 0, 255]")


def turn_off():
    with SMBus(2) as bus:
        for i in range(8):
            data = [0, 0, 0]
            bus.write_i2c_block_data(8, i, data)
    print("All leds turned off")