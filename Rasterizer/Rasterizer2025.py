import pygame
from gl import *
from BMP_Writer import GenerateBMP
from model import Model
from shaders import *

width = 256
height = 256

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

# triangle3 = [[510,70], [550, 160], [570,80] ]

triangleModel = Model()
triangleModel.vertices = [ 110,  70, 0,
						   150, 160, 0,
						   170,  80, 0 ]

triangleModel.vertexShader = vertexShader

rend.models.append(triangleModel)


isRunning = True
while isRunning:

	deltaTime = clock.tick(60) / 1000.0


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_1:
				rend.primitiveType = POINTS

			elif event.key == pygame.K_2:
				rend.primitiveType = LINES

			elif event.key == pygame.K_3:
				rend.primitiveType = TRIANGLES



	keys = pygame.key.get_pressed()

	if keys[pygame.K_RIGHT]:
		triangleModel.translation[0] += 10 * deltaTime
	if keys[pygame.K_LEFT]:
		triangleModel.translation[0] -= 10 * deltaTime
	if keys[pygame.K_UP]:
		triangleModel.translation[1] += 10 * deltaTime
	if keys[pygame.K_DOWN]:
		triangleModel.translation[1] -= 10 * deltaTime


	if keys[pygame.K_d]:
		triangleModel.rotation[2] += 20 * deltaTime
	if keys[pygame.K_a]:
		triangleModel.rotation[2] -= 20 * deltaTime

	if keys[pygame.K_w]:
		triangleModel.scale =  [(i + deltaTime) for i in triangleModel.scale]
	if keys[pygame.K_s]:
		triangleModel.scale = [(i - deltaTime) for i in triangleModel.scale ]










		rend.glClear()

		# Escribir lo que se va a dibujar aqui
		rend.glPoint(100,100,(255,0,0))  # ← Corregir indentación aquí
		rend.glPoint(150,150,(0,255,0))
	
		#Dibujar una linea. 
		rend.glLine([50, 50], [200, 200], (0, 0, 255))  
		rend.glLine([200, 50], [50, 200], (255, 255, 0)) 

		rend.glRender()

	#########################################

	pygame.display.flip()


GenerateBMP("output.bmp", width, height, 3, rend.frameBuffer)

pygame.quit()
