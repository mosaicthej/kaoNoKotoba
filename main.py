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

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', help='input image path')
parser.add_argument('--output', help='output image path')   # if not set, <input>_kotoba.png
parser.add_argument('--width', help='width of the output image') # if not set, same as input
parser.add_argument('--height', help='height of the output image')  # if not set, same as input
parser.add_argument('--char', help='string to render the image') # if not set, use '言葉'
args = parser.parse_args()

# get the arguments
input_path = args.input 
if args.output:
    output_path = args.output
else:
    output_path = input_path.split('.')[0] + '_kotoba.png'
if args.width:
    width = int(args.width)
else:
    width = 0
if args.height:
    height = int(args.height)
else:
    height = 0
if args.char:
    char = args.char
else:
    char = '言葉'

# get the image
image = Image.open(input_path)
# resize the image
if width == 0:
    width = image.size[0]
if height == 0:
    height = image.size[1]
image = image.resize((width, height))
# convert the image to grayscale
image = image.convert('L')
# convert the image to numpy array
image = np.array(image)

# get the average color of each block
block_size = 4
block_width = math.floor(width / block_size)
block_height = math.floor(height / block_size)
block_avg_color = np.zeros((block_height, block_width))
for i in range(block_height):
    for j in range(block_width):
        block_avg_color[i][j] = np.mean(image[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size])

# The characters from the string are always as string (in same order),
# the color of each character, will depending on the block they are representing.

# also, add the output to a text html (to keep color) file
# file must be in utf-8
with open(output_path.split('.')[0] + '.html', 'w', encoding='utf-8') as f:
    f.write('<html>\n')
    f.write('<body>\n')
    # generate new image
    new_image = Image.new('L', (width, height), 255)
    # draw the image
    for i in range(block_height):
        for j in range(block_width):
            char_idx = j % len(char)
            char_color = int(block_avg_color[i][j])
            char_image = Image.new('L', (block_size, block_size), char_color)
            new_image.paste(char_image, (j*block_size, i*block_size))

            # write to html file, color needs to be in hex
            f.write('<font color="#%02x%02x%02x">' % (char_color, char_color, char_color))
            f.write(char[char_idx])
            f.write('</font>')
        f.write('<br>\n')
    f.write('</body>\n')
    f.write('</html>\n')


# save the image
new_image.save(output_path)

# open the image
os.system('open ' + output_path)