import pygame 
from gl import Renderer  

width = 960 
height = 540
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rasterizer 2025 - Polígono")
clock = pygame.time.Clock()

# Crear instancia del renderer
render = Renderer(screen)

#definir el poligono 
polygon = [
    (165, 380), (185, 360), (180, 330), (207, 345),
    (233, 330), (230, 360), (250, 380), (220, 385),
    (205, 410), (193, 383)
]
isRUNNING = True

while isRUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRUNNING = False

    #para limpiar la pantalla
    render.glClear()
    
    #para establecer el color de fondo
    render.glColor(1,0,0)
    render.glFillPolygon(polygon)
    
    #para dibujar el poligono
    render.glColor(1, 1, 1)
    render.glDrawPolygon(polygon)
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
exit(0)