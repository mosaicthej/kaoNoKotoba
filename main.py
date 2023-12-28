#!/usr/local/anaconda3/bin/python
# receive an image, render the image using string of the choice.


# 该项目的创作构思由本人和 [@chenrcy](https://github.com/Chenrcy) 协力完成，
# 授权给合作者 [@chenrcy](https://github.com/Chenrcy) 作为其python课程期末作业论文材料使用
# 信息：段辰昕 107242023004233 西安外国语大学 旅游管理 2023

# MVP plan:

# 1. receive image
#     image is just in path;
# 2. parse image
#     use PIL to parse image; 
#     Make it 2D array of pixels.
# 3. Analyze the image
#     group the image into blocks of pixels, since characters are bigger than pixels.
#     and calculate the average color of each block.
# 4. Render the image
#     use the average color of each block to choose a string to represent the block.
#     and render the image.
#     each block is a character whose color is the average color of the block.

from PIL import Image
import numpy as np
import argparse
import math
import os
import random

def half_to_full_width(s):
    """
    Convert half-width characters in the string to full-width characters.
    """
    full_width_str = ""
    for char in s:
        if char == ' ':
            full_width_str += '\u3000'  # 全角空格
        elif 0x21 <= ord(char) <= 0x7E:
            full_width_str += chr(ord(char) + 0xFEE0)
        else:
            full_width_str += char
    return full_width_str

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', help='input image path')
parser.add_argument('--outdir', help='output directory') # if not set, same as input
parser.add_argument('--output', help='output image path')   # if not set, <input>_kotoba.png
parser.add_argument('--width', help='width of the output image') # if not set, same as input
parser.add_argument('--height', help='height of the output image')  # if not set, same as input
parser.add_argument('--corpus', help='corpus to use') # if not set, use '言葉'
parser.add_argument('--color', help='whether to use color') # if not set, use 'false'
parser.add_argument('--bs', help='block size') # if not set, use 4
parser.add_argument('--bgalpha', help='background alpha; input 10 for 10%') # if not set, use 0.45
args = parser.parse_args()

# get the arguments
input_path = args.input 
if args.outdir:
    output_dir = args.outdir
else:
    # if no `out` directory, make one
    output_dir = 'out'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
if args.output: output_name = args.output
else: output_name = input_path.split('.')[0] + '_kotoba.png'
output_path = os.path.join(output_dir, output_name)

if args.width: width = int(args.width)
else: width = 0

if args.height: height = int(args.height)
else: height = 0

# this is a path to a file which each line is a phrase
if args.corpus: corpus_path = args.corpus
else: corpus_path = None

if args.color: use_color = args.color=='true'

if args.bs: block_size = int(args.bs)
else: block_size = 4

if args.bgalpha: bg_alpha = float(args.bgalpha)/100
else: bg_alpha = 0.45

# get the image
image = Image.open(input_path)
# resize the image
if width == 0: width = image.size[0]
if height == 0: height = image.size[1]
image = image.resize((width, height))

# convert the image to RGB or grayscale
if use_color: image = image.convert('RGB')
else: image = image.convert('L')

# convert the image to numpy array
image = np.array(image)

# get the average color of each block
block_width = math.floor(width / block_size)
block_height = math.floor(height / block_size)
if use_color:
    block_avg_color = np.zeros((block_height, block_width, 3))
    for i in range(block_height):
        for j in range(block_width):
            for k in range(3):
                block_avg_color[i][j][k] = np.mean(image[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size, k])
else:
    block_avg_color = np.zeros((block_height, block_width))
    for i in range(block_height):
        for j in range(block_width):
            block_avg_color[i][j] = np.mean(image[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])

# The characters from the string are always as string (in same order),
# the color of each character, will depending on the block they are representing.

if corpus_path:
    with open(corpus_path, 'r', encoding='utf-8') as f:
        kotoba = set(f.read().splitlines())
else:
    kotoba = {'言葉'}
fw_kotoba = {half_to_full_width(s) for s in kotoba}
kotaba = fw_kotoba

done_word = False

# kotoba = {s+'　' for s in kotoba} # add a space after each word
# note that, all characters should be full-width, so the block size is consistent

# also, add the output to a text html (to keep color) file
# file must be in utf-8
with open(output_path.split('.')[0] + '.html', 'w', encoding='utf-8') as f:
    # tell browser to decode in utf-8
    f.write('<meta charset="UTF-8">\n')
    f.write('<html>\n')
    f.write('<body>\n')
    # set it to not wrap
    f.write('<p style="white-space: nowrap">\n')
    # f.write('<b><strong>')
    # also, make sure the font is heavy, like, very heavy
    # want a very very dense font face
    f.write('<style>body {font-family: "Hiragino Sans GB W3", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", "WenQuanYi Micro Hei", "sans-serif";}</style>\n')
    f.write('<style>body {font-weight: 1000;}</style>\n')
    # also, make the characters tightly packed and line height small
    f.write('<style>body {letter-spacing: -1px; line-height: -1;}</style>\n')
    # generate new image
    if use_color:
        new_image = Image.new('RGB', (width, height), (255, 255, 255))
    else:
        new_image = Image.new('L', (width, height), 255)
    # draw the image

    char = random.choice(tuple(kotoba))
    for i in range(block_height):
        char_idx = -1
        html_buffer = ''
        prev_char_color = None  # keep track of the previous color, if same as current, don't write html tag again.
        for j in range(block_width):
            if done_word: # when word is done, choose a new word
                char = random.choice(tuple(kotoba))
                done_word = False
                char_idx = -1
            char_idx += 1
            if char_idx == len(char) - 1:
                done_word = True
            if use_color:
                char_color = [int(k) for k in block_avg_color[i][j]]
                char_image = Image.new('RGB', (block_size, block_size), tuple(char_color))
                # instead of writng pixel, write a character on the image
                
            else:
                char_color = int(block_avg_color[i][j])
                char_image = Image.new('L', (block_size, block_size), char_color)
            new_image.paste(char_image, (j*block_size, i*block_size))

            # check if the color is the same as the previous one, if so, don't write html tag again
            if prev_char_color is None: prev_char_color = char_color
            if prev_char_color == char_color and j != block_width - 1: # also flush if last block of the row
                html_buffer += char[char_idx]  # write to buffer
                continue

            # in this case, new char is different from everything in the buffer
            # flush the buffer to html
            if use_color:
                f.write('<font color="#%02x%02x%02x">' % tuple(prev_char_color))
                # for each character wriiten, also want its background to be the same color but lighter
                # set the background color to be alpha specified above (default 0.45)
                f.write('<span style="background-color: rgba(%d, %d, %d, %f)">' % tuple(prev_char_color + [bg_alpha]))
            else:
                f.write('<font color="#%02x%02x%02x">' % (prev_char_color, prev_char_color, prev_char_color))
            f.write(html_buffer)    # flush buffer to html
            f.write('</font>')
            html_buffer = char[char_idx]
            prev_char_color = char_color
        f.write('<br>\n')
    # f.write('</strong></b>\n')
    f.write('</p>\n')
    f.write('</body>\n')
    f.write('</html>\n')


# save the image
new_image.save(output_path)

# open the image
os.system('open ' + output_path)
