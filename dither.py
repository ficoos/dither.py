#!/usr/bin/env python3
import sys

from PIL import Image

DITHER_TABLE = (64, 128, 192, 0)


def clamp(val, min_val, max_val):
    return min(max(min_val, val), max_val)


def open_image(path):
    img = Image.open(path)
    img = img.convert('L')
    return img


def ordered_dither(img):
    pixels = list(img.getdata())
    height = img.height
    width = img.width

    i = 0
    for line in range(height):
        for column in range(width):
            dt_idx = (line % 2) * 2 + (column % 2)
            if pixels[i] > DITHER_TABLE[dt_idx]:
                pixels[i] = 255
            else:
                pixels[i] = 0
            i += 1
    res = Image.new('L', (width, height))
    res.putdata(pixels)
    return res


def floyd_steinberg_dither(img):
    pixels = list(img.getdata())
    height = img.height
    width = img.width

    def mod_pixel(x, y, delta):
        i = y * width + x
        pixels[i] = clamp(pixels[i] + delta, 0, 255)

    i = 0
    for row in range(height):
        for column in range(width):
            if pixels[i] > 128:
                err = -255 + pixels[i]
                pixels[i] = 255
            else:
                err = pixels[i]
                pixels[i] = 0

            err_u = err // 16
            if column < (width - 1):
                mod_pixel(column + 1, row, err_u * 7)
                if row < (height - 1):
                    mod_pixel(column + 1, row + 1, err_u)
            if row < (height - 1):
                mod_pixel(column, row + 1, err_u * 5)
                if column > 0:
                    mod_pixel(column - 1, row + 1, err_u * 3)
            i += 1

    res = Image.new('L', (width, height))
    res.putdata(pixels)
    return res


def dither(img, method='ordered'):
    if method == 'ordered':
        return ordered_dither(img)

    return floyd_steinberg_dither(img)


dither(open_image(sys.argv[1]), method='floy_steinberg').show()
dither(open_image(sys.argv[1]), method='ordered').show()
