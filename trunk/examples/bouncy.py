"""Bouncy Bouncy

Demos how to use domains to position pariticles and redirect them
using the Bounce controller.
"""

__version__ = '$Id$'

from pyglet import image
from pyglet.gl import *
import sys
sys.path.append('../..')

from particle import Particle, ParticleGroup, default_system
from particle.renderer import PointRenderer
from particle.emitter import StaticEmitter
from particle.controller import Movement, Bounce, Gravity
from particle.domain import Box, Sphere

if __name__ == '__main__':
	"""This file is meant to show how to use controller, renderer, system, particle, group to implement
	the effect in pyparticle.py"""
	win = pyglet.window.Window(resizable=True, visible=False)


	def resize(widthWindow, heightWindow):
		"""Initial settings for the OpenGL state machine, clear color, window size, etc"""
		glEnable(GL_BLEND)
		glEnable(GL_POINT_SMOOTH)
		glShadeModel(GL_SMOOTH)# Enables Smooth Shading
		glBlendFunc(GL_SRC_ALPHA,GL_ONE)#Type Of Blending To Perform
		glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST);#Really Nice Perspective Calculations
		glHint(GL_POINT_SMOOTH_HINT,GL_NICEST);#Really Nice Point Smoothing
		glDisable(GL_DEPTH_TEST)
	
	ball_count = 100
	ball_size = 15
	bumper_count = 8

	# Screen domain is a box the size of the screen
	screen_domain = Box((ball_size/2.0, ball_size/2.0, 0), 
		(win.width-ball_size/2.0,win.height-ball_size/2.0,0))


	def set_bumper_color(particle, group, bumper, collision_point, collision_normal):
		"""Set bumper color to the color of the particle that collided with it"""
		bumper.color = tuple(particle.color)[:3]

	bumpers = []
	for i in range(bumper_count):
		sphere = Sphere(
			(win.width/(bumper_count-1) * i, win.height*2.0/3.0 - (i % 2) * win.height/3, 0), 
			radius=win.height / 15)
		bumper = Bounce(sphere, friction=-0.5, callback=set_bumper_color)
		bumper.color = (1,0,0)
		bumpers.append(bumper)

	default_system.add_global_controller(
		Gravity((0,-50,0)),
		Movement(max_velocity=200), 
		Bounce(screen_domain, friction=0.01),
		*bumpers
	)
	group = ParticleGroup(renderer=PointRenderer(point_size=ball_size))

	ball_emitter = StaticEmitter(
		# The rate and expire time are setup for a burst all at once
		position=screen_domain,
		deviation=Particle(velocity=(60,60,0), color=(0.3,0.3,0.3,0)),
		color=[(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1), (0,1,1,1), (1,1,1,1)],
	)
	ball_emitter.emit(ball_count, group)
	group.update(0)
	# Kill particles inside the bumpers
	for p in group:
		for bumper in bumpers:
			if p.position in bumper.domain:
				group.kill(p)

	win.resize = resize
	win.set_visible(True)
	win.resize(win.width, win.height)
	pyglet.clock.schedule_interval(default_system.update, (1.0/30.0))

	def draw_bumpers():
		glPointSize(bumpers[0].domain.radius * 2 - ball_size/2.0 - 15)
		glColor3f(1.0, 1.0, 0)
		glBegin(GL_POINTS)
		for bumper in bumpers:
			cx, cy, cz = bumper.domain.center_point
			glVertex3f(cx, cy, cz)
		glEnd()
		glPointSize(bumpers[0].domain.radius * 2 - ball_size/2.0)
		glBegin(GL_POINTS)
		for bumper in bumpers:
			cx, cy, cz = bumper.domain.center_point
			glColor3f(*bumper.color)
			glVertex3f(cx, cy, cz)
		glEnd()

	@win.event
	def on_draw():
		global i
		win.clear()
		glLoadIdentity()
		draw_bumpers()
		default_system.draw()

	pyglet.app.run()