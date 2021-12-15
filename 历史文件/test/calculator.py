#!/usr/bin/env python
# Example 2: A Python program from the Raspberry Pi User Guide
userName = input("What is your name? ")
# 两种不同的打印方式
print("Welcome to the program,", userName)
print("Welcome, {0},  to the program.".format(userName))
goAgain = 1
while goAgain == 1:
    firstNumber = int(input("Type the first number: "))
    secondNumber = int(input("Type the second number: "))
    print(firstNumber, "added to", secondNumber, "equals", firstNumber + secondNumber)
    print(firstNumber, "minus", secondNumber, "equals", firstNumber - secondNumber)
    print(firstNumber, "multiplied by", secondNumber, "equals", firstNumber * secondNumber)
    goAgain = int(input("Type 1 to enter more numberes,or any other number to quit: "))

