import pygame
import random
import sqlite3
from sqlite3 import Error
import os
import time
import sys
import textutil
import RPi.GPIO as GPIO

# Globals
buttonPending = False # is there a button push to process?
buttonPressed = 0
BUTTON_1 = 21
BUTTON_2 = 20
BUTTON_3 = 16

def button_press(channel):
    global buttonPending
    global buttonPressed

    if buttonPending == False:
        buttonPending = True
        buttonPressed = channel

    print 'buttonPressed is ' + str(buttonPressed)

def clear_button():
    global buttonPending
    global buttonPressed

    buttonPending = False
    buttonPressed = 0
    print 'pending button cleared'

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #GPIO.add_event_detect(BUTTON_1, GPIO.BOTH, callback=button_press, bouncetime=300) 
    #GPIO.add_event_detect(BUTTON_2, GPIO.BOTH, callback=button_press, bouncetime=300)
    #GPIO.add_event_detect(BUTTON_3, GPIO.BOTH, callback=button_press, bouncetime=300)

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
    mode = "new_question"

    random.seed()
    conn = create_connection('trivia.db')
    countQuestions = count_questions(conn)

    pygame.init()
    #screen = pygame.display.set_mode((800, 480))
    screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    
    gpio_init()
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)
    statusFont = pygame.font.Font(None, 200)
    questionRect = pygame.Rect((5, 5, 795, 200))
    questionColor = (226, 226, 226)
    answersRect = pygame.Rect((5, 320, 795, 200))
    answersColor = (226, 226, 226)

    correctText = statusFont.render("CORRECT", 1, (0, 232, 23))
    wrongText = statusFont.render("WRONG", 1, (232, 0, 23))
    helperText = font.render("Press button to try again", 1, questionColor)
    
    buttonUp = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))

        if mode == "new_question":
            question = get_question(conn, countQuestions)
            renderedQuestion = textutil.render_textrect(question[0], font, questionRect, questionColor, (0, 0, 0), 0)
            answersText = "1) " + question[1] + "\n"
            answersText += "2) " + question[2] + "\n"
            answersText += "3) " + question[3] + "\n"
            renderedAnswers = textutil.render_textrect(answersText, font, answersRect, answersColor, (0, 0, 0), 0)
            mode = "question"

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        
        answer = 0
        if GPIO.input(BUTTON_1) == GPIO.LOW or pressed[pygame.K_1]: answer = 1
        if GPIO.input(BUTTON_2) == GPIO.LOW or pressed[pygame.K_2]: answer = 2
        if GPIO.input(BUTTON_3) == GPIO.LOW or pressed[pygame.K_3]: answer = 3
        if answer == 0: buttonUp = True

        # only take action on button press if buttons have been up
        if buttonUp:
            if mode == "question" and answer > 0:
                if question[4] == answer:
                    mode = "correct"
                else:
                    mode = "wrong"
                buttonUp = False
            elif answer > 0:
                mode = "new_question"
                buttonUp = False

        if mode == "question":
            screen.blit(renderedQuestion, questionRect.topleft)
            screen.blit(renderedAnswers, answersRect.topleft)
        elif mode == "correct":
            screen.blit(correctText, (400 - correctText.get_width() // 2, 240 - correctText.get_height() // 2))
            screen.blit(helperText, (400 - helperText.get_width() //2, 420))
        elif mode == "wrong":
            screen.blit(wrongText, (400 - wrongText.get_width() // 2, 240 - wrongText.get_height() // 2))
            screen.blit(helperText, (400 - helperText.get_width() //2, 420))

        #debug blitting
        #screen.blit(font.render(mode, 1, (255,255,255)), (600, 430))

        pygame.display.flip()

        clock.tick(60)
