import pygame
from gl import *
from BMP_Writer import GenerateBMP
from model import Model
from shaders import *

width = 720
height = 720

screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("Rasterizer 2025 - Modelo 3D OBJ")
clock = pygame.time.Clock()

rend = Renderer(screen)

# Cargar modelo desde archivo .obj
objModel = Model()
objModel.load_obj("prueba.obj")
objModel.scale_to_fit(width, height)  # Escalar automáticamente
objModel.vertexShader = vertexShader

rend.models.append(objModel)

isRunning = True
while isRunning:
    deltaTime = clock.tick(60)/ 1000.0

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

    # Controles de movimiento
    if keys[pygame.K_RIGHT]:
        objModel.translation[0] += 50 * deltaTime
    if keys[pygame.K_LEFT]:
        objModel.translation[0] -= 50 * deltaTime
    if keys[pygame.K_UP]:
        objModel.translation[1] += 50 * deltaTime
    if keys[pygame.K_DOWN]:
        objModel.translation[1] -= 50 * deltaTime

    # Controles de rotación
    if keys[pygame.K_d]:
        objModel.rotation[2] += 45 * deltaTime
    if keys[pygame.K_a]:
        objModel.rotation[2] -= 45 * deltaTime
    if keys[pygame.K_q]:
        objModel.rotation[1] += 45 * deltaTime
    if keys[pygame.K_e]:
        objModel.rotation[1] -= 45 * deltaTime

    # Controles de escala
    if keys[pygame.K_w]:
        objModel.scale = [i * (1 + deltaTime) for i in objModel.scale]
    if keys[pygame.K_s]:
        objModel.scale = [i * (1 - deltaTime) for i in objModel.scale]

    # Renderizar
    rend.glClear()
    rend.glRender()

    pygame.display.flip()

# Exportar imagen final
GenerateBMP("output.bmp", width, height, 3, rend.frameBuffer)
print("Imagen exportada como output.bmp")

pygame.quit()
