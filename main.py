# receive an image, render the image using string of the choice.

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
if args.output:
    output_name = args.output
else:
    output_name = input_path.split('.')[0] + '_kotoba.png'
output_path = os.path.join(output_dir, output_name)

if args.width:
    width = int(args.width)
else:
    width = 0
if args.height:
    height = int(args.height)
else:
    height = 0
if args.corpus: # this is a path to a file which each line is a phrase
    corpus_path = args.corpus
else:
    corpus_path = None
if args.color:
    use_color = args.color=='true'
if args.bs:
    block_size = int(args.bs)
else:
    block_size = 4

# get the image
image = Image.open(input_path)
# resize the image
if width == 0:
    width = image.size[0]
if height == 0:
    height = image.size[1]
image = image.resize((width, height))
if use_color:
    # convert the image to RGB
    image = image.convert('RGB')
else:
    # convert the image to grayscale
    image = image.convert('L')
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
        kotaba = set(f.read().splitlines())
else:
    kotaba = {'言葉'}
done_word = False

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
    f.write('<style>body {font-weight: 1000;}</style>\n')
    # generate new image
    if use_color:
        new_image = Image.new('RGB', (width, height), (255, 255, 255))
    else:
        new_image = Image.new('L', (width, height), 255)
    # draw the image

    char = random.choice(tuple(kotaba))
    for i in range(block_height):
        char_idx = -1
        for j in range(block_width):
            if done_word: # when word is done, choose a new word
                char = random.choice(tuple(kotaba))
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

            # write to html file, color needs to be in hex
            if use_color:
                f.write('<font color="#%02x%02x%02x">' % tuple(char_color))
            else:
                f.write('<font color="#%02x%02x%02x">' % (char_color, char_color, char_color))
            f.write(char[char_idx])
            f.write('</font>')
        f.write('<br>\n')
    # f.write('</strong></b>\n')
    f.write('</p>\n')
    f.write('</body>\n')
    f.write('</html>\n')


# save the image
new_image.save(output_path)

# open the image
os.system('open ' + output_path)