"""
Check the text version as well as I spent a lot of time doing it.

Title: Project SEKAI Scores

Description: This database record the scores I achieved in a rhythm game called Project SEKAI.

Fields:

    Entry: The unique id of each entry, every new entry added will have a entry id of 1 larger than the largest entry id found in the database at a given moment.

    Song Name: The name of song I played. Since the game is a rhythm game, I need to choose a song in the game every time I play.

    Difficulty: The difficulty of the chart I played. Every song has 5 different charts I can choose from to play, and every song have charts with different difficulties, ranging from 5-36. In the database the difficulty only ranges from 25-34.

    Perfect, Great, Good, Bad, Miss: These 5 fields are the judgments I achieved from the play. Every time I hit a note when playing, the game will assign me a judgment of how accurate I hit the note based on the timing. A Perfect judgment means I hit the note perfectly, and each judgments down means less accurate hits, with miss meaning I missed the note completely. At the end of each song, the game will give a report of how many each judgment I obtain on the last play, and that is the number I add to the database.

    Accuracy: Related to judgments, the accuracy is a measurement of how accurate the hits are in percentage. The formula is Perfect / Sum of all judgments in . This field will be automatically calculated by the program. Most entries in the database has an accuracy of 95%+ with some being at 80%-95% and no entries has an accuracy below 80%.

    Combo Break: Combo is another metric in rhythm game that counts how many notes in a row a player hits accurately. In this game, Perfect and Great are considered accurate, meaning Good, Bad, and Miss will reset the combo, or "break" it. Combo Break records the number of judgments that "breaks" the combo, so the formula of calculating Combo Break is Good + Bad + Miss. This field will be automatically calculated by the program. Most entries in the database has less than 10 combo breaks, and the maximum is 91 combo breaks.

"""

import pygame
from pygame import draw, event, display, time, font


pygame.init()

# set screen size
SIZE = (800, 500)
screen = display.set_mode(SIZE)

# define states
MENU = 0
POPUP = 1  # not used

CURSOR = '|'  # define the character used for representing a text cursor

input_box = False  # define if there is any type of text input enabled
shift_pressed = [False, False]  # define if the user pressed the left and right shift
shift = False  # define if the user pressed the shift
input_text = None  # stores the text in the text box when a input box is enabled; stores None when no input box is enabled
input_column = int()  # stores the column index of the cell the user is modifying; stores negative values when the user is modifying filter arguments

NUM_SHIFT = (')', '!', '@', '#', '$', '%', '^', '&', '*', '(')  # stores the characters the user is inputting when the user hit shift and a number key at the same time
# stores less-used keys on the keyboard
KEYS = (
    (pygame.K_BACKQUOTE, '`', '~'),
    (pygame.K_MINUS, '-', '_'),
    (pygame.K_EQUALS, '=', '+'),
    (pygame.K_LEFTBRACKET, '[', '{'),
    (pygame.K_RIGHTBRACKET, ']', '}'),
    (pygame.K_BACKSLASH, '\\', '|'),
    (pygame.K_SEMICOLON, ';', ':'),
    (pygame.K_QUOTE, '\'', '"'),
    (pygame.K_COMMA, ',', '<'),
    (pygame.K_PERIOD, '.', '>'),
    (pygame.K_SLASH, '/', '?'),
)

# define fonts
TITLE = font.SysFont("Arial", 30)
OTHER = font.SysFont("Arial", 15)

# define colors
BG = (50, 50, 50)
BORDER = (255, 255, 255)
TABLE_TEXT = (255, 255, 255)
HIGHLIGHT = (0, 0, 159)
ERROR = (255, 204, 0)
BOX = (255, 255, 255)
INPUT_TEXT = (0, 0, 0)
FILTER_ENABLED = (0, 0, 0)
SCROLL_BAR = (255, 255, 255)

COLUMN = 10  # define the number of columns in the data
ROW_HEIGHT = 30  # define the height of each row of the table
TABLE_START_X = 50  # define the the x-value which the visible window of the table starts at
TABLE_END_X = 750  # define the the x-value which the visible window of the table ends at
TABLE_START_Y = 150  # define the the y-value which the visible window of the table starts at
TABLE_END_Y = 450  # define the the y-value which the visible window of the table ends at
PADDING = 5  # define the amount of spaces between the text and the border of the box on each direction
SCROLL_SPEED = ROW_HEIGHT*2+10  # define the number of pixels to shift the table upwards or downwards every time the user scroll using mousewheel
scroll_bar_height = TABLE_END_Y - TABLE_START_Y  # define the height of the scroll bar

DATA_TYPES = ("int", "str", "int", "int", "int", "int", "int", "int", "percentage", "int")  # define the value type for each column, useful for determine the data type for each value when reading from csv file
STRING_FORMAT = ("%i", "%s", "%i", "%i", "%i", "%i", "%i", "%i", "%.2f%%", "%i")  # define the print format for each column, useful for finding the width each value will take up
STRING_JUSTIFY = (1, 0, 1, 1, 1, 1, 1, 1, 1, 1)  # define the justification of each column; 0 for left justified and 1 for right justified

running = True  
timer = time.Clock()

column_width = [50, 0, 60, 50, 40, 40, 40, 40, 60, 90]  # define the width of each column (the second value will be set in int())
column_start_x = list()  # define the x-value of the left border of each column
state = MENU  # the current page
head = list()  # the header of the table
body_csv = list()  # the body of the the table used when saving to file; no errors is written into this list
body_display = list()  # the body that includes all entries the user can see without any filters
body_filtered = list()  # the body the users sees with filters applied
valid = list()  # stores if each cell in body_display is valid or not
valid_filtered = list()  # stores if each cell in body_filtered is valid or not
next_id = int()  # the next entry number used when adding a new entry
selected_entry = -1  # define which entry is selected by the user using the index of body_filtered
table_top_y = TABLE_START_Y  # define the y-value of the start of the first row of the table even that row is not shown
table_bottom_y = int()  # define the y-value of the end of the last row of the table even that row is not shown
scroll_bar_y = TABLE_START_Y  # define the y-position of the top of the scroll bar
scroll_bar_clicked = False  # define if the scroll bar is clicked by the user
scroll_bar_clicked_diff = int()  # define the y-position the user click on the scroll bar relative to the top of the scroll bar 

# define if each filter is enabled
diff_enabled = False
acc_enabled = False
cb_enabled = False
# define each the argument of each filter; if the argument is valid, it will be stored as int or float; if the argument is invalid, it will be stored as string
diff_filter = ""
acc_filter = ""
cb_filter = ""
# define if each argument is valid
diff_valid = False
acc_valid = False
cb_valid = False

# general-use functions
def save_csv():
    """Save data to data.csv."""
    f = open("data.csv", 'w')
    line = str()
    for value in head:
        line += value + ','
    f.write(line.rstrip(',')+'\n')
    for entry in body_csv:
        line = str()
        for value in entry:
            line += str(value) + ','
        f.write(line.rstrip(',')+'\n')
    f.close()

def sum_list(nums: list):
    """Return the sum of all values in a given list. Used for calculating the width of the table, accuracies, and combo breaks."""
    sum = 0
    for n in nums:
        sum += n
    return sum

# functions for initialization
def parse_csvline(line: str):
    """Convert a line in csv into a list of strings."""
    return line.rstrip().split(',')

def read_csv():
    """Read data.csv and return the header and the body of the table from it."""
    f = open("data.csv", 'r')
    head = parse_csvline(f.readline())
    body = list()
    while True:
        line = f.readline()
        if line == "":
            break
        data = parse_csvline(line)
        body.append(data)
    f.close()
    return head, body

def init():
    """All initialization done at the start of the program such as reading from the file, the width of each columns of the table, the next entry number"""
    global column_width, column_start_x, head, body_csv, body_display, valid, next_id, table_bottom_y

    column_width[1] = TABLE_END_X - TABLE_START_X - sum_list(column_width)  # calculate the width of the second column
    # calculate column_start_x using the technique of prefix sum array
    column_start_x.append(TABLE_START_X)
    for i in range(COLUMN-1):
        column_start_x.append(column_start_x[i]+column_width[i])

    head, body_csv = read_csv()
    # convert values from string to int or float if needed
    for i in range(len(body_csv)):
        for j in range(COLUMN):
            if DATA_TYPES[j] == "int":
                body_csv[i][j] = int(body_csv[i][j])
            elif DATA_TYPES[j] == "percentage":
                body_csv[i][j] = float(body_csv[i][j])

    # copy everything from body_csv to body_display
    for i in range(len(body_csv)):
        body_display.append(list())
        valid.append(list())
        for j in range(COLUMN):
            body_display[i].append(body_csv[i][j])
            valid[i].append(True)

    # get body_filtered and valid_filtered
    get_filtered_table()

    if len(body_csv) == 0:
        next_id = 0
    else:
        next_id = body_csv[-1][0] + 1

def display_table():
    """Display the table on the screen."""
    # draw the body starting with the first row that is visible to the user
    for i in range((TABLE_START_Y-table_top_y)//ROW_HEIGHT, len(body_filtered)):
        y = table_top_y+ROW_HEIGHT*i  # calculate the y-value this row starts at
        # if this row is no longer visible to the user, stop drawing and end the loop
        if y >= TABLE_END_Y:
            break
        for j in range(COLUMN):
            # highlight the selected row in a different color
            if i == selected_entry:
                if input_box and input_column == j:
                    # draw the input box when the user is inputting in the current cell
                    draw.rect(screen, BOX, (column_start_x[j], y, column_width[j], ROW_HEIGHT))
                    text = OTHER.render(input_text+CURSOR, True, INPUT_TEXT)
                    text_width, text_height = text.get_size()
                    screen.blit(text, (column_start_x[j]+PADDING, y+PADDING, text_width, text_height))
                    continue
                else:
                    draw.rect(screen, HIGHLIGHT, (column_start_x[j], y, column_width[j], ROW_HEIGHT))
            elif valid_filtered[i][j]:
                draw.rect(screen, BG, (column_start_x[j], y, column_width[j], ROW_HEIGHT))
            else:
                # draw the cell in a different color when the value in cell is invalid
                draw.rect(screen, ERROR, (column_start_x[j], y, column_width[j], ROW_HEIGHT))
            draw.rect(screen, BORDER, (column_start_x[j], y, column_width[j], ROW_HEIGHT), 1)
            if valid_filtered[i][j]:
                # display the text by default format when the text is valid
                text = OTHER.render(STRING_FORMAT[j]%body_filtered[i][j], True, TABLE_TEXT)
                text_width, text_height = text.get_size()
                if STRING_JUSTIFY[j] == 0:
                    screen.blit(text, (column_start_x[j]+PADDING, y+PADDING, text_width, text_height))
                elif STRING_JUSTIFY[j] == 1:
                    screen.blit(text, (column_start_x[j]+column_width[j]-PADDING-text_width, y+PADDING, text_width, text_height))
            else:
                # display the text in string and left justified when the text is invalid
                text = OTHER.render(body_filtered[i][j], True, TABLE_TEXT)
                text_width, text_height = text.get_size()
                screen.blit(text, (column_start_x[j]+PADDING, y+PADDING, text_width, text_height))

    # cover the end of the table to create a constant visible window since sometimes the last row will be only partially visible but the row can only be drawn fully
    draw.rect(screen, BG, (0, TABLE_END_Y, SIZE[0], 50))

    # draw the header of the table last to cover the top of the table (reasons same as above)
    for i in range(COLUMN):
        draw.rect(screen, BG, (column_start_x[i], TABLE_START_Y-ROW_HEIGHT, column_width[i], ROW_HEIGHT))
        draw.rect(screen, BORDER, (column_start_x[i], TABLE_START_Y-ROW_HEIGHT, column_width[i], ROW_HEIGHT), 1)
        text = OTHER.render(head[i], True, TABLE_TEXT)
        text_width, text_height = text.get_size()
        screen.blit(text, (column_start_x[i]+PADDING, TABLE_START_Y-ROW_HEIGHT+PADDING, text_width, text_height))

def find_entry(body: list, key: int):
    """Find an entry from entry number and return the index of the entry. Return -1 if the entry is not found."""
    hi = len(body) - 1
    lo = 0
    while hi - lo > 1:
        mid = (hi+lo) // 2
        if body[mid][0] < key:
            lo = mid + 1
        elif body[mid][0] > key:
            hi = mid - 1
        else:
            return mid
    if body[hi][0] == key:
        return hi
    elif body[lo][0] == key:
        return lo
    else:
        return -1

def lower_bound(body: list, key: int):
    """Find an entry that is the smallest number in body that is greater or equal to the given entry number and return the index of the entry. Return -1 if the given entry number is larger than the largest entry number in body."""
    if len(body) == 0 or body[-1][0] < key:
        return -1
    hi = len(body) - 1
    lo = 0
    while hi != lo:
        mid = (hi+lo) // 2
        if body[mid][0] < key:
            lo = mid + 1
        elif body[mid][0] > key:
            hi = mid
        else:
            return mid
    return hi

def update():
    """Update the table with the new input text."""
    global body_csv, body_display, valid, input_box, input_text, diff_filter, diff_valid, acc_filter, acc_valid, cb_filter, cb_valid
    if not input_box:
        return
    input_text = input_text.strip().rstrip()
    # check if the user is inputting in the table or filter arguments
    if input_column >= 0:
        index = find_entry(body_display, body_filtered[selected_entry][0])
        # check what data type should the text be and check for validity accordingly
        if DATA_TYPES[input_column] == "str":
            body_display[index][input_column] = input_text
            if len(input_text) == 0:
                valid[index][input_column] = False
            else:
                valid[index][input_column] = True
        else:
            # data type here will be int
            if input_column >= 3:
                # here the user input a number for a judgment
                # check if the number is valid
                if input_text.isdigit():
                    body_display[index][input_column] = int(input_text)
                    valid[index][input_column] = True
                    # update accuracy and combo break if the used values are valid
                    if valid[index][5] and valid[index][6] and valid[index][7]:
                        body_display[index][9] = sum_list(body_display[index][5:8])
                        valid[index][9] = True
                        if valid[index][3] and valid[index][4]:
                            body_display[index][8] = body_display[index][3] / sum_list(body_display[index][3:8]) * 100
                            valid[index][8] = True
                else:
                    # change the cell to invalid and change accuracy and combo break to "N/A" if the judgment affect them
                    # perfect and great will only affect accuracy; good, bad, and miss will affect both
                    body_display[index][input_column] = input_text
                    valid[index][input_column] = False
                    body_display[index][8] = "N/A"
                    valid[index][8] = False
                    if input_column >= 5:
                        body_display[index][9] = "N/A"
                        valid[index][9] = False

            elif input_column == 2:
                # here the user is input the difficulty
                # check if the number is valid
                if input_text.isdigit():
                    body_display[index][input_column] = int(input_text)
                    valid[index][input_column] = True
                else:
                    body_display[index][input_column] = input_text
                    valid[index][input_column] = False

        # if all values in the modified row is valid, save to the file
        if valid[index] == [True] * COLUMN:
            insert_index = lower_bound(body_csv, body_display[index][0])
            data = list()
            for i in range(COLUMN):
                data.append(body_display[index][i])
            if insert_index == -1:
                body_csv.append(data)
            elif body_csv[insert_index][0] == body_display[index][0]:
                body_csv[insert_index] = data
            else:
                body_csv = body_csv[:insert_index] + [data] + body_csv[insert_index:]
            save_csv()
    else:
        if input_column == -1:
            if input_text.isdigit():
                diff_valid = True
                diff_filter = int(input_text)
            else:
                diff_valid = False
                diff_filter = input_text
        elif input_column == -2:
            decimal_point = input_text.find('.')
            if decimal_point == -1:
                if input_text.isdigit():
                    acc_valid = True
                    acc_filter = round(float(input_text), 2)
                    if acc_filter > 100:
                        acc_filter = input_text
                        acc_valid = False
                else:
                    acc_valid = False
                    acc_filter = input_text
            else:
                if (input_text[:decimal_point]+input_text[decimal_point+1:]).isdigit():
                    acc_valid = True
                    acc_filter = round(float(input_text), 2)
                    if acc_filter > 100:
                        acc_filter = input_text
                        acc_valid = False
                else:
                    acc_valid = False
                    acc_filter = input_text
        else:
            if input_text.isdigit():
                cb_valid = True
                cb_filter = int(input_text)
            else:
                cb_valid = False
                cb_filter = input_text

    get_filtered_table()
    input_box = False
    input_text = None

def get_filtered_table():
    """Get body_filtered and valid_filtered with filters applied."""
    global body_filtered, valid_filtered, table_bottom_y
    body_filtered = list()
    valid_filtered = list()
    if diff_enabled and diff_valid:
        # add any entries that match the filter
        for i in range(len(body_display)):
            if not valid[i][2] or body_display[i][2] >= diff_filter:
                body_filtered.append(body_display[i])
                valid_filtered.append(valid[i])
    else:
        # add the entire table when difficulty filter is not used
        for i in range(len(body_display)):
            body_filtered.append(body_display[i])
            valid_filtered.append(valid[i])
    if acc_enabled and acc_valid:
        # delete any entries that doesn't match the filter
        for i in range(len(body_filtered)-1, -1, -1):
            if valid_filtered[i][8] and round(body_filtered[i][8], 2) < acc_filter:
                del body_filtered[i]
                del valid_filtered[i]
    if cb_enabled and cb_valid:
        # delete any entries that doesn't match the filter
        for i in range(len(body_filtered)-1, -1, -1):
            if valid_filtered[i][9] and body_filtered[i][9] > cb_filter:
                del body_filtered[i]
                del valid_filtered[i]
    table_bottom_y = table_top_y + len(body_filtered)*ROW_HEIGHT

init()
while True:
    if state == MENU:
        # fill the background
        draw.rect(screen, BG, (0, 0)+SIZE)

        # calculate the height of the scroll bar by a very complicated formula
        scroll_bar_height = (TABLE_END_Y-TABLE_START_Y) * (TABLE_END_Y-TABLE_START_Y) // (table_bottom_y-table_top_y)

        for e in event.get():
            if e.type == pygame.QUIT:
                running = False
                break
            if e.type == pygame.MOUSEBUTTONDOWN:
                x, y = e.pos
                # check if the user uses the left-click
                if e.button == 1:
                    # check if the user clicks inside the table
                    if x >= TABLE_START_X and x <= TABLE_END_X and y >= TABLE_START_Y and y <= TABLE_END_Y and y <= table_bottom_y:
                        entry = (y-table_top_y) // ROW_HEIGHT  # get the entry index the user clicks on
                        # check if the user click on the same entry twice or more
                        if entry == selected_entry:
                            if x >= column_start_x[1] and x < column_start_x[8]:
                                # find which column the user clicks on
                                for i in range(8, 0, -1):
                                    # check if the user click on column i
                                    if x >= column_start_x[i]:
                                        # if yes, check if the user click was modifying another column before
                                        if input_box and input_column != i:
                                            update()
                                        if not input_box:
                                            # enable the input box
                                            input_box = True
                                            input_text = ""
                                            input_column = i
                                        break
                            else:
                                update()
                        else:
                            update()
                            selected_entry = entry
                    else:
                        # check if the user clicks on the "EXIT" button
                        if x >= 700 and x <= 750 and y >= 20 and y <= 50:
                            running = False
                            break
                        # check if the user clicks around the filter area
                        if x <= 530 and y >= 75 and y <= 95:
                            # check if the user clicks on the difficulty filter
                            if x >= 105 and x <= 235:
                                # check if the user click on the box (the clickable area is larger than the box)
                                if x < 180:
                                    diff_enabled = not diff_enabled
                                    get_filtered_table()
                                else:
                                    if input_box and input_column != -1:
                                        update()
                                        selected_entry = -1
                                    input_box = True
                                    input_text = ""
                                    input_column = -1
                                    continue
                            # check if the user clicks on the accuracy filter
                            elif x >= 235 and x <= 365:
                                # check if the user click on the box (the clickable area is larger than the box)
                                if x < 320:
                                    acc_enabled = not acc_enabled
                                    get_filtered_table()
                                else:
                                    if input_box and input_column != -2:
                                        update()
                                        selected_entry = -1
                                    input_box = True
                                    input_text = ""
                                    input_column = -2
                                    continue
                            # check if the user clicks on the combo break filter
                            elif x >= 385 and x <= 535:
                                # check if the user click on the box (the clickable area is larger than the box)
                                if x < 490:
                                    cb_enabled = not cb_enabled
                                    get_filtered_table()
                                else:
                                    if input_box and input_column != 3:
                                        update()
                                        selected_entry = -1
                                    input_box = True
                                    input_text = ""
                                    input_column = -3
                                    continue
                        # check if the user clicks on the option area
                        elif x >= 550 and y >= 70 and y <= 100:
                            # check if the user clicks on the "Delete" button and the user has chosen one entry
                            if x >= 690 and x <= 750 and selected_entry != -1:
                                index_display = find_entry(body_display, body_filtered[selected_entry][0])  # find the entry in body_display
                                index_csv = find_entry(body_csv, body_filtered[selected_entry][0])  # find the entry in body_csv
                                # if the entry is found in body_csv, delete it as well
                                if index_csv != -1:
                                    del body_csv[index_csv]
                                del body_filtered[selected_entry]
                                del valid_filtered[selected_entry]
                                del body_display[index_display]
                                del valid[index_display]
                                table_bottom_y -= ROW_HEIGHT
                                input_box = False
                                input_text = None
                                save_csv()
                                # change selected_entry if it goes over the max index of the table, which happens after deleting the last element in the table
                                if selected_entry == len(body_filtered):
                                    selected_entry -= 1
                                # calculate next_id
                                if len(body_display) == 0:
                                    next_id = 0
                                else:
                                    next_id = body_display[-1][0] + 1
                                continue
                            # check if the user clicks on the "Duplicate" button and the user has chosen one entry
                            elif x >= 620 and x <= 680 and selected_entry != -1:
                                update()
                                # add the duplicated entry to the end of the table
                                body_display.append(list())
                                valid.append(list())
                                body_display[-1].append(next_id)
                                valid[-1].append(True)
                                for i in range(1, COLUMN):
                                    body_display[-1].append(body_filtered[selected_entry][i])
                                    valid[-1].append(valid_filtered[selected_entry][i])
                                body_filtered.append(body_display[-1])
                                valid_filtered.append(valid[-1])

                                # save to file is the duplicated entry is valid
                                if valid_filtered[selected_entry] == [True]*COLUMN:
                                    body_csv.append(list())
                                    for i in range(COLUMN):
                                        body_csv[-1].append(body_filtered[selected_entry][i])
                                    save_csv()

                                table_bottom_y += ROW_HEIGHT
                                # shift the table to the end
                                diff = table_bottom_y - TABLE_END_Y
                                table_bottom_y -= diff
                                table_top_y -= diff
                                selected_entry = len(body_filtered) - 1
                                next_id += 1
                                continue
                            # check if the user clicks on the "Add" button
                            elif x >= 550 and x <= 610 and next_id < 100000:  # stop adding new entries when the next entry number will reach 6-digit since the number will exceed the column width at that point
                                update()
                                # add a blank entry to the end of the table
                                body_display.append([next_id]+[str()]*7+["N/A"]*2)
                                valid.append([True]+[False]*(COLUMN-1))
                                body_filtered.append(body_display[-1])
                                valid_filtered.append(valid[-1])
                                table_bottom_y += ROW_HEIGHT
                                # shift the table to the end
                                diff = table_bottom_y - TABLE_END_Y
                                table_bottom_y -= diff
                                table_top_y -= diff
                                selected_entry = len(body_filtered) - 1
                                next_id += 1
                                continue
                        elif table_bottom_y-table_top_y > TABLE_END_Y-TABLE_START_Y and x >= TABLE_END_X+5 and x <= TABLE_END_X+15:
                            # check if the user clicked on the scroll bar
                            if y >= scroll_bar_y and y <= scroll_bar_y+scroll_bar_height:
                                scroll_bar_clicked = True
                                scroll_bar_clicked_diff = y - scroll_bar_y
                            elif y >= TABLE_START_Y and y <= TABLE_END_Y:
                                scroll_bar_y = y - scroll_bar_height//2  # move the center of the scroll bar to where the mouse pointer is
                                # restrict the position of the scroll bar
                                if scroll_bar_y < TABLE_START_Y:
                                    scroll_bar_y = TABLE_START_Y
                                elif scroll_bar_y > TABLE_END_Y-scroll_bar_height:
                                    scroll_bar_y = TABLE_END_Y - scroll_bar_height
                                # find the position of the table by a complex formula
                                new_table_top_y = TABLE_START_Y - (scroll_bar_y-TABLE_START_Y)*(table_bottom_y-table_top_y-TABLE_END_Y+TABLE_START_Y)//(TABLE_END_Y-TABLE_START_Y-scroll_bar_height)
                                # shift the table
                                diff = new_table_top_y - table_top_y
                                table_top_y += diff
                                table_bottom_y += diff
                                scroll_bar_clicked = True
                                scroll_bar_clicked_diff = y - scroll_bar_y
                        update()
                        selected_entry = -1
                # check if the user is scrolling
                elif e.button == 4:  # downscroll
                    if x >= TABLE_START_X and x <= TABLE_END_X and y >= TABLE_START_Y and y <= TABLE_END_Y:
                        # only shift the table if the point is on the table and disable any input within the table
                        if input_box and input_column >= 0:
                            input_box = False
                            input_text = None
                        table_top_y += SCROLL_SPEED
                        table_bottom_y += SCROLL_SPEED
                elif e.button == 5:  # upscroll
                    if x >= TABLE_START_X and x <= TABLE_END_X and y >= TABLE_START_Y and y <= TABLE_END_Y:
                        # only shift the table if the point is on the table and disable any input within the table
                        if input_box and input_column >= 0:
                            input_box = False
                            input_text = None
                        table_top_y -= SCROLL_SPEED
                        table_bottom_y -= SCROLL_SPEED
            elif e.type == pygame.MOUSEBUTTONUP:
                if table_bottom_y-table_top_y > TABLE_END_Y-TABLE_START_Y:
                    scroll_bar_clicked = False
            elif e.type == pygame.KEYDOWN:
                if input_box:
                    # check if the user is inputting numbers
                    if e.key >= pygame.K_0 and e.key <= pygame.K_9:
                        if shift:
                            input_text += NUM_SHIFT[e.key-pygame.K_0]  # get the character the user is inputting from NUM_SHIFT
                        else:
                            input_text += chr(e.key-pygame.K_0+ord('0'))  # get the number the user is inputting by ASCII code
                    elif e.key >= pygame.K_a and e.key <= pygame.K_z:
                        if shift:
                            input_text += chr(e.key-pygame.K_a+ord('A'))  # get the letter the user is inputting by ASCII code
                        else:
                            input_text += chr(e.key-pygame.K_a+ord('a'))  # get the letter the user is inputting by ASCII code
                    elif e.key == pygame.K_SPACE:
                        input_text += ' '
                    elif e.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif e.key == pygame.K_RETURN:
                        # update the table when the user pressed enter
                        update()
                    elif e.key == pygame.K_ESCAPE:
                        # do not update the table when the user pressed escape
                        input_box = False
                        input_text = None
                    elif e.key == pygame.K_LSHIFT:
                        shift_pressed[0] = True
                        shift = True
                    elif e.key == pygame.K_RSHIFT:
                        shift_pressed[1] = True
                        shift = True
                    else:
                        # check if the user is inputting other keys on the keyboard from KEYS
                        for key in KEYS:
                            if e.key == key[0]:
                                if shift:
                                    input_text += key[2]
                                else:
                                    input_text += key[1]
                                break
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LSHIFT:
                    shift_pressed[0] = False
                    shift = shift_pressed[0] or shift_pressed[1]
                elif e.key == pygame.K_RSHIFT:
                    shift_pressed[1] = False
                    shift = shift_pressed[0] or shift_pressed[1]
            elif e.type == pygame.MOUSEMOTION:
                # check if the scroll bar is dragged
                if scroll_bar_clicked:
                    x, y = e.pos
                    scroll_bar_y = y - scroll_bar_clicked_diff
                    # restrict the position of the scroll bar
                    if scroll_bar_y < TABLE_START_Y:
                        scroll_bar_y = TABLE_START_Y
                    elif scroll_bar_y > TABLE_END_Y-scroll_bar_height:
                        scroll_bar_y = TABLE_END_Y - scroll_bar_height
                    # find the position of the table by a complex formula
                    new_table_top_y = TABLE_START_Y - (scroll_bar_y-TABLE_START_Y)*(table_bottom_y-table_top_y-TABLE_END_Y+TABLE_START_Y)//(TABLE_END_Y-TABLE_START_Y-scroll_bar_height)
                    # shift the table
                    diff = new_table_top_y - table_top_y
                    table_top_y += diff
                    table_bottom_y += diff
    # end the loop if the user pressed exit
    if not running:
        break

    # check if the table scroll beyond the allowed range, if yes, shift the table back
    if table_bottom_y < TABLE_END_Y:
        diff = TABLE_END_Y - table_bottom_y
        table_top_y += diff
        table_bottom_y += diff
    if table_top_y > TABLE_START_Y:
        diff = table_top_y - TABLE_START_Y
        table_top_y -= diff
        table_bottom_y -= diff

    # check if a scroll bar is needed
    if table_bottom_y-table_top_y > TABLE_END_Y-TABLE_START_Y:
        if not scroll_bar_clicked:
            # find the position of the scroll bar by a very complex formula: 
            scroll_bar_y = TABLE_START_Y + (TABLE_START_Y-table_top_y)*(TABLE_END_Y-TABLE_START_Y-scroll_bar_height)//(table_bottom_y-table_top_y-TABLE_END_Y+TABLE_START_Y)
        #draw the scroll bar
        draw.rect(screen, SCROLL_BAR, (TABLE_END_X+5, scroll_bar_y, 10, scroll_bar_height))

    if input_box:
        # check if input text reach the width of the input box
        text = OTHER.render(input_text, True, TABLE_TEXT)
        text_width, text_height = text.get_size()
        if input_column >= 0:
            if text_width + PADDING*2 > column_width[input_column]:
                input_text = input_text[:-1]
        else:
            if text_width + PADDING*2 > 45:
                input_text = input_text[:-1]

    # display the title
    text = TITLE.render("Project SEKAI Scores", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (400-text_width//2, 20, text_width, text_height))

    # display the table
    display_table()

    # display the filters
    text = OTHER.render("Filters:", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (TABLE_START_X, 70+PADDING, text_width, text_height))

    text = OTHER.render("Difficulty ≥", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (120, 70+PADDING, text_width, text_height))
    draw.rect(screen, BOX, (105, 80, 10, 10))
    if diff_enabled:
        # draw a dot in the box when the filter is enabled
        draw.circle(screen, FILTER_ENABLED, (110, 85), 3)
    draw.rect(screen, BOX, (180, 75, 45, 20))
    if not diff_valid:
        # outline the text box with a different color when the text inside is invalid
        draw.rect(screen, ERROR, (180, 75, 45, 20), 3)
    if input_box and input_column == -1:
        text = OTHER.render(input_text+CURSOR, True, INPUT_TEXT)
    elif diff_valid:
        text = OTHER.render("%i"%diff_filter, True, INPUT_TEXT)
    else:
        text = OTHER.render(diff_filter, True, INPUT_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (180+PADDING, 70+PADDING, text_width, text_height))

    text = OTHER.render("Accuracy ≥                  %", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (250, 70+PADDING, text_width, text_height))
    draw.rect(screen, BOX, (235, 80, 10, 10))
    if acc_enabled:
        # draw a dot in the box when the filter is enabled
        draw.circle(screen, FILTER_ENABLED, (240, 85), 3)
    draw.rect(screen, BOX, (320, 75, 45, 20))
    if not acc_valid:
        # outline the text box with a different color when the text inside is invalid
        draw.rect(screen, ERROR, (320, 75, 45, 20), 3)
    if input_box and input_column == -2:
        text = OTHER.render(input_text+CURSOR, True, INPUT_TEXT)
    elif acc_valid:
        text = OTHER.render("%.2f"%acc_filter, True, INPUT_TEXT)
    else:
        text = OTHER.render(acc_filter, True, INPUT_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (320+PADDING, 70+PADDING, text_width, text_height))

    text = OTHER.render("Combo Break ≤", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (400, 70+PADDING, text_width, text_height))
    draw.rect(screen, BOX, (385, 80, 10, 10))
    if cb_enabled:
        # draw a dot in the box when the filter is enabled
        draw.circle(screen, FILTER_ENABLED, (390, 85), 3)
    draw.rect(screen, BOX, (490, 75, 45, 20))
    if not cb_valid:
        # outline the text box with a different color when the text inside is invalid
        draw.rect(screen, ERROR, (490, 75, 45, 20), 3)
    if input_box and input_column == -3:
        text = OTHER.render(input_text+CURSOR, True, INPUT_TEXT)
    elif cb_valid:
        text = OTHER.render("%i"%cb_filter, True, INPUT_TEXT)
    else:
        text = OTHER.render(cb_filter, True, INPUT_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (490+PADDING, 70+PADDING, text_width, text_height))

    # display the buttons
    text = OTHER.render("Add", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (580-text_width//2, 70+PADDING, text_width, text_height))
    draw.rect(screen, BORDER, (550, 70, 60, 30), 1)

    text = OTHER.render("Duplicate", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (650-text_width//2, 70+PADDING, text_width, text_height))
    draw.rect(screen, BORDER, (620, 70, 60, 30), 1)

    text = OTHER.render("Delete", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (720-text_width//2, 70+PADDING, text_width, text_height))
    draw.rect(screen, BORDER, (690, 70, 60, 30), 1)

    text = OTHER.render("EXIT", True, TABLE_TEXT)
    text_width, text_height = text.get_size()
    screen.blit(text, (725-text_width//2, 25, text_width, text_height))
    draw.rect(screen, BORDER, (700, 20, 50, 30), 1)

    display.flip()
    timer.tick(60)

pygame.quit()
