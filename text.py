# define the id of each page
MENU = 0
ADD = 1
MODIFY = 2
DELETE = 3
REPORT = 4
EXIT = 999

COLUMN = 10  # define the number of columns in the data
SEPARATOR = " | "  # define the character that separates each column of the table
SPACE = len(SEPARATOR)  # define the length fo space between each column of the table

DATA_TYPES = ("int", "str", "int", "int", "int", "int", "int", "int", "percentage", "int")  # define the value type for each column, useful for determine the data type for each value when reading from csv file
STRING_FORMAT = ("%i", "%s", "%i", "%i", "%i", "%i", "%i", "%i", "%.2f%%", "%i")  # define the print format for each column, useful for finding the width each value will take up
STRING_FORMAT_WITH_MIN_WIDTH = ("%%%ii", "%%-%is", "%%%ii", "%%%ii", "%%%ii", "%%%ii", "%%%ii", "%%%ii", "%%%i.2f%%%%", "%%%ii")  # define the print format for each column with custom minimum field width; same as STRING_FORMAT except it allows the program to insert a minimum field width into the string using string formatting before inserting data from the table using string formatting again

page = MENU  # the current page
head = list()  # the header of the table
body = list()  # the body of the the table
max_lens = list()  # the length of the longest value in each column of the table
next_id = int()  # the next entry number used when adding a new entry
break_line_len = int()  # the length of the horizontal break line; changed based on the width of the table

# general-use functions
def line_break(char: str):
    """Print a horizontal line with char"""
    print(char*break_line_len)

def save_csv():
    """Save data to data.csv."""
    f = open("data.csv", 'w')
    line = str()
    for value in head:
        line += value + ','
    f.write(line.rstrip(',')+'\n')
    for entry in body:
        line = str()
        for value in entry:
            line += str(value) + ','
        f.write(line.rstrip(',')+'\n')
    f.close()

def striped_input(prompt: str):
    """Same as input() function except it strips the leading and trailing spaces from the input."""
    return input(prompt).strip()

def get_command(instr: str):
    """Get the command in lowercase from the input excluding '/'."""
    return instr[1:].strip()

def display_help():
    """Display the help message."""
    print()
    print("In any prompt, type '/restart' to restart from the beginning, type '/back' to discard changes and return to the main menu, '/display' to display the data again, and '/help' to see this prompt again.")

def find_entry(key: int):
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

def sum_list(nums: list):
    """Return the sum of all values in a given list. Used when calculating accuracies and combo breaks."""
    sum = 0
    for n in nums:
        sum += n
    return sum

def init():
    """All initialization done at the start of the program such as reading from the file, the width of each columns of the table, the next entry number, the length of the horizontal line in line_break(), and the accuracy and the number of combo break of each entry."""
    global head, body, max_lens, next_id, break_line_len
    head, body = read_csv()
    # convert values from string to int or float if needed
    for i in range(len(body)):
        for j in range(COLUMN):
            if DATA_TYPES[j] == "int":
                body[i][j] = int(body[i][j])
            elif DATA_TYPES[j] == "percentage":
                body[i][j] = float(body[i][j])

    if len(body) == 0:
        next_id = 0
    else:
        next_id = body[-1][0] + 1

    # find the max width for each column of the table, used to align and display the table
    for i in range(COLUMN):
        max_lens.append(len(head[i]))
        for j in range(len(body)):
            if len(STRING_FORMAT[i]%body[j][i]) > max_lens[i]:
                max_lens[i] = len(STRING_FORMAT[i]%body[j][i])
        break_line_len += max_lens[i] + SPACE

# functions for init()
def parse_csvline(line: str):
    """Convert a line in csv into a list of strings"""
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

# functions for display_table()
def head_str(head: list, max_lens: list):
    """Convert the header from list to a string for printing."""
    output = str()
    for i in range(COLUMN):
        output += "%%-%is"%max_lens[i]%head[i] + SEPARATOR
    return output.rstrip()

def body_str(body: list, max_lens: list):
    """Convert body from list to a string for printing."""
    if len(body) == 0:
        return "There are no entries."
    output = str()
    for i in range(len(body)):
        for j in range(COLUMN):
            if DATA_TYPES[j] == "percentage":
                # data with '%' sign have 1 less minimum field width as the '%' sign occupies one space and it is not a part of the number
                output += STRING_FORMAT_WITH_MIN_WIDTH[j]%(max_lens[j]-1)%body[i][j] + SEPARATOR
            else:
                output += STRING_FORMAT_WITH_MIN_WIDTH[j]%max_lens[j]%body[i][j] + SEPARATOR
        output = output.rstrip() + '\n'
    return output.rstrip()

# functions for display
def display_table(head: list, body: list, max_lens: list):
    """Display the data in a table."""
    print(head_str(head, max_lens))
    line_break('-')
    print(body_str(body, max_lens))

def display_metadata(row: list):
    """Display the metadata of a entry: entry number, song name, and difficulty."""
    print()
    print(("Entry #"+STRING_FORMAT[0]+":") % row[0])
    line_break('-')
    print(("Song Name: "+STRING_FORMAT[1]) % row[1])
    print(("Difficulty: "+STRING_FORMAT[2]) % row[2])

def display_score(row: list):
    """Display the score of a entry: number of perfect, great, good, bad, and miss; and accuracy and number of combo break."""
    # find the longest judgment value to align them
    max_len = 0
    for i in range(5):
        if len(STRING_FORMAT[i+3]%row[i+3]) > max_len:
            max_len = len(STRING_FORMAT[i+3]%row[i+3])

    # display the data
    line_break('-')
    print("Score:")
    print(("Perfect  "+STRING_FORMAT_WITH_MIN_WIDTH[3]) % max_len % row[3])
    print(("Great    "+STRING_FORMAT_WITH_MIN_WIDTH[4]) % max_len % row[4])
    print(("Good     "+STRING_FORMAT_WITH_MIN_WIDTH[5]) % max_len % row[5])
    print(("Bad      "+STRING_FORMAT_WITH_MIN_WIDTH[6]) % max_len % row[6])
    print(("Miss     "+STRING_FORMAT_WITH_MIN_WIDTH[7]) % max_len % row[7])
    print(("Accuracy: "+STRING_FORMAT[8]) % row[8])
    print(("Combo Break: "+STRING_FORMAT[9]) % row[9])

def difficulty_filter(diff: int):
    """Display a table only with entries that have difficulties greater or equal to diff."""
    global break_line_len
    # find all entries that satisfy the criteria
    filtered_body = list()
    for i in range(len(body)):
        if int(body[i][2]) >= diff:
            filtered_body.append(body[i])

    # find the maximum width of each column of the filtered table and the length of the break line; these will be different and probably smaller than the original table
    filtered_max_lens = list()
    for i in range(COLUMN):
        break_line_len -= max_lens[i]
        filtered_max_lens.append(len(head[i]))
        for j in range(len(filtered_body)):
            if len(STRING_FORMAT[i]%filtered_body[j][i]) > filtered_max_lens[i]:
                filtered_max_lens[i] = len(STRING_FORMAT[i]%filtered_body[j][i])
        break_line_len += filtered_max_lens[i]

    # display the table
    print()
    print("Project SEKAI Scores: Difficulty >= %i" % diff)
    line_break('=')
    display_table(head, filtered_body, filtered_max_lens)

    # change the length of the break line back to the original
    for i in range(COLUMN):
        break_line_len -= filtered_max_lens[i]
        break_line_len += max_lens[i]

def accuracy_filter(acc: float):
    """Display a table only with entries that have accuracies greater or equal to acc%."""
    global break_line_len
    # find all entries that satisfy the criteria
    filtered_body = list()
    for i in range(len(body)):
        if body[i][8] >= acc:
            filtered_body.append(body[i])

    # find the maximum width of each column of the filtered table and the length of the break line; these will be different and probably smaller than the original table
    filtered_max_lens = list()
    for i in range(COLUMN):
        break_line_len -= max_lens[i]
        filtered_max_lens.append(len(head[i]))
        for j in range(len(filtered_body)):
            if len(STRING_FORMAT[i]%filtered_body[j][i]) > filtered_max_lens[i]:
                filtered_max_lens[i] = len(STRING_FORMAT[i]%filtered_body[j][i])
        break_line_len += filtered_max_lens[i]

    # display the table
    print()
    print("Project SEKAI Scores: Accuracy >= %.2f%%" % acc)
    line_break('=')
    display_table(head, filtered_body, filtered_max_lens)

    # change the length of the break line back to the original
    for i in range(COLUMN):
        break_line_len -= filtered_max_lens[i]
        break_line_len += max_lens[i]

def combo_break_filter(cb: int):
    """Return a table of only entries with accuracies greater or equal to acc%."""
    global break_line_len
    filtered_body = list()
    for i in range(len(body)):
        if body[i][9] <= cb:
            filtered_body.append(body[i])
    print()
    filtered_max_lens = list()
    for i in range(COLUMN):
        break_line_len -= max_lens[i]
        filtered_max_lens.append(len(head[i]))
        for j in range(len(filtered_body)):
            if len(STRING_FORMAT[i]%filtered_body[j][i]) > filtered_max_lens[i]:
                filtered_max_lens[i] = len(STRING_FORMAT[i]%filtered_body[j][i])
        break_line_len += filtered_max_lens[i]

    print("Project SEKAI Scores: Combo Break <= %i" % cb)
    line_break('=')
    display_table(head, filtered_body, filtered_max_lens)
    for i in range(COLUMN):
        break_line_len -= filtered_max_lens[i]
        break_line_len += max_lens[i]

# functions for each page
# the return of these functions is the page the program is going to next
def menu():
    """Display the main menu."""
    print("Project SEKAI Scores")
    line_break('=')
    display_table(head, body, max_lens)
    line_break('=')
    while True:
        print()
        print("List of available action to preform:")
        print("1 -- Add a new entry.")
        # check if there are existing entries
        if len(body) > 0:
            # these operations would only makes sense to do if there are entries to work
            print("2 -- Modify an existing entry.")
            print("3 -- Remove an existing entry.")
            print("4 -- Generate a report based on filters.")
        print("0 -- Exit")
        print()
        action = striped_input("Please enter the number before the action you want to perform: ")
        if not action.isdigit():
            print("Error: '%s' is not a whole number." % action)
            continue
        action = int(action)
        if action == 0:
            return EXIT
        # check if there are existing entries
        elif len(body) == 0:
            # when there are no entries, only adding entries will be available
            if action == 1:
                return action
            else:
                print("Error: '%i' does not associates with any actions." % action)
        else:
            if action < 5:
                return action
            else:
                print("Error: '%i' does not associates with any actions." % action)

def add():
    """Display the entry-adding page."""
    global body, max_lens, break_line_len, next_id
    print()
    line_break('=')
    print()
    print("Please enter information for the new entry.")
    display_help()
    get_diff = True  # define if the program needs to ask for the difficulty of the song after the while loop below ends; True if so and False otherwise
    while True:
        print()
        name = striped_input("Please enter the song name, or enter '/' followed by the entry number you want to copy the song name from: ")
        if len(name) == 0:
            print("Error: the song name should not be blank.")
            continue
        elif name[0] == '/':
            command = get_command(name)
            if command.isdigit():
                index = find_entry(int(command))
                if index == -1:
                    print("Error: entry #%s not found." % command)
                    continue
                restart = False  # define if the program needs to start from the beginning of the large while loop to get the song name again
                while True:
                    display_metadata(body[index])
                    print()
                    response = striped_input("Are you sure you want to copy the song name from this entry? (y/n): ")
                    if response == 'y':
                        name = body[index][1]
                    elif response == 'n':
                        restart = True  # the user doesn't want to copy from this entry, so the program needs to ask the user again to enter the song name
                    else:
                        print("Error: Please answer the question with 'y' for yes and 'n' for no.")
                        continue
                    break
                if restart:
                    continue
                while True:
                    print()
                    response = striped_input("Do you want to copy the difficulty from this entry as well? (y/n): ")
                    if response == 'y':
                        diff = body[index][2]
                        get_diff = False  # the program already got the difficulty of the song so no need to get it again
                    elif response != 'n':
                        print("Error: Please answer the question with 'y' for yes and 'n' for no.")
                        continue
                    # if the response is no, the program will simply break from the loop and get the difficulty from the next while loop
                    break
            elif command == "restart":
                return ADD
            elif command == "back":
                print()
                line_break('=')
                return MENU
            elif command == "display":
                print()
                display_table(head, body, max_lens)
                continue
            elif command == "help":
                display_help()
                continue
            else:
                print("'%s' is not a valid command." % command)
                display_help()
                continue
        break
    # get the difficulty from the user if the program haven't already
    if get_diff:
        while True:
            print()
            diff = striped_input("Please enter the difficulty of the chart: ")
            if len(diff) == 0:
                print("Error: '' is not a number.")
                continue
            elif diff[0] == '/':
                command = get_command(diff)
                if command == "restart":
                    return ADD
                elif command == "back":
                    print()
                    print('=')
                    return MENU
                elif command == "display":
                    print()
                    display_table(head, body, max_lens)
                    continue
                elif command == "help":
                    display_help()
                    continue
                else:
                    print("'%s' is not a valid command." % command)
                    display_help()
                    continue
            elif not diff.isdigit():
                print("Error: '%s' is not a whole number." % diff)
                continue
            diff = int(diff)
            break

    while True:
        score = list()  # stores the number of all judgments (perfect, great, good, bad, and miss) in one list
        for i in range(5):
            while True:
                print()
                number = striped_input("Please enter the number of '%s' you got: " % head[i+3])
                if len(number) == 0:
                    print("Error: '' is not a number.")
                    continue
                elif number[0] == '/':
                    command = get_command(number)
                    if command == "restart":
                        return ADD
                    elif command == "back":
                        print()
                        line_break('=')
                        return MENU
                    elif command == "display":
                        print()
                        display_table(head, body, max_lens)
                        continue
                    elif command == "help":
                        display_help()
                        continue
                    else:
                        print("Error: '%s' is not a valid command." % command)
                        continue
                elif not number.isdigit():
                    print("Error: '%s' is not a whole number." % number)
                    continue
                score.append(int(number))
                break
        # check if the sum of all judgments is 0; it is impossible to have this as charts must have notes in them and there must be a judgment for each of them; also, the accuracy calculation will give involve a division by 0 if this is the case
        if sum_list(score) == 0:
            print("Error: the sum of all judgments can not be 0.")
            continue
        # combine all information of the new entry into one list, in the same format as if it was stored in body
        # accuracy = perfect / sum of all judgments
        # combo break = good + bad + miss
        data = [next_id, name, diff] + score + [score[0]/sum_list(score)*100, sum_list(score[2:])]
        display_metadata(data)
        display_score(data)

        # update max_lens with the lengths from the new entry if necessary
        for i in range(COLUMN):
            if len(STRING_FORMAT[i]%data[i]) > max_lens[i]:
                break_line_len -= max_lens[i]
                max_lens[i] = len(STRING_FORMAT[i]%data[i])
                break_line_len += max_lens[i]
        
        body.append(data)
        save_csv()
        print()
        print("Entry #%i has been added successfully." % next_id)
        next_id += 1  # increase next_id at the end as the print() above uses the previous next_id
        break
    # ask the user if they want to another entry, mainly used to pause the program and let the user see the "added successfully" confirmation
    while True:
        print()
        response = striped_input("Do you want to add another entry? (y/n): ")
        if response == 'y':
            return ADD
        elif response != 'n':
            print("Error: Please answer the question with 'y' for yes and 'n' for no.")
            continue
        # if the response is no, the program will simply break from the loop and return to the main menu
        break
    print()
    line_break('=')
    return MENU

def modify():
    """Display the entry-modifying page."""
    global body, max_lens, break_line_len
    print()
    line_break('=')
    display_help()
    while True:
        print()
        entry = striped_input("Please enter the entry # of the entry that you want to modify: ")
        if len(entry) == 0:
            print("Error: '' is not a number.")
            continue
        elif entry[0] == '/':
            command = get_command(entry)
            if command == "restart":
                return MODIFY
            elif command == "back":
                print()
                line_break('=')
                return MENU
            elif command == "display":
                print()
                display_table(head, body, max_lens)
                continue
            elif command == "help":
                display_help()
                continue
            else:
                print("Error: '%s' is not a valid command." % command)
                continue
        elif not entry.isdigit():
            print("Error: '%s' is not a whole number." % entry)
            continue
        entry = int(entry)
        index = find_entry(entry)
        # check if entry the user is in the database
        if index == -1:
            print("Error: entry #%i not found." % entry)
            continue
        display_metadata(body[index])
        display_score(body[index])
        while True:
            print()
            print("List of fields to modify:")
            print("1 -- Song Name")
            print("2 -- Difficulty")
            print("3 -- Score")
            print()
            field = striped_input("Please enter the number before the field you want to modify: ")
            if len(field) == 0:
                print("Error: '' is not a number.")
                continue
            elif field[0] == '/':
                command = get_command(field)
                if command == "restart":
                    return MODIFY
                elif command == "back":
                    print()
                    line_break('=')
                    return MENU
                elif command == "display":
                    print()
                    display_table(head, body, max_lens)
                    continue
                elif command == "help":
                    display_help()
                    continue
                else:
                    print("Error: '%s' is not a valid command." % command)
                    continue
            elif not field.isdigit():
                print("Error: '%s' is not a whole number" % field)
                continue
            field = int(field)
            if field == 1:
                while True:
                    print()
                    name = striped_input("Please enter the new song name: ")
                    if len(name) == 0:
                        print("Error: song name should not be blank.")
                        continue
                    elif name[0] == '/':
                        command = get_command(name)
                        if command == "restart":
                            return MODIFY
                        elif command == "back":
                            print()
                            line_break('=')
                            return MENU
                        elif command == "display":
                            print()
                            display_table(head, body, max_lens)
                            continue
                        elif command == "help":
                            display_help()
                            continue
                        else:
                            print("Error: '%s' is not a valid command." % command)
                            continue
                    # check if the program needs to update max_lens with this modification; if the lengths of the unmodified data from this entry is the longest of all, and the new data is shorter than the old ones, values from max_lens could change to smaller values and thus need to be updated
                    # only the song name is changed here so only check the length of the song name
                    if len(STRING_FORMAT[1]%body[index][1]) == max_lens[1]:
                        get_max = True
                    else:
                        get_max = False
                    body[index][1] = name
                    break_line_len -= max_lens[1]  # remove the previous longest length from the length of the break line (sum of the longest length from all columns) as the longest length can change by the code below
                    # check if the new song name is even longer the previous longest
                    if len(STRING_FORMAT[1]%body[index][1]) > max_lens[1]:
                        # if so, only need to update max_lens to the new length
                        max_lens[1] = len(STRING_FORMAT[1]%body[index][1])
                    elif get_max:
                        # update max_lens by finding the longest length of this column again
                        max_lens[1] = 0
                        for i in range(len(body)):
                            if len(STRING_FORMAT[1]%body[i][1]) > max_lens[1]:
                                max_lens[1] = len(STRING_FORMAT[1]%body[i][1])
                    break_line_len += max_lens[1]  # add the new longest length to the length of the break line again
                    break
            elif field == 2:
                while True:
                    print()
                    diff = striped_input("Please enter the new difficulty: ")
                    if len(diff) == 0:
                        print("Error: '' is not a number.")
                        continue
                    elif diff[0] == '/':
                        command = get_command(diff)
                        if command == "restart":
                            return MODIFY
                        elif command == "back":
                            print()
                            line_break('=')
                            return MENU
                        elif command == "display":
                            print()
                            display_table(head, body, max_lens)
                            continue
                        elif command == "help":
                            display_help()
                            continue
                        else:
                            print("Error: '%s' is not a valid command." % command)
                            continue
                    elif not diff.isdigit():
                        print("Error: '%s' is not a whole number." % diff)
                        continue
                    # check if the program needs to update max_lens with this modification; if the lengths of the unmodified data from this entry is the longest of all, and the new data is shorter than the old ones, values from max_lens could change to smaller values and thus need to be updated
                    # only the difficulty is changed here so only check the length of the difficulty
                    if len(STRING_FORMAT[2]%body[index][2]) == max_lens[2]:
                        get_max = True
                    else:
                        get_max = False

                    body[index][2] = int(diff)

                    break_line_len -= max_lens[2]  # remove the previous longest length from the length of the break line (sum of the longest length from all columns) as the longest length can change by the code below
                    # check if the new song name is even longer the previous longest
                    if len(str(body[index][2])) > max_lens[2]:
                        # if so, only need to update max_lens to the new length
                        max_lens = len(str(body[index][2]))
                    elif get_max:
                        # update max_lens by finding the longest length of this column again
                        max_lens[2] = 0
                        for i in range(len(body)):
                            if len(STRING_FORMAT[2]%body[i][2]) > max_lens[2]:
                                max_lens[2] = len(STRING_FORMAT[2]%body[i][2])
                    break_line_len += max_lens[2]  # add the new longest length to the length of the break line again
                    break
            elif field == 3:
                while True:
                    get_max = list()  # stores which columns need to update max_lens
                    score = list()  # stores the number of all judgments (perfect, great, good, bad, and miss) in one list
                    # get all judgments from a loop
                    for i in range(5):
                        while True:
                            print()
                            number = striped_input("Please enter the new number of '%s' you got: " % head[i+3])
                            if len(number) == 0:
                                print("Error: '' is not a number.")
                                continue
                            elif number[0] == '/':
                                command = get_command(number)
                                if command == "restart":
                                    return MODIFY
                                elif command == "back":
                                    print()
                                    line_break('=')
                                    return MENU
                                elif command == "display":
                                    print()
                                    display_table(head, body, max_lens)
                                    continue
                                elif command == "help":
                                    display_help()
                                    continue
                                else:
                                    print("Error: '%s' is not a valid command." % command)
                                    continue
                            elif not number.isdigit():
                                print("Error: '%s' is not a whole number." % number)
                                continue
                            break
                        score.append(int(number))
                        # check if the program needs to update max_lens with this modification; if the lengths of the unmodified data from this entry is the longest of all, and the new data is shorter than the old ones, values from max_lens could change to smaller values and thus need to be updated
                        if len(STRING_FORMAT[i+3]%body[index][i+3]) == max_lens[i+3]:
                            get_max.append(True)
                        else:
                            get_max.append(False)
                    
                    if sum_list(score) == 0:
                        print("Error: the sum of all judgments can not be 0.")
                        continue
                    for i in range(5):
                        body[index][i+3] = score[i]

                    # check if the program needs to update max_lens with changes of accuracy and combo break
                    if len(STRING_FORMAT[8]%body[index][8]) == max_lens[8]:
                        get_max.append(True)
                    else:
                        get_max.append(False)
                    if len(STRING_FORMAT[9]%body[index][9]) == max_lens[9]:
                        get_max.append(True)
                    else:
                        get_max.append(False)
                    
                    # change accuracy and combo break as well
                    body[index][8] = score[0] / sum_list(score) * 100
                    body[index][9] = sum_list(score[2:])

                    # update max_lens if necessary
                    for i in range(7):
                        break_line_len -= max_lens[i+3]  # remove the previous longest length from the length of the break line (sum of the longest length from all columns) as the longest length can change by the code below
                        # check if the new song name is even longer the previous longest
                        if len(STRING_FORMAT[i+3]%body[index][i+3]) > max_lens[i+3]:
                            # if so, only need to update max_lens to the new length
                            max_lens = len(STRING_FORMAT[i+3]%body[index][i+3])
                        elif get_max[i]:
                            # update max_lens by finding the longest length of this column again
                            max_lens[i+3] = 0
                            for j in range(len(body)):
                                if len(STRING_FORMAT[i+3]%body[j][i+3]) > max_lens[i+3]:
                                    max_lens[i+3] = len(STRING_FORMAT[i+3]%body[j][i+3])
                        break_line_len += max_lens[i+3]  # add the new longest length to the length of the break line again
                    break
            else:
                print("Error: '%i' does not associate with any fields." % field)
                continue
            display_metadata(body[index])
            display_score(body[index])
            save_csv()
            print()
            print("Entry #%i has been modified successfully." % entry)
            restart = False  # define if the program needs to continue with the current loop
            # ask the user if they want to modify another field of the entry, mainly used to pause the program and let the user see the "modified successfully" confirmation
            while True:
                print()
                response = striped_input("Do you want to modify another field from entry #%i? (y/n): " % entry)
                if response == 'y':
                    restart = True  # as the response is yes, the program needs to ask the user again what field they want to modify
                elif response != 'n':
                    print("Error: Please answer the question with 'y' for yes and 'n' for no.")
                    continue
                # if the response is no, the program will simply break from the loop and return to the main menu
                break
            if restart:
                continue
            break
        print()
        line_break('=')
        return MENU

def delete():
    """Display the entry-deleting page."""
    global body, max_lens, break_line_len
    print()
    line_break('=')
    display_help()
    while True:
        print()
        entry = striped_input("Please enter the entry # of the entry you want to delete: ")
        if len(entry) == 0:
            print("Error: '' is not a number.")
            continue
        elif entry[0] == '/':
            command = get_command(entry)
            if command == "restart":
                return DELETE
            elif command == "back":
                print()
                line_break('=')
                return MENU
            elif command == "display":
                print()
                display_table(head, body, max_lens)
                continue
            elif command == "help":
                display_help()
                continue
            else:
                print("Error: '%s' is not a valid command." % command)
                continue
        elif not entry.isdigit():
            print("Error: '%s' is not a whole number." % entry)
            continue
        entry = int(entry)
        index = find_entry(entry)
        if index == -1:
            print("Error: Entry #%i not found." % entry)
            continue
        display_metadata(body[index])
        display_score(body[index])
        # ask the user to confirm their choice
        while True:
            print()
            response = striped_input("Are you sure you want to delete this entry? This process is not recoverable. (y/n): ")
            if response == 'y':
                get_max = list()  # stores which columns need to update max_lens
                for i in range(COLUMN):
                    if len(STRING_FORMAT[i]%body[index][i]) == max_lens[i]:
                        get_max.append(True)
                    else:
                        get_max.append(False)
                del body[index]
                # update max_lens if necessary
                for i in range(COLUMN):
                    if get_max[i]:
                        break_line_len -= max_lens[i]  # remove the previous longest length from the length of the break line (sum of the longest length from all columns) as the longest length can change by the code below
                        max_lens[i] = 0
                        for j in range(len(body)):
                            if len(STRING_FORMAT[i]%body[j][i]) > max_lens[i]:
                                max_lens[i] = len(STRING_FORMAT[i]%body[j][i])
                        break_line_len += max_lens[i]  # add the new longest length to the length of the break line again
                    break
                save_csv()
                print()
                print("Entry #%i deleted successfully." % entry)
                # ask the user if they want to delete another entry, mainly used to pause the program and let the user see the "deleted successfully" confirmation
                while True:
                    print()
                    response = striped_input("Do you want to delete another entry? (y/n): ")
                    if response == 'y':
                        return DELETE
                    elif response != 'n':
                        print("Error: Please answer the question with 'y' for yes and 'n' for no.")
                        continue
                    # if the response is no, the program will simply break from the loop and return to the main menu
                    break
            elif response == 'n':
                return DELETE
            else:
                print("Error: Please answer the question with 'y' for yes and 'n' for no.")
                continue
            break
        print()
        line_break('=')
        return MENU

def report():
    """Display the report-generating page."""
    line_break('=')
    display_help()
    while True:
        print()
        print("List of filters to choose from:")
        print("1 -- Difficulty >= n")
        print("2 -- Accuracy >= n%")
        print("3 -- Combo Break <= n")
        print()
        argument = striped_input("Please enter the number before the filter you want to use: ")
        if len(argument) == 0:
            print("Error: '' is not a number.")
        elif argument[0] == '/':
            command = get_command(argument)
            if command == "restart":
                return REPORT
            elif command == "back":
                print()
                line_break('=')
                return MENU
            elif command == "display":
                print()
                display_table(head, body, max_lens)
                continue
            elif command == "help":
                display_help()
                continue
            else:
                print("Error: '%s' is not a valid command." % command)
                continue
        elif not argument.isdigit():
            print("Error: '%s' is not whole a number." % argument)
            continue
        argument = int(argument)
        if argument > 3 or argument == 0:
            print("Error: '%i' does not associate with any filters." % argument)
            continue
        if argument == 1:
            while True:
                print()
                diff = striped_input("Please enter n: ")
                if len(diff) == 0:
                    print("Error: '' is not a number.")
                    continue
                elif diff[0] == '/':
                    command = get_command(diff)
                    if command == "restart":
                        return REPORT
                    elif command == "back":
                        print()
                        line_break('=')
                        return MENU
                    elif command == "display":
                        print()
                        display_table(head, body, max_lens)
                        continue
                    elif command == "help":
                        display_help()
                        continue
                elif not diff.isdigit():
                    print("Error: '%s' is not a whole number." % diff)
                    continue
                difficulty_filter(int(diff))
                break
        elif argument == 2:
            while True:
                print()
                acc = striped_input("Please enter n: ")
                if len(acc) == 0:
                    print("Error: '' is not a number.")
                    continue
                elif acc[0] == '/':
                    command = get_command(acc)
                    if command == "restart":
                        return REPORT
                    elif command == "back":
                        return MENU
                    elif command == "display":
                        print()
                        display_table(head, body, max_lens)
                        continue
                    elif command == "help":
                        display_help()
                        continue
                else:
                    # check is the input number is a decimal
                    decimal_point = acc.find('.')
                    if decimal_point == -1:
                        if not acc.isdigit():
                            print("Error: '%s' is not a number between 0 and 100." % acc)
                            continue
                    else:
                        # check if all characters other than the decimal point are digits
                        if not (acc[:decimal_point]+acc[decimal_point+1:]).isdigit():
                            print("Error: '%s' is not a number between 0 and 100." % acc)
                            continue
                acc = float(acc)
                if acc > 100:
                    print("Error: '%s' is not a number between 0 and 100." % acc)
                    continue
                accuracy_filter(acc)
                break
        elif argument == 3:
            while True:
                print()
                cb = striped_input("Please enter n: ")
                if len(cb) == 0:
                    print("Error: '' is not a number.")
                    continue
                elif cb[0] == '/':
                    command = get_command(cb)
                    if command == "restart":
                        return REPORT
                    elif command == "back":
                        print()
                        line_break('=')
                        return MENU
                    elif command == "display":
                        print()
                        display_table(head, body, max_lens)
                        continue
                    elif command == "help":
                        display_help()
                        continue
                elif not cb.isdigit():
                    print("Error: '%s' is not a whole number." % cb)
                    continue
                combo_break_filter(int(cb))
                break
        else:
            print("Error: '%i' does not associate with any filters." % argument)
        break
    line_break("=")
    # ask the user if they want to generate another report, mainly used to pause the program and let the user see the report
    while True:
        print()
        response = striped_input("Do you want to generate another report? (y/n): ")
        if response == 'y':
            return REPORT
        elif response != 'n':
            print("Error: Please answer the question with 'y' for yes and 'n' for no.")
            continue
        # if the response is no, the program will simply break from the loop and return to the main menu
        break
    print()
    line_break('=')
    return MENU

init()
while True:
    # check which page the program is currently on
    if page == MENU:
        page = menu()
    elif page == ADD:
        page = add()
    elif page == MODIFY:
        page = modify()
    elif page == DELETE:
        page = delete()
    elif page == REPORT:
        page = report()
    else:
        # break the infinite loop and end the program
        break
