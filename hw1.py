f = open("hw1.txt", 'r',encoding="utf-8")
Finall = open("hw1end", 'w',encoding="utf-8")
line=f.readline()
label=line[:7].strip().upper()
opcode=line[9:14].strip().upper()
operand=line[17:34].strip().upper()
LOC = 0000
Data = {}
DataCount = 0
objectCode = ''
SYMTAB = {} #儲存label
OPTAB = {
    'ADD' : '18','AND': '40','COMP': '28','DIV': '24',
    'J'   : '3C','JEQ': '30','JGT' : '34','JLT': '38',
    'JSUB': '48','LDA': '00','LDCH': '50','LDL': '08',
    'LDX' : '04','MUL': '20','OR'  : '44','RD' : 'D8',
    'RSUB': '4C','STA': '0C','STCH': '54','STL': '14',
    'STSW': 'E8','STX': '10','SUB' : '1C','TD' : 'E0',
    'TIX' : '2C','WD' : 'DC'
}

def ifComment():
    global label,opcode,operand
    if (len(label)!=0 and label[0]=='.') or line=='': 
        return True
    return False

def storeData():
    global Data,DataCount,opcode,operand,label,LOC,line
    line=line.replace('\n', '').replace('\r', '') #將換行符號替換成空格，消除行尾的換行符號
    newline = label.ljust(8) + ' ' + opcode.ljust(6) + '  ' + operand.ljust(18) + line[34:]
    IntermediateData = {'LOC':hex(LOC)[2:].upper().zfill(6), 'label': label, 'opcode': opcode, 'operand': operand ,'line': newline}
    Data[DataCount] = IntermediateData
    DataCount += 1

def readData():
    global Data, DataCount, LOC, label, opcode, operand, line
    #使用 DataCount 作為索引，從 Data 字典中取得對應索引位置的資訊
    LOC = Data[DataCount]['LOC']
    label = Data[DataCount]['label']
    opcode = Data[DataCount]['opcode']
    operand = Data[DataCount]['operand']
    line = Data[DataCount]['line']
    DataCount += 1

def ascii_to_hex(ascii_str):
    hex_str = ''.join(format(ord(char), 'x') for char in ascii_str)
    return hex_str

#   LOC
if opcode == "START":
    startAddress = int(operand,16) 
    LOC = startAddress
    storeData()
    line=f.readline()
    label=line[:7].strip().upper()
    opcode=line[9:14].strip().upper()
    operand=line[17:34].strip().upper()  
else:
    startAddress = 0000
    LOC = 0000
    
while opcode != "END":
    LOCTEMP = LOC
    if not ifComment():
        if label !='':
            if label in SYMTAB:
                print(LOC + " label " + label + "重複的Label")
            else:
                SYMTAB[label] = hex(LOC)[2:].upper() #去掉十六進制開頭的 '0x'
        if opcode in OPTAB:
            LOCTEMP += 3
        elif opcode == "WORD":
            LOCTEMP += 3
        elif opcode == "RESW":
            LOCTEMP += int(operand)*3
        elif opcode == "RESB":
            LOCTEMP += int(operand)
        elif opcode == "BYTE":
            if operand[0] == 'C':
                LOCTEMP += (len(operand)-3)
            elif operand[0] == 'X':
                LOCTEMP += 1
    storeData()

    LOC = LOCTEMP
    line=f.readline()
    label=line[:7].strip().upper()
    opcode=line[9:14].strip().upper()
    operand=line[17:34].strip().upper()
storeData()


DataCount = 0
readData()

if opcode == "START":
    Finall.write(f"{LOC}{' '}{line}\n")
    readData()
    
#objectCode
while opcode != "END":
    if ifComment():
        Finall.write(f"{line}\n")
    else:
        if opcode in OPTAB:
            if operand in SYMTAB:
                objectCode = OPTAB[opcode] + str(SYMTAB[operand]).zfill(4)
            
            #處理Buffer,X
            elif ',' in operand:
                parts = operand.split(',')
                label = parts[0]
                register = parts[1]
                if label in SYMTAB:
                    label_address = int(SYMTAB[label], 16)  
                    if register == 'X':
                        label_address += 0x8000  
                    final = label_address
                    a = hex(final)[2:]
                    b=str(a)
                    objectCode=OPTAB[opcode] +b
                    
            else:
                objectCode = OPTAB[opcode] + '0000'
                print(LOC + ' ' + operand + ' 搜尋不到此operand')

        elif opcode == 'BYTE':
            if  operand[0] == 'C':
                data = line.split("C'")[1].split("'")[0]
                ascii_value = ascii_to_hex(data).upper()
                objectCode=ascii_value
            elif operand[0] == 'X':
                    data = line.split("X'")[1].split("'")[0]
                    if len(data) > 2:
                        print("Error:必須兩個數值，且介於00~FF")
                    else:
                        try:
                            int_value = int(data, 16)
                            if int_value < 0x00 or int_value > 0xFF:
                                print("Error:超過範圍")
                            else:
                                objectCode = data
                        except ValueError:
                            print("Error: Invalid hexadecimal value")

        elif  opcode == 'WORD':
            if operand[0] == '-':
                objectCode = 'fff' + hex(4096 - int(operand[1:]))[2:].upper()
            else:
                objectCode = hex(int(operand))[2:].zfill(6)
        else:
            objectCode = ''
            
        if opcode == 'RESB' or opcode == 'RESW':
            objectCode=" "

        Finall.write(f"{LOC} {line} {objectCode}\n")

        

    readData()

Finall.write(f"{LOC}{line}\n") #end


