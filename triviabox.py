#!/usr/bin/python

import random
import sys
import sqlite3
from sqlite3 import Error

def CreateConnection(dbFile):
    try:
        conn = sqlite3.connect(dbFile)
        return conn
    except Error as e:
        print(e)
    return None

def CountQuestions(conn):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM Trivia')

    return cur.fetchone()[0]

def GetQuestion(conn, countQuestions):
    id = random.randrange(1, countQuestions)
    cur = conn.cursor()
    cur.execute('SELECT Question,Answer1,Answer2,Answer3,CorrectAnswer FROM Trivia WHERE TriviaId = ' + str(id))
    return cur.fetchone()    
    
random.seed()
conn = CreateConnection('trivia.db')
countQuestions = CountQuestions(conn)

while(1):
    question = GetQuestion(conn, countQuestions)
    print(question[0])
    print('1) ' + question[1])
    print('2) ' + question[2])
    print('3) ' + question[3])
    choice = input('? ')
    if(choice == 'q' or choice == 'quit' or choice == 'exit'):
        sys.exit()
    if(int(choice) == question[4]):
        print('Correct')
    else:
        print('Wrong')
    print()
