# Program: client.py
# Author: Joel Ristvedt

#IMPORTS
from OpenGL import GL, GLU, GLUT
from sdl2 import *
import sys
import ctypes

def run():
	if SDL_Init(SDL_INIT_VIDEO) != 0:
		print(SDL_GetError())
		return -1

	window = SDL_CreateWindow(b"OpenGL Test",
							  SDL_WINDOWPOS_UNDEFINED,
							  SDL_WINDOWPOS_UNDEFINED, 800, 600,
							  SDL_WINDOW_OPENGL)
	
	if not window:
		print(SDL_GetError())
		return -1

	SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
	SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,
    					SDL_GL_CONTEXT_PROFILE_CORE)
	context = SDL_GL_CreateContext(window)

	event = SDL_Event()
	running = True
	while running:
		while SDL_PollEvent(ctypes.byref(event)) != 0:
			if event.type == SDL_QUIT:
				running = False

		GL.glClearColor(1, 1, 0, 1)
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		GL.glColor3f(0, 1, 1)
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GLU.gluOrtho2D(0, 800, 0, 600)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		
		GL.glPushMatrix()
		GL.glTranslatef(25, 25, 0)
		GLUT.glutWireSphere(25, 1000, 10)
		#GL.glBegin(GL.GL_LINES)
		#GL.glVertex2i(0, 0)
		#GL.glVertex2i(0, 50)
		#GL.glEnd()
		GL.glPopMatrix()
		GL.glFlush()


		SDL_GL_SwapWindow(window)
		SDL_Delay(10)

	SDL_GL_DeleteContext(context)
	SDL_DestroyWindow(window)
	SDL_Quit()
	return 0

if __name__ == "__main__":
	sys.exit(run())