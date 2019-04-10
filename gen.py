from pandas import DataFrame
import copy
import inspect, re
import os

absolutePath = os.path.dirname(os.path.abspath(__file__))

def varname(p):

  for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
    var = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if var:
      return var.group(1)

productionList = []
newProductionList = []
terminalsList = []
nonTerminalsList = []
closures = {}
shiftList = []
reductionList = []
ruleDict = {}


def readProductions():
    global productionList, terminalsList, nonTerminalsList, ruleDict

    productionFile = open(absolutePath + "/grammar", "r")

    for production in productionFile:
        productionList.append(production.strip())
        if production[0] not in nonTerminalsList:
            nonTerminalsList.append(production[0])

    for production in productionList:
        for character in production.strip():
            if character not in nonTerminalsList and character not in terminalsList:
                terminalsList.append(character)
    terminalsList = terminalsList[1:]
    # # terminalsList = [terminalsList[-1]] + terminalsList[:-1]

    for l in range(1, len(productionList)+1):
        ruleDict[l] = productionList[l-1]

def augmentedProductionList():
    global productionList, newProductionList
    readProductions()
    if "'" not in productionList[0]:
        productionList.insert(0, productionList[0][0]+"' "+productionList[0][0])
        newProductionList = []    
        for production in productionList:
            index = production.index(" ")
            production = production[:index+1]+"."+production[index+1:]
            newProductionList.append(production)

# # augmentedProductionList()
# # print(newProductionList)

def computeFirstClose():
    global newProductionList, nonTerminalsList, closures
    augmentedProductionList()
    temporarProductionList = []
    temporarProductionList.append(newProductionList[0])
    index = 0
    for production in temporarProductionList:
        currentPosition = production.index(".")
        dotIndex = production[currentPosition+1]
        if dotIndex in nonTerminalsList:
            for grammar in newProductionList:
                if grammar[0] == dotIndex and\
                    grammar not in temporarProductionList:
                    temporarProductionList.append(grammar)
        closures[index] = temporarProductionList

# # computeFirstClose()
# # print(closures)
    
def computeShiftLists():
    global productionList, nonTerminalsList, terminalsList, closures, shiftList
    computeFirstClose()
    variables = nonTerminalsList + terminalsList

    index = 0
    currentState = 0
    isDone = False

    while not isDone:
        for variable in variables:

            temporarProductionList = []
            try:
                for rules in closures[currentState]:
                    if rules[-1] == ".":
                        continue
                    dotIndex = rules.index(".")

                    if rules[dotIndex+1] == variable:

                        rule = copy.deepcopy(rules)
                        rule = rule.replace(".", "")
                        rule = rule[:dotIndex+1]+"."+rule[dotIndex+1:]
                        temporarProductionList.append(rule)

                        for rule in temporarProductionList:
                            dotIndex = rule.index(".")
                            if rule[-1] == ".":
                                pass
                            else:
                                dotIndex = rule[dotIndex+1]

                                if dotIndex in nonTerminalsList:
                                    for production in newProductionList:
                                        if production[0] == dotIndex and\
                                         production[1] != "'" and production not in temporarProductionList:
                                            temporarProductionList.append(production)
                
            except:
                isDone = True
                break

            if temporarProductionList:
                if temporarProductionList not in closures.values():
                    index += 1
                    closures[index] = temporarProductionList
                for dictionaryIndex,dictionaryValue in closures.items():
                    if temporarProductionList == dictionaryValue:
                        idx = dictionaryIndex

                shiftList.append([currentState, variable, idx])


        currentState += 1

# # computeShiftLists()
# # for i in shiftList:
# #     print(i)



def nextProduct(character):

    global ruleDict, urm_dict, terminalsList

    value = []
    if character == ruleDict[1][0]:
        value.append("$")
    
    for rule in ruleDict.values():
        
        leftString, rightString = rule.split()
        
        if character == rule[-1]:
            for each in nextProduct(rule[0]):
                if each not in value:
                    value.append(each)
                   
        
        if character in rightString:
            idx = rightString.index(character)
            try:
                if rightString[idx+1] in nonTerminalsList and rightString[idx+1] != character:
                    
                    for each in nextProduct(rightString[idx+1]):
                        value.append(each)
                else:
                    value.append(rightString[idx+1])

            except:
                    
                pass
    return value

# # computeShiftLists()
# # print(nextProduct("E"))

def computeReductionLists():
    global closures, ruleDict, reductionList

    reductionList.append([1, "$", "acc"])

    for item in closures.items():
        try:
            for production in item[1]:
                leftString, rightString = production.split(".")

                for rule in ruleDict.items():

                    if leftString == rule[1]:
                        nextRule = nextProduct(leftString[0])

                        for character in nextRule:
                            reductionList.append([item[0], character, "r"+str(rule[0])])

        except:
            pass

# # computeShiftLists()
# # computeReductionLists()
# # for i in reductionList:
# #     print(i)



computeShiftLists()
computeReductionLists()

terminalsList = [terminalsList[-1]] + terminalsList[:-1]

numberOfLines = sum(1 for line in open(absolutePath + '/grammar'))
for production in range(numberOfLines+1):
    productionList[production] = productionList[production].split()
productionList = productionList[1:]

allCharsList = [None for i in range(len(terminalsList) + 1 + len(nonTerminalsList))]

allCharsList[len(terminalsList)] = '$'
for character in range(len(terminalsList)):
    allCharsList[character] = str(terminalsList[character])

for character in range(len(nonTerminalsList)):
    allCharsList[character+len(terminalsList)+1] = nonTerminalsList[character]


pushDownAutomataTable = [['-' for i in range(len(allCharsList))] for j in range(len(closures))]

def generateTable():
    for item in range(len(shiftList)):
        if shiftList[item][1] in nonTerminalsList:
            pushDownAutomataTable[shiftList[item][0]][allCharsList.index(shiftList[item][1])] =\
            shiftList[item][2]
        if shiftList[item][1] in terminalsList:
            pushDownAutomataTable[shiftList[item][0]][allCharsList.index(shiftList[item][1])] =\
            'd' + str(shiftList[item][2])
    for item in range(len(reductionList)):        
        pushDownAutomataTable[reductionList[item][0]][allCharsList.index(reductionList[item][1])] =\
        reductionList[item][2]


generateTable()
print(DataFrame(pushDownAutomataTable, columns=allCharsList))



testString = input("\n\nINTRODUCETI UN STRING, DOMNULE: ")

testString = testString + "$"
PDAStack = []
PDAStack.append("$")
PDAStack.append("0")
temporarString = "$0"
intermediarStack = []
indexIntermediarStack = 1
t = [None] #used for results
indexTable = 1

lenTestString = len(testString)
space = 22

print('\n'"Stiva:" + (space-int(lenTestString/2))*' ' + "Sirul de intrare:"\
            + (space - 7)*' ' + "Actiune rezutata:"'\n')
print(str(temporarString) + (space - len(PDAStack))*' ' + (lenTestString-len(testString))*' ' +testString)

while PDAStack[len(PDAStack)-1] != '1' or testString != '$':
    try:
        if "a" in PDAStack:
            intermediarStack.append("a" + str(indexTable))
            indexTable += 1

        cod = [] 
        cod.append(PDAStack[len(PDAStack)-1]) # last char from PDAStack
        cod.append(testString[0]) # first char from testString

        firstCharPosition = allCharsList.index(cod[1])

        if firstCharPosition == None:
            break
        if pushDownAutomataTable[int(cod[0])][firstCharPosition][0] == 'd':
            PDAStack.append(testString[0])
            PDAStack.append(pushDownAutomataTable[int(cod[0])][firstCharPosition][1:])
            testString = testString.replace(testString[0],'',1)
        elif pushDownAutomataTable[int(cod[0])][firstCharPosition][0] == 'r':
            char = productionList[int(pushDownAutomataTable[int(cod[0])][firstCharPosition][1:])-1][0]
            segment = len(PDAStack) - 2*len(productionList[int(pushDownAutomataTable[int(cod[0])][firstCharPosition][1:])-1][1])
            for character in PDAStack[segment:]:

                if character != "a" and character != "(" and character != ")" and character in terminalsList:
                    t.append(intermediarStack[len(intermediarStack)-2] + character + intermediarStack[len(intermediarStack)-1])
                    intermediarStack.pop()
                    intermediarStack.pop()
                    intermediarStack.append(varname(t) + str(indexIntermediarStack))
                    print("\nCod generat: " + varname(t) + str(indexIntermediarStack) + " = " + t[indexIntermediarStack] + "\n")
                    indexIntermediarStack += 1
            
            PDAStack = PDAStack[:segment]
            PDAStack.append(char)
            charPosition = allCharsList.index(char)
            PDAStack.append(str(pushDownAutomataTable[int(PDAStack[len(PDAStack)-2])][charPosition]))

        temporarString = ""
        for idx in range(len(PDAStack)):
            temporarString += str(PDAStack[idx])
        print(str(temporarString) + (space - len(temporarString))*' ' + (lenTestString-len(testString))*' ' + testString\
        + (space + int(lenTestString/6))*' ' + pushDownAutomataTable[int(cod[0])][firstCharPosition])

        if pushDownAutomataTable[int(cod[0])][firstCharPosition][0] == '-':
            break
    except:
        break

if PDAStack[len(PDAStack)-1] == '1' and testString == '$':
    print('\n''\t''\t'"<<<<<<<< SIRUL A FOST ACCEPTAT! >>>>>>>\n")

    if t != [t[0]]:
        print("Cod intermediar generat:")
        for idx in range(1,len(t)):
            print(varname(t) + str(idx) + " = " + str(t[idx]))
    else:
        print("Nu s-a generat cod intermediar!")
else:
    print('\n''\t'"¯\_(-_-)_/¯    SIRUL NU A FOST ACCEPTAT!    ¯\_(-_-)_/¯\n")
