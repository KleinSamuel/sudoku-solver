#!/usr/bin/python3

import argparse
import imutils
import cv2
import pytesseract
import sys
import sudoku_solver as ss

parser = argparse.ArgumentParser()
parser.add_argument("--image","-i", dest="IMAGE_PATH", required=True)
args = parser.parse_args()

OUTPUT_PATH = args.IMAGE_PATH[0:args.IMAGE_PATH.rfind(".")]+"_solved"+args.IMAGE_PATH[args.IMAGE_PATH.rfind("."):]

# read in image
image = cv2.imread(args.IMAGE_PATH)

# check if sudoku is not fullscreen
tmp_image = imutils.resize(image, height=500)
gray = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,127,255,0)
im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# find largest rectangle in image
highest = 0
bounding_rect = None
for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    rect_size = w*h
    if rect_size < 250000 and rect_size > 100000 and rect_size > highest:
        highest = rect_size
        bounding_rect = cv2.boundingRect(cnt)

# if highest rectangle is found crop image
if not highest == 0:
    x,y,w,h = bounding_rect
    image = tmp_image[y:y+h, x:x+w]

# resize image to 500x500
image = imutils.resize(image, height=500)

# create copy of original image
original_image = image.copy()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,127,255,0)
im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# compute size of single field of 9x9 array of image
inner_rect_width = int(500/9)

cols = "123456789"
rows = "ABCDEFGHI"

sudoku = {}
original_positions = []

# iterate detected numbers
for cnt in contours:

    # get parameters of bounding rectangle of detected part of image
    x,y,w,h = cv2.boundingRect(cnt)

    # compute size of detected part
    rect_size = w*h

    # check if detected part of image is of appropriate size
    if rect_size <= 2000 and rect_size > 400:

        # compute coordinates of center of rectangle
        x_middle = int(x+(w/2))
        y_middle = int(y+(h/2))

        # compute coordinates of rectangle
        x_coord = int(x_middle/inner_rect_width)
        y_coord = int(y_middle/inner_rect_width)

        # crop image part where a digit is detected
        tmp_image = image[y-2:y+h+2, x-2:x+w+2]
        gray = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # use tesseract to detect digits from cropped image parts
        config = ("--oem 2 --psm 10")
        detected_digit = pytesseract.image_to_string(blurred, lang="eng", config=config)

        # store detected digit
        sudoku[rows[y_coord]+cols[x_coord]] = str(detected_digit)

        #cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
        #cv2.rectangle(image, (x_middle,y_middle), (x_middle,y_middle), (255,0,0), 2)
        #font = cv2.FONT_HERSHEY_PLAIN
        #cv2.putText(image, str(x_coord)+":"+str(y_coord), (x,y), font, 1, (0,0,0), 1, cv2.LINE_AA)

# fill empty spaces with 0
for r in rows:
    for c in cols:
        key = r+c
        if not key in sudoku:
            sudoku[key] = str(0)
        else:
            original_positions.append(r+c)

# generate string from detected sudoku
detected_sudoku_string = ss.generate_string_from_sudoku(sudoku)

# solve sudoku
solved_sudoku = ss.solve_sudoku(detected_sudoku_string)

# check if sudoku was valid and can be solved
if solved_sudoku == False:
    print("Not Solvable")
    sys.exit(0)

# print solution into image
font = cv2.FONT_HERSHEY_DUPLEX
for x in range(0,9):
    for y in range(0,9):
        row = rows[y]
        col = cols[x]
        if row+col in original_positions:
            continue
        pos_x = x*inner_rect_width+15
        pos_y = y*inner_rect_width+45
        cv2.putText(original_image, solved_sudoku[row+col], (pos_x,pos_y), font, 1.5, (0,0,0), 1, cv2.LINE_AA)

# save image with solution
cv2.imwrite(OUTPUT_PATH, original_image)