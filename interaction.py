#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import time
import math

import readchar

import psutil
import os
import signal

import sys

try:
    from msvcrt import getch  # try to import Windows version
except ImportError:
    def getchar(): # define non-Windows version
        # Returns a single character from standard input
        import tty, termios, sys
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def blink(leds_service):
    #blink
    hexColour = int('0x00%02x%02x%02x' % (255, 255, 0), 0)
    leds_service.fadeRGB("ChestLeds", hexColour, 10)

    return

def interaction(motion_service, speech_service):
    #start the interaction
    # look at both
    # talk

    # go to an init head pose.
    names = ["HeadPitch", "HeadYaw"]
    angleLists = [0., 0.]
    times = [1.0, 1.0]
    isAbsolute = True
    motion_service.angleInterpolation(names, angleLists, times, isAbsolute)

    time.sleep(0.5)

    # move slowly the head to look in the left direction
    angleLists = [-0.25, 0.45]
    fractionMaxSpeed = 0.1
    motion_service.setAngles(names, angleLists, fractionMaxSpeed)

    # rotate slightly on left
    turn(motion_service, 0, 0, 0.3, 0.1)

    speech_service.say("Excuse me, I would like to pass.")

    # while the previous motion is still running, update the angle
    angleLists = [-0.25, -0.25]
    motion_service.setAngles(names, angleLists, fractionMaxSpeed)

    # rotate slightly on right
    turn(motion_service, 0, 0, -0.1, 0.1)

    time.sleep(1.0)

    angleLists = [0., 0.]
    motion_service.angleInterpolation(names, angleLists, times, isAbsolute)

    time.sleep(2.0)

    speech_service.say("Thank you!")

    return

def gesture(motion_service):
    #move arm on right

    yaw = -0.420290
    pitch =  0.797101
    roll =  1
    bent =  0.478261
    rwrist = 1.

    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
    angleLists = [pitch, yaw, roll, bent, rwrist]
    times = [1.0, 1.0, 1.0, 1.0, 1.0]
    isAbsolute = True
    motion_service.angleInterpolation(names, angleLists, times, isAbsolute)

    time.sleep(1.0)

    # move right arm back in position
    yaw = -0.159420
    pitch = 1.365217
    roll = 0.717391
    bent = 0.304348
    rwrist = 0.536232
    angleLists = [pitch, yaw, roll, bent, rwrist]
    motion_service.angleInterpolation(names, angleLists, times, isAbsolute)

    return

def move(motion_service, x, y, z, vel, acc):
    motion_service.killMove()
    motion_service.moveToward(x, y, z, [["MaxVelXY", vel], ["MaxAccXY", acc]])
    return

def turn(motion_service, x, y, z, vel):
    motion_service.killMove()
    motion_service.moveTo(x, y, z, vel)
    return


def main(session):
    memory_service = session.service("ALMemory")
    motion_service = session.service("ALMotion")

    speech_service = session.service("ALTextToSpeech")

    leds_service = session.service("ALLeds")

    posture_service = session.service("ALRobotPosture")

   # Send robot to Stand Init
    posture_service.goToPosture("Stand", 0.5)

    tablet_service = session.service("ALTabletService")

    # use the arrows for moving
        # up arrow -> go forward
        # down arrow -> go backward
        # right arrow -> turn right
        # left arrow -> turn left
        # s -> stop
    # use the arrows combined with other keyboard char for change the velocity
        # a -> accelerate
        # d -> decrease acceleration

    dir = -1

    vel = 0.1
    acc = 0.1

    while True:
        ch = readchar.readkey()

        if ch == 'q': # pressed key "q"  - exit
            print('bye!')
            motion_service.killMove()
            posture_service.goToPosture("Stand", 0.5)
            break

        # NAVIGATION
        elif ch == readchar.key.UP: #pressed key arrow up - move forward
            dir = 1
            move(motion_service, 1, 0, 0, vel, acc)

        elif ch == readchar.key.DOWN: #pressed key arrow down - move backward
            dir = 2

            move(motion_service, -1, 0, 0, vel, acc)

        elif ch == readchar.key.RIGHT: #pressed key arrow right - rotate right

            if dir == 1:
                move(motion_service, 1, 0, -vel, vel, acc)
            else:
                move(motion_service, -1, 0, -vel, vel, acc)
        elif ch == readchar.key.LEFT: #pressed key arrow left - rotate left
            if dir == 1:
                move(motion_service, 1, 0, vel, vel, acc)
            else:
                move(motion_service, -1, 0, vel, vel, acc)

        elif ch == 'a' or ch == 'd':
            if ch == 'a':
                vel += 0.1
                acc += 0.1
            else:
                vel -= 0.1
                acc -= 0.1
            if dir == 1:
                move(motion_service, 1, 0, 0, vel, acc)
            if dir == 2:
                move(motion_service, -1, 0, 0, vel, acc)

        elif ch == 's':
            motion_service.killMove()

        # SOCIAL NAVIGATION STUDY

        elif ch == 'b': #pressed key b - blink leds
            blink(leds_service)
        elif ch == 't': #pressed key t - start interaction with people-obstacles
            interaction(motion_service,speech_service)
        elif ch == 'g': #pressed key g - make gesture
            gesture(motion_service)

        # GENERIC USUFUL COMMANDS

        elif ch == 'p': #pressed key p - go in rest position
            posture_service.goToPosture("Stand", 0.5)

        elif ch == 'h': #pressed key h - help menu
            menu(speech_service,tablet_service)

def menu(speech_service,tablet_service):
    speech_service.say("Using yoru keyboard, you can command me to do several things.")
    speech_service.say("Here it is the list of all things that you can make me do:")
    speech_service.say("Use the keyboard arrows for moving me around, I can go forward, backward and turn left and right")
    speech_service.say("Use the keyboard key a for increasing the velocity of my navigation")
    speech_service.say("Use the keyboard key d for decreasing the velocity of my navigation")
    speech_service.say("Use the keyboard key s for stopping my navigation")
    speech_service.say("Use the keyboard key g for moving my right arm")
    speech_service.say("Use the keyboard key t for startign the interaction")
    speech_service.say("Use the keyboard key b for changing the colour of my shoulder")
    speech_service.say("Use the keyboard key p for letting me assume my basic stand position")
    speech_service.say("Use the keyboard key q to exit")
    speech_service.say("Use the keyboard key h for this menu")

    tablet_service.showImage("heart.png")

    time.sleep(3)

    # Hide the web view
    tablet_service.hideImage()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.0.204.249",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)




