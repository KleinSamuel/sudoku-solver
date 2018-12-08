#!/usr/bin/python3

import sys

# strings for example sudokus where .=0
easy1 = ".94...13..............76..2.8..1.....32.........2...6.....5.4.......8..7..63.4..8"
hard1 = ".....6....59.....82....8....45........3........6..3.54...325..6.................."
test1 = "070006000900000041008009050090007002003000800400800010080300900160000007000500080"

rows = "ABCDEFGHI"
cols = "123456789"

# create combinations of given rows and cols
def combine(row, col):
    out = []
    for r in row:
        for c in col:
            out.append(r+c)
    return out

# list of all fields with respective name; 0:0 = A1; 8:8 = I9;
fieldnames  = combine(rows, cols)

# lists of all row, column and block combinations
entity_1 = []
for c in cols:
    entity_1.append(combine(rows, c))
entity_2 = []
for r in rows:
    entity_1.append(combine(r, cols))
entity_3 = []
for i in range(0,9,3):
    r = rows[i:i+3]
    for j in range(0,9,3):
        c = cols[j:j+3]
        entity_3.append(combine(r, c))

# row, col and block combinations concatenated into list
comparison_entities = (entity_1 + entity_2 + entity_3)

# dict with fieldname as key and fields of row, col, block this field is in
included_dict = {}
for field in fieldnames:
    tmp = []
    for entity in comparison_entities:
        if field in entity:
            tmp.append(entity)
    included_dict[field] = tmp

# set with fieldname as key and unique set of fields of row, col, block this field is in
included_set = {}
for field in fieldnames:
    included_set[field] = set(sum(included_dict[field],[]))-set([field])

# create dict from sudoku string with fieldname as key and list of possible numbers as value
def create_dict_with_possible_numbers_from_string(grid):
    tmp_dict = {}
    for field in fieldnames:
        tmp_dict[field] = cols
    for fieldname,numbers in create_dict_from_string(grid).items():
        if numbers in cols and not find_values(tmp_dict, fieldname, numbers):
            return False
    return tmp_dict

# parse sudoku string into dict where key is fieldname and value is the respective number
def create_dict_from_string(grid):
    out = {}
    for i in range(0,len(grid)):
        out[fieldnames[i]] = grid[i]
    return out

# create new list with all possible numbers for a fieldname
def find_values(tmp_dict, fieldname, numbers):
    tmp = tmp_dict[fieldname].replace(numbers, "")
    if all(remove_impossible_moves(tmp_dict, fieldname, numbers_2) for numbers_2 in tmp):
        return tmp_dict
    else:
        return False

# remove numbers from list which are contained in the same row, col or block
def remove_impossible_moves(tmp_dict, fieldname, numbers):
    if numbers not in tmp_dict[fieldname]:
        return tmp_dict
    tmp_dict[fieldname] = tmp_dict[fieldname].replace(numbers,'')
    if len(tmp_dict[fieldname]) == 0:
        return False
    elif len(tmp_dict[fieldname]) == 1:
        numbers2 = tmp_dict[fieldname]
        if not all(remove_impossible_moves(tmp_dict, fieldname2, numbers2) for fieldname2 in included_set[fieldname]):
            return False
    for fields in included_dict[fieldname]:
        f = [fieldname for fieldname in fields if numbers in tmp_dict[fieldname]]
        if len(f) == 0:
            return False
        elif len(f) == 1:
            if not find_values(tmp_dict, f[0], numbers):
                return False
    return tmp_dict

# print formatted sudoku
def print_sudoku(tmp_dict):
    line = "+-------+-------+-------+"
    print(line)
    for r in rows:
        sys.stdout.write("| ")
        for c in cols:
            sys.stdout.write(tmp_dict[r+c]+" ")
            if int(c)%3 == 0:
                sys.stdout.write("| ")
            if c == "9":
                print("")
        if r in "CF": print(line)
    print(line)

# solve given sudoku string
def solve_sudoku(sudoku_string):
    return _solve_sudoku(create_dict_with_possible_numbers_from_string(sudoku_string))

# recursive part of the solve function
def _solve_sudoku(tmp_dict):
    if tmp_dict is False:
        return False
    # check if every field only has one possible number -> sudoku is solved and can be returned
    return_flag = True
    for fieldname in fieldnames:
        if len(tmp_dict[fieldname]) != 1:
            return_flag = False
            break
    if return_flag:
        return tmp_dict
    # get field with fewest possible numbers
    tmp_field = None
    tmp_counter = 100
    for fieldname in fieldnames:
        if len(tmp_dict[fieldname]) > 1:
            if len(tmp_dict[fieldname]) < tmp_counter:
                tmp_counter = len(tmp_dict[fieldname])
                tmp_field = fieldname
    # iterate each possible number in this field and call recursive function
    return return_one_item(_solve_sudoku(find_values(tmp_dict.copy(), tmp_field, move)) for move in tmp_dict[tmp_field])

# return the first item in dict and False if no items in dict
def return_one_item(tmp_dict):
    for item in tmp_dict:
        if item:
            return item
    return False

# generate a string from a sudoku dict
def generate_string_from_sudoku(sudoku):
    output = ""
    for row in rows:
        for col in cols:
            output += str(sudoku[row+col])
    return output
