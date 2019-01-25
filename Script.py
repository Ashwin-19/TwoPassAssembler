# Code by Ashwin Singh, Bhuvanyu Dogra
# Roll no.s - 2017222, 2017226
# Branch - CSAM

import numpy
import pandas

# Declare OPCODE arrays

Assembly_Opcodes = ["CLA", "LAC", "SAC", "ADD", "SUB", "BRZ", "BRN", "BRP", "INP", "DSP", "MUL", "DIV", "STP"]
Machine_Opcodes = ["0000", "0001", "0010", "0011", "0100", "0101", "0110", "0111", "1000", "1001", "1010", "1011", "1100"]

# Error Flag

flag = 0

# Location Counter

global Location_Counter

Location_Counter = 0

# Symbol Table

Symbols = []
Types = []
Symbol_Values = []
Valid = []
Symbol_Offset = []
Declared_Symbols = []
Existing_Labels = []

# Literal Table

Literal_Values = []
Literal_Offset = []

# Opcode Table

Opcodes = []
MachineCodes = []
Operand_1 = []
Operand_2 = []
Opcode_Offset = []

# Opening file and taking all instructions initially as lines in a string

f = open("input.txt", "r")
lines = f.readlines()

# Initializing two arrays for use in code

conditional_arr_1 = ["LAC", "SAC", "ADD", "SUB", "BRZ", "BRN", "BRP", "INP", "DSP", "MUL", "DIV"]
Branch_Opcodes = ['BRZ', 'BRN', 'BRP']

# Cleaning the strings in instructions by removing \n and \t

for j in range(len(lines)):
    lines[j] = list(lines[j].split("\t"))
    for i in range(len(lines[j])):
        lines[j][i] = lines[j][i].strip(" ")

for line in lines:
    if len(line) == 1:
        line[0] = line[0].rstrip('\n')
    elif len(line) == 2:
        line[1] = line[1].rstrip("\n")
    elif len(line) == 3:
        line[2] = line[2].rstrip('\n')

# Remove comments
for line in lines:
    if line[0] == "//":
        lines.remove(line)

# Checking for start statement

if lines[0][0] == "START" and len(lines[0]) == 2:
    Location_Counter = int(lines[0][1])
    lines.remove(lines[0])
else:
    raise Exception("No start instruction in code")

# Reading the code line by line

for line in lines:

    # if the length of the instruction is 1
    if len(line) == 1:

        # Only possible case is the case of STP or CLA
        if line[0] == 'STP' or line[0] == 'CLA':
            # adding corresponding opcode to the Opcode Table
            Opcodes.append(line[0])

            # adding corresponding machine opcode to the Opcode Table
            if line[0] == 'STP':
                MachineCodes.append(Machine_Opcodes[-1])
            else:
                MachineCodes.append(Machine_Opcodes[0])

            # No operands required for STP/CLA
            Operand_1.append(None)
            Operand_2.append(None)

            # Storing the location counter for the instruction
            Opcode_Offset.append(Location_Counter)
            Location_Counter += 12

        else:
            raise Exception("Invalid format of instruction")
            flag = 1

    # if the length of the instruction is 2
    elif len(line) == 2:

        # check for DC
        if line[1] == "DC":

            Declared_Symbols.append(line[0])

            # check if the symbol pre-exists
            flag_in = False
            for itr in range(len(Symbols)):

                if line[0] == Symbols[itr]:
                    temp = itr
                    flag_in = True
                    break

            # Case of pre-existence
            if flag_in:

                # update validity
                Valid[temp] = True

                # update type of symbol
                if Types[temp] == "label":
                    raise Exception("Error: Given variable is also a label")
                else:
                    Types[temp] = "variable"

                # store the location counter for instruction
                Symbol_Offset[temp] = Location_Counter

                # store the value of the variable initialized - 0 by default
                Symbol_Values[temp] = 0

            # otherwise add the symbol to the symbol table
            else:

                # add the symbol name
                Symbols.append(line[0])

                # add the symbol type
                Types.append('variable')

                # symbol is valid because DC opcode exists
                Valid.append(True)

                # store the location counter for instruction
                Symbol_Offset.append(Location_Counter)

                # store the value of the variable initialized - 0 by default
                Symbol_Values.append(0)

        # if any other opcode is used except STP/CLA
        elif line[0] in conditional_arr_1:

            # adding corresponding opcode to the Opcode Table
            Opcodes.append(line[0])

            # finding corresponding index for the machine opcode
            for i in range(len(Assembly_Opcodes)):
                if line[0] == Assembly_Opcodes[i]:
                    temp = i
                    break

            # adding corresponding machine opcode to the Opcode Table
            MachineCodes.append(Machine_Opcodes[temp])

            # adding the required operand to the Opcode Table
            Operand_1.append('ACC')
            Operand_2.append(line[1])

            # storing the location counter for the instruction
            Opcode_Offset.append(Location_Counter)

            # Checking if there is a symbol or a literal
            if line[1].isalpha():
                # if not already added to the Symbol Table, add to the table
                if line[1] not in Symbols:

                    # add symbol name
                    Symbols.append(line[1])

                    # validity is not confirmed before DC opcode, hence false currently
                    Valid.append(False)

                    # Value is not known, hence None
                    Symbol_Values.append(None)

                    # check if the symbol is a variable or a label, and put type accordingly
                    if line[0] in Branch_Opcodes:
                        Types.append('label')
                    else:
                        Types.append('variable')

                    # storing the location counter for the instruction in the table
                    Symbol_Offset.append(None)

                else:

                    for itr in range(len(Symbols)):
                        if Symbols[itr] == line[1] and Types[itr] == "label" and line[0] not in Branch_Opcodes:
                            raise Exception("Error: label cannot be used as a variable")
                        elif Symbols[itr] == line[1] and Types[itr] == "variable" and line[0] in Branch_Opcodes:
                            raise Exception("Error: variable cannot be used as a label")

            # if it is a literal
            elif line[1].isdigit():

                # add the value of literal to the literal table
                if int(line[1], 10) not in Literal_Values:
                    Literal_Values.append(int(line[1], 10))

                    # add the value of corresponding location counter to the literal table
                    Literal_Offset.append(Location_Counter)

            # if it is not a symbol/literal, error exists
            else:
                raise Exception("Error: incorrect instruction format for operand")

                # set error flag to 1
                flag = 1

            # Increase the location counter
            Location_Counter += 12

        else:

            # Other possibility for 2-length instruction is label + STP/CLA
            if line[1] == 'STP' or line[1] == 'CLA':

                # adding corresponding opcode to the Opcode Table
                Opcodes.append(line[1])

                # adding corresponding machine opcode to the Opcode Table
                if line[1] == 'STP':
                    MachineCodes.append(Machine_Opcodes[-1])
                else:
                    MachineCodes.append(Machine_Opcodes[0])

                # No operand required for STP/CLA
                Operand_1.append(None)
                Operand_2.append(None)
                Opcode_Offset.append(Location_Counter)

                # check if the label already exists in the table
                flag_in = False
                for itr in range(len(Symbols)):
                    if Symbols[itr] == line[0]:
                        temp = itr
                        flag_in = True
                        break

                # if it pre-exists, update validity and location counter
                if flag_in:

                    if Types[temp] == 'variable':
                        raise Exception("Given label has been used as a variable in the code")
                    else:
                        Valid[temp] = True
                        Symbol_Offset[temp] = Location_Counter

                # otherwise add the label to the symbol table
                else:

                    # add corresponding label name
                    Symbols.append(line[0])

                    # a label has no value, hence none
                    Symbol_Values.append(None)

                    # type is label due to the conditionals
                    Types.append("label")

                    # valid due to the opcode next to it
                    Valid.append(True)

                    # store the location counter for the instruction
                    Symbol_Offset.append(Location_Counter)

                # increment the location counter
                Location_Counter += 12

            # no other possibility for a 2 length instruction exists, so error persists
            else:

                raise Exception("Error: Incorrect Instruction Format - invalid opcode / missing operand")

                # set error flag to 1
                flag = 1

    # if the length of the instruction is 3
    elif len(line) == 3:

        # CASE-1: Declarative instruction
        if line[1] == 'DC':

            Declared_Symbols.append(line[0])

            # check if the symbol pre-exists
            flag_in = False
            for itr in range(len(Symbols)):

                if line[0] == Symbols[itr]:
                    temp = itr
                    flag_in = True
                    break

            # Case of pre-existence
            if flag_in:

                # update validity
                Valid[temp] = True

                # update type of symbol
                if Types[temp] == "label":
                    raise Exception("Error: A label cannot be declared")
                else:
                    Types[temp] = "variable"

                # store the location counter for instruction
                Symbol_Offset[temp] = Location_Counter

                # store the value of the variable initialized - 0 by default
                if line[2].isdigit():
                    Symbol_Values[temp] = int(line[2], 10)
                else:
                    Symbol_Values[temp] = 0

            # otherwise add the symbol to the symbol table
            else:

                # add the symbol name
                Symbols.append(line[0])

                # add the symbol type
                Types.append('variable')

                # symbol is valid because DC opcode exists
                Valid.append(True)

                # store the location counter for instruction
                Symbol_Offset.append(Location_Counter)

                # store the value of the variable initialized - 0 by default
                if line[2].isdigit():
                    Symbol_Values.append(int(line[2], 10))
                else:
                    Symbol_Values.append(0)

            # increment the location counter
            Location_Counter += 12

        # CASE-2: Labelled instruction
        else:

            # finding corresponding index for the machine opcode, if there is any
            if line[1] in Assembly_Opcodes:
                for i in range(len(Assembly_Opcodes)):
                    if line[1] == Assembly_Opcodes[i]:
                        temp = i
                        break

            # if there doesn't exist any such opcode
            else:
                raise Exception("Error: Such an opcode does not exist")
                flag = 1

            # adding corresponding opcode to the Opcode Table
            Opcodes.append(line[1])

            # adding corresponding machine opcode to the Opcode Table
            MachineCodes.append(Machine_Opcodes[temp])

            # adding the required operand to the Opcode Table
            Operand_1.append('ACC')
            Operand_2.append(line[2])

            # storing the location counter for the instruction
            Opcode_Offset.append(Location_Counter)

            Existing_Labels.append(line[0])

            # check for pre-existence of label in symbol table
            if line[0] in Symbols:

                for itr in range(len(Symbols)):
                    if Symbols[itr] == line[0]:
                        temp = itr
                        break

                # update validity of existence
                if Types[temp] == "variable":
                    raise Exception("Given label has been used as a variable in the code")
                else:
                    Valid[temp] = True
                    # update location counter of label
                    Symbol_Offset[temp] = Location_Counter

            else:

                # adding the name of the label
                Symbols.append(line[0])

                # adding the type of the label
                Types.append('label')

                # A label has no value, hence none
                Symbol_Values.append(None)

                # update validity
                Valid.append(True)

                # store the location counter for the instruction
                Symbol_Offset.append(Location_Counter)

            if line[2].isalpha():
                if line[2] in Symbols:

                    for itr in range(len(Symbols)):
                        if Symbols[itr] == line[2]:
                            temp = itr
                            break

                    # update validity of existence

                    if Types[itr] == "label" and line[1] not in Branch_Opcodes:
                        raise Exception("Error: A label cannot be used as a variable")
                    elif Types[itr] == "variable" and (line[1] in Branch_Opcodes):
                        raise Exception("Error: A variable cannot be used as a label")
                    else:
                        Valid[temp] = True

                    if Types[itr] == 'label':
                        Symbol_Offset[itr] = Location_Counter

                else:

                    # adding the name of the label
                    Symbols.append(line[2])

                    # adding the type of the label
                    if line[1] in Branch_Opcodes:
                        Types.append('label')
                    else:
                        Types.append('variable')

                    # A label has no value, hence none
                    Symbol_Values.append(None)

                    # update validity
                    Valid.append(False)

                    # store the location counter for the instruction
                    Symbol_Offset.append(None)

            elif line[2].isdigit():
                # add the value of literal to the literal table
                if int(line[2], 10) not in Literal_Values:
                    Literal_Values.append(int(line[1], 10))

                    # add the value of corresponding location counter to the literal table
                    Literal_Offset.append(Location_Counter)

            else:
                raise Exception("Error: Invalid format for operand")

            # increment location counter
            Location_Counter += 12

    else:

        raise Exception("Error: Instruction length is more than expected")
        flag = 1

# Check for variables not declared
# flag = 0 if no error

for itr in range(len(Symbols)):
    if not Valid[itr]:
        raise Exception("Error: The variable is never declared in the code")
        flag = 1

# to check if the code length can't be fit into the memory of the system
code_length = len(Opcodes) + len(Symbols) + len(Literal_Values)
if code_length > 4096:
    print("Error: memory may be insufficient for the given file")

# Check for STP
if not Opcodes.__contains__("STP"):
    raise Exception("No end instruction in the code")

# Check for duplicate labels
for itr in range(len(Existing_Labels)):
    for itr2 in range(len(Existing_Labels)):
        if Existing_Labels[itr] == Existing_Labels[itr2] and itr != itr2:
            raise Exception("Error: Duplicate label in the code")

# Check for duplicate variables
for itr in range(len(Declared_Symbols)):
    for itr2 in range(len(Declared_Symbols)):
        if Declared_Symbols[itr] == Declared_Symbols[itr2] and itr != itr2:
            raise Exception("Error: Duplicate variable in the code")

if flag == 0:

    # Print Symbol Table
    print("SYMBOL TABLE:")
    print()

    if len(Symbols) != 0:
        Symbol_Table = pandas.DataFrame()
        Symbol_Table['Symbol'] = numpy.array([i for i in Symbols])
        Symbol_Table['Values'] = numpy.array([i for i in Symbol_Values])
        Symbol_Table['Types'] = numpy.array([i for i in Types])
        Symbol_Table['Offset'] = numpy.array([i for i in Symbol_Offset])
        Symbol_Table['Validity'] = numpy.array([i for i in Valid])
        print(Symbol_Table)
    print()

    # Print Literal Table
    print("LITERAL TABLE:")
    print()

    if len(Literal_Values) != 0:
        Literal_Table = pandas.DataFrame()
        Literal_Table['Values'] = numpy.array([i for i in Literal_Values])
        Literal_Table['Offset'] = numpy.array([i for i in Literal_Offset])
        print(Literal_Table)
    print()

    # Print Opcode Table
    print("OPCODE TABLE:")
    print()

    if len(Opcodes) != 0:
        Opcode_Table = pandas.DataFrame()
        Opcode_Table['Opcodes'] = numpy.array([i for i in Opcodes])
        Opcode_Table['Machine Codes'] = numpy.array([i for i in MachineCodes])
        Opcode_Table['Operand 1'] = numpy.array([i for i in Operand_1])
        Opcode_Table['Operand 2'] = numpy.array([i for i in Operand_2])
        Opcode_Table['Offset'] = numpy.array([i for i in Opcode_Offset])
        print(Opcode_Table)

    print()

else:

    SystemExit

# Conversion to Machine language

# Assignment of addresses to symbols and literals

Symbol_addresses = [0 for i in range(len(Symbols))]
Literal_addresses = [0 for i in range(len(Literal_Values))]
Opcode_addresses = [0 for i in range(len(Opcodes))]
Operand_addresses = []

for itr in range(len(Symbols)):

    if Types[itr] == "variable":

        address = Symbol_Offset[itr]
        part = bin(address)
        part = part[2:]
        add_zeros = 8 - len(part)
        part = add_zeros * "0" + part
        Symbol_addresses[itr] = part

for itr in range(len(Literal_Values)):

    address = Literal_Offset[itr]
    part = bin(address)
    part = part[2:]
    add_zeros = 8 - len(part)
    part = add_zeros*"0" + part
    Literal_addresses[itr] = part

for itr in range(len(Opcodes)):

    address = Opcode_Offset[itr]
    part = bin(address)
    part = part[2:]
    add_zeros = 8 - len(part)
    part = add_zeros * "0" + part
    Opcode_addresses[itr] = part

for operand in Operand_2:

    if operand == None:

        Operand_addresses.append("")

    elif operand.isdigit():

        index = Literal_Values.index(int(operand))
        address = Literal_addresses[index]
        Operand_addresses.append(address)

    else:

        index = Symbols.index(operand)

        if Types[index] == "variable":
            address = Symbol_addresses[index]
            Operand_addresses.append(address)
        else:
            offset = Symbol_Offset[index]
            index_2 = Opcode_Offset.index(offset)
            address = Opcode_addresses[index_2]
            Operand_addresses.append(address)

file = open("output.txt", "w")

for itr in range(len(Opcodes)):
    line = Opcode_addresses[itr] + " " + MachineCodes[itr] + " " + Operand_addresses[itr]
    file.write(str(line) + '\n')

file.close()