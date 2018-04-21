import pygame
import random
import sqlite3
from sqlite3 import Error
import os
import time
import textutil

def create_connection(dbFile):
    try:
        conn = sqlite3.connect(dbFile)
        return conn
    except Error as e:
        print(e)
    return None


def count_questions(conn):
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM Trivia')

    return cur.fetchone()[0]

def get_question(conn, countQuestions):
    id = random.randrange(1, countQuestions)
    cur = conn.cursor()
    cur.execute('SELECT Question,Answer1,Answer2,Answer3,CorrectAnswer FROM Trivia WHERE TriviaId = ' + str(id))
    return cur.fetchone()

if __name__ == '__main__':
    mode = "question"

    random.seed()
    conn = create_connection('trivia.db')
    countQuestions = count_questions(conn)

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    done = False
    frameWait = 0 # start at 0 to get first question

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    statusFont = pygame.font.Font(None, 100)
    questionRect = pygame.Rect((5, 5, 500, 200))
    questionColor = (216, 216, 216)
    answersRect = pygame.Rect((5, 205, 500, 200))
    answersColor = (216, 216, 216)

    correctText = statusFont.render("CORRECT", 1, (0, 232, 23))
    wrongText = statusFont.render("WRONG", 1, (232, 0, 23))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # when frameWait ends, start new question
        if frameWait == 0:
            question = get_question(conn, countQuestions)
            renderedQuestion = textutil.render_textrect(question[0], font, questionRect, questionColor, (0, 0, 0), 0)
            answersText = "1) " + question[1] + "\n"
            answersText += "2) " + question[2] + "\n"
            answersText += "3) " + question[3] + "\n"
            renderedAnswers = textutil.render_textrect(answersText, font, answersRect, answersColor, (0, 0, 0), 0)
            mode = "question"
            frameWait = -1

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]: done = True
        if frameWait <= 0:
            answer = 0
            if pressed[pygame.K_1]: answer = 1
            if pressed[pygame.K_2]: answer = 2
            if pressed[pygame.K_3]: answer = 3
            if mode == "question" and answer > 0:
                if question[4] == answer:
                    mode = "correct"
                else:
                    mode = "wrong"
                frameWait = 240

        screen.fill((0, 0, 0))

        if mode == "question":
            screen.blit(renderedQuestion, questionRect.topleft)
            screen.blit(renderedAnswers, answersRect.topleft)
        elif mode == "correct":
            screen.blit(correctText, (200 - correctText.get_width() // 2, 200 - correctText.get_height() // 2))
        elif mode == "wrong":
            screen.blit(wrongText, (200 - wrongText.get_width() // 2, 200 - wrongText.get_height() // 2))

        pygame.display.flip()

        if frameWait > 0:
            frameWait -= 1

        clock.tick(60)
