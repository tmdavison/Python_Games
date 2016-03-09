#!/usr/bin/env python

#########
# 2016 Copyright (C) James Derrick
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# ### ABOUT THE GAME ###
#
# NB This is written for python 2.7!
#
# This is a simple recreation of the popular slime volleyball game, which
# can be found here: http://slimegames.eu/ . However, none of the same code
# was used and everything was reverse engineered from the memories of 
# hours of fun I had as a kid! This version is in python.
#
# I also used Simon Mouradian's pong game as a template to build this.
# Simon's game can be found here: https://github.com/slmouradian/pong
# Also on github.
#
# ### HOW TO PLAY ###
# -----------------------------------
# ACTION   | LEFT SLIME | RIGHT SLIME|
# -----------------------------------
# JUMP     |     W      |      I     |
# MV LEFT  |     A      |      J     |
# MV RIGHT |     D      |      L     |
# -----------------------------------
#
# As in tennis you are allowed one bounce of the ball in your 'court' (half)
# after this, if the ball touches the floor of your court, your opponent scores
# a point and vice versa. The net is mainly cosmetic at this stage, and simply
# divides the courts.
#
# Please enjoy! 
#########

from Tkinter import *
import numpy as np
import string
import random

sounds_enabled = False
try:
    from pygame import mixer
    sounds_enabled = True
except:
    pass

WIDTH = 900
HEIGHT = 500
BALL_RADIUS = 14
BALL_R = BALL_RADIUS
SLIME_R = 40
BALL_MASS = 25
SLIME_MASS = 50

LEFT = False
RIGHT = True

LINE_COLOUR='black'
BALL_COLOUR='black'
SLIME1_COLOUR='blue'
SLIME2_COLOUR='red'
slime_acc = 8

def ball_bbox(ball_pos):
    return ball_pos[0]-BALL_RADIUS, ball_pos[1]-BALL_RADIUS, ball_pos[0]+BALL_RADIUS, ball_pos[1]+BALL_RADIUS

def reset_ball(direction):
    global ball, ball_pos, ball_vel,slime1_vel,slime2_vel,slime1,slime2,m1,m2,BOUNCE_L,BOUNCE_R
    if direction==RIGHT:
        ball_pos = [3.*WIDTH/4., HEIGHT/2]
        canvas.coords(ball, ball_bbox(ball_pos))
    else:
        ball_pos = [WIDTH/4., HEIGHT/2]
        canvas.coords(ball, ball_bbox(ball_pos))
    m1 = SLIME_MASS
    m2 = BALL_MASS
    canvas.coords(slime1,WIDTH/4.-SLIME_R,HEIGHT-SLIME_R,WIDTH/4.+SLIME_R,HEIGHT+SLIME_R)
    canvas.coords(slime2,3.*WIDTH/4.-SLIME_R,HEIGHT-SLIME_R,3.*WIDTH/4.+SLIME_R,HEIGHT+SLIME_R)
    slime1_vel = [0.,0,]
    slime2_vel = [0.,0,]
    ball_vel = [0,0]
    BOUNCE_L = False
    BOUNCE_R = False

def draw_movable_items():
    global ball, ball_pos, slime1, slime2
    ball_pos   = [WIDTH/2., HEIGHT/2.]
    ball       = canvas.create_oval(ball_bbox(ball_pos),fill=BALL_COLOUR)
    slime1     = canvas.create_arc((WIDTH/4.)-SLIME_R,HEIGHT-SLIME_R,(WIDTH/4.)+SLIME_R,HEIGHT+SLIME_R, \
                                          fill=SLIME1_COLOUR,extent=180)
    slime2     = canvas.create_arc((WIDTH/4.)-SLIME_R+WIDTH,HEIGHT-SLIME_R,(WIDTH/4.)+SLIME_R+WIDTH,HEIGHT+SLIME_R, \
                                          fill=SLIME2_COLOUR,extent=180)
def new_game():
    global slime1_vel, slime2_vel
    global score1, score2, score1_label, score2_label
    if sounds_enabled:
        new_game_sound.play()
    slime1_vel = [0.,0.]
    slime2_vel = [0.,0.]
    score1 = 0
    canvas.itemconfigure(score1_label,text=str(score1))
    score2 = 0
    canvas.itemconfigure(score2_label,text=str(score2))
    reset_ball(RIGHT)

def find_centre(coords):
	x0 = coords[0]
	y0 = coords[1]
	x1 = coords[2]
	y1 = coords[3]
	x = (x0 + x1)/2.
	y = (y0 + y1)/2.
	return x,y

def collision(v1,x1,m1,v2,x2,m2):   
	v1 = np.array(v1)
	x1 = np.array(x1)
	v2 = np.array(v2)
	x2 = np.array(x2)
	newv1 = v1-((2.*m2/(m2+m1))*np.dot((v1-v2),(x1-x2))/np.linalg.norm(x1-x2)**2.)*(x1-x2)
	newv2 = v2-((2.*m1/(m1+m2))*np.dot((v2-v1),(x2-x1))/np.linalg.norm(x2-x1)**2.)*(x2-x1)
	newv1 = v1-((2.*m2/(m2+m1))*np.dot((v1-v2),(x1-x2))/np.linalg.norm(x1-x2)**2.)*(x1-x2)
	newv2 = v2-((2.*m1/(m1+m2))*np.dot((v2-v1),(x2-x1))/np.linalg.norm(x2-x1)**2.)*(x2-x1)
	
	return newv1,newv2
	


def dynamics():
	global score1,score2,ball_pos, ball_vel,slime1_vel,slime2_vel,m1,m2,collide,jump1,jump2,BOUNCE_L,BOUNCE_R
	bx,by      = find_centre(canvas.coords(ball))
	s1x,s1y    = find_centre(canvas.coords(slime1))
	s2x,s2y    = find_centre(canvas.coords(slime2))
	
	
	#jump1 = False
	#jump2 = False
	
	if s1y < HEIGHT: 
		jump1 = True
	else:
		jump1 = False
	if s2y < HEIGHT: 
		jump2 = True
	else:
		jump2 = False
	
	vec1        = np.array([bx-s1x,by-s1y])
	mag1        = np.sqrt(vec1[0]**2. + vec1[1]**2.)
	vec2        = np.array([bx-s2x,by-s2y])
	mag2        = np.sqrt(vec2[0]**2. + vec2[1]**2.)
	if (mag1 >= (SLIME_R+BALL_R)) and (mag2>=(SLIME_R+BALL_R)): collide = False
	
	canvas.move(slime1,slime1_vel[0],slime1_vel[1])
	canvas.move(slime2,slime2_vel[0],slime2_vel[1])
	canvas.move(ball,ball_vel[0],ball_vel[1])
	
	if canvas.coords(slime1)[3]>HEIGHT+SLIME_R:
		x0 = canvas.coords(slime1)[0]
		x1 = canvas.coords(slime1)[2]
		canvas.coords(slime1,x0,HEIGHT-SLIME_R,x1,HEIGHT+SLIME_R)
		slime1_vel[1] = 0.
	if canvas.coords(slime2)[3]>HEIGHT+SLIME_R:
		x0 = canvas.coords(slime2)[0]
		x1 = canvas.coords(slime2)[2]
		canvas.coords(slime2,x0,HEIGHT-SLIME_R,x1,HEIGHT+SLIME_R)
		slime2_vel[1] = 0.
	if jump1 and canvas.coords(slime1)[3]<(HEIGHT+SLIME_R): slime1_vel[1] += 10.*10.e-3
	if jump2 and canvas.coords(slime2)[3]<(HEIGHT+SLIME_R): slime2_vel[1] += 10.*10.e-3 
	
		
	if canvas.coords(slime1)[0]<=0:
		y0 = canvas.coords(slime1)[1]
		y1 = canvas.coords(slime1)[3]
		canvas.coords(slime1,0,y0,2*SLIME_R,y1)
		slime1_vel[0] = 0
	elif canvas.coords(slime1)[2]>=WIDTH/2.:
		y0 = canvas.coords(slime1)[1]
	 	y1 = canvas.coords(slime1)[3]
		canvas.coords(slime1,WIDTH/2. - 2*SLIME_R,y0,WIDTH/2.,y1)
		slime1_vel[0] = 0
	
	if canvas.coords(slime2)[0]<=WIDTH/2.:
		y0 = canvas.coords(slime2)[1]
		y1 = canvas.coords(slime2)[3]
		canvas.coords(slime2,WIDTH/2.,y0,WIDTH/2.+2*SLIME_R,y1)
		slime2_vel[0] = 0
	elif canvas.coords(slime2)[2]>=WIDTH:
		y0 = canvas.coords(slime2)[1]
		y1 = canvas.coords(slime2)[3]
		canvas.coords(slime2,WIDTH - 2*SLIME_R,y0,WIDTH,y1)
		slime2_vel[0] = 0
	else:
		pass
	#if canvas.coords(ball)[1] <= 0:
		#ball_vel[1] = -0.9*ball_vel[1]
	
	if collide == False:
		if (canvas.coords(ball)[2]<=(WIDTH/2.)):
			BOUNCE_R   = False
			bx,by      = find_centre(canvas.coords(ball))
			sx,sy      = find_centre(canvas.coords(slime1))
			vec        = np.array([bx-sx,by-sy])
			mag        = np.sqrt(vec[0]**2. + vec[1]**2.)
			if mag <= (SLIME_R+BALL_R):
				collide = True
				bX = np.array([bx,by])
				sX = np.array([sx,sy])
				slime1_vel,ball_vel = collision(slime1_vel,sX,m1,ball_vel,bX,m2)
				#if sy >= HEIGHT: slime1_vel[1] = 0.
			else:
				pass
			if (canvas.coords(ball)[3]>=HEIGHT) and BOUNCE_L:
				reset_ball(RIGHT)
				score2 += 1
				BOUNCE_L = False
				canvas.itemconfigure(score2_label,text=str(score2))
			if (canvas.coords(ball)[3]>=HEIGHT):
				BOUNCE_L = True
				ball_vel[1] = -.9*ball_vel[1]
			if (canvas.coords(ball)[3]>=(HEIGHT-1.5*SLIME_R) and canvas.coords(ball)[0]==WIDTH/2.):
				reset_ball(RIGHT)
				score2 += 1
				canvas.itemconfigure(score2_label,text=str(score2))
		elif (canvas.coords(ball)[0]>= WIDTH/2.):
			BOUNCE_L = False
			bx,by   = find_centre(canvas.coords(ball))
			sx,sy   = find_centre(canvas.coords(slime2))
			vec        = np.array([bx-sx,by-sy])
			mag        = np.sqrt(vec[0]**2. + vec[1]**2.)
			if mag <= (SLIME_R+BALL_R):
				collide = True
				bX = np.array([bx,by])
				sX = np.array([sx,sy])
				slime2_vel,ball_vel = collision(slime2_vel,sX,m1,ball_vel,bX,m2)
			else:
			    pass
			if (canvas.coords(ball)[3]>=HEIGHT) and BOUNCE_R:
				reset_ball(LEFT)
				score1 += 1
				BOUNCE_R = False
				canvas.itemconfigure(score1_label,text=str(score1))
			if (canvas.coords(ball)[3]>=HEIGHT):
				BOUNCE_R = True
				ball_vel[1] = -.9*ball_vel[1]
			if (canvas.coords(ball)[3]>=(HEIGHT-1.5*SLIME_R) and canvas.coords(ball)[0]==WIDTH/2.):
				reset_ball(LEFT)
				score1 += 1
				canvas.itemconfigure(score1_label,text=str(score1))
	if collide:
		pass
	else:
		ball_vel[1]   += 10.*10.e-3
        
        

	if canvas.coords(ball)[2] >= WIDTH:
	    ball_vel[0] = -0.9*ball_vel[0]

	if canvas.coords(ball)[0] <= 0:
	    ball_vel[0] = -0.9*ball_vel[0]

	canvas.after(10,dynamics)


def KeyPressed(event):
    global slime1_vel, slime2_vel,jump1,jump2
    if event.char == 'a':
        slime1_vel[0] = -1.*slime_acc
    elif event.char == 'd':
        slime1_vel[0] = slime_acc
    elif event.char == 'j':
        slime2_vel[0] = -1.*slime_acc
    elif event.char == 'l':
        slime2_vel[0] = slime_acc
    elif event.char == 'w':
        if jump1 == False: 
            slime1_vel[1] = -1.*slime_acc/2.
        else:
            pass
    elif event.char == 'i':
        if jump2 == False: 
           slime2_vel[1] = -1.*slime_acc/2.
        else:
           pass

def KeyReleased(event):
    global slime1_vel, slime2_vel,jump1,jump2
    if event.char == 'a':
        slime1_vel[0] = 0.
    elif event.char == 'd':
        slime1_vel[0] = 0.
    elif event.char == 'j':
        slime2_vel[0] = 0.
    elif event.char == 'l':
        slime2_vel[0] = 0.
    elif event.char == 'w':
        pass
    elif event.char == 'i':
        pass

def draw_scores():
    global score1_label, score2_label
    score1_label = canvas.create_text((WIDTH/2)-40, 40, text='0',\
                                          font=('TkDefaultFont',40),\
                                          fill=LINE_COLOUR)
    score2_label = canvas.create_text((WIDTH/2)+40, 40, text='0',\
                                          font=('TkDefaultFont',40),\
                                          fill=LINE_COLOUR)


# Create master frame and drawing canvas.
frame = Tk()
frame.title('Slime Tennis')
canvas = Canvas(frame, width=WIDTH, height=HEIGHT, bg='white')
canvas.pack()

# Draw the net
canvas.create_line(WIDTH/2, HEIGHT-1.5*SLIME_R, WIDTH/2, HEIGHT, fill=LINE_COLOUR)
#canvas.create_line(PAD_WIDTH,0, PAD_WIDTH,HEIGHT, fill=LINE_COLOUR)
#canvas.create_line(WIDTH-PAD_WIDTH,0, WIDTH-PAD_WIDTH,HEIGHT, fill=LINE_COLOUR)

# Register key event handlers
frame.bind('<Key>', KeyPressed)
frame.bind('<KeyRelease>', KeyReleased)

# Draw the ball and slimes
draw_movable_items()

resetButton = Button(frame, text ="Reset", command = new_game)
resetButton.pack()

if sounds_enabled:
    load_sounds()
draw_scores()
new_game()

dynamics()
frame.mainloop()
