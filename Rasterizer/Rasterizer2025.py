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

polygon_2 = [(321, 335),(288, 286),(339, 251) ,(374, 302)]

polygon_3 = [(377, 249) ,(411, 197) ,(436, 249)]


polygon_4 = [
    (413, 177), (448, 159), (502, 88), (553, 53), (535, 36), (676, 37), (660, 52),
    (750, 145), (761, 179), (672, 192), (659, 214), (615, 214), (632, 230), (580, 230),
    (597, 215), (552, 214), (517, 144), (466, 180)
]

polygon_5 = [(682, 175), (708, 120), (735, 148), (739, 170)]


isRUNNING = True

while isRUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRUNNING = False

    #para limpiar la pantalla
    render.glClear()
    
    #para establecer el color de fondo
    render.glColor(1,1,0)
    render.glFillPolygon(polygon)
    
    #para dibujar el poligono
    render.glColor(1, 1, 1)
    render.glDrawPolygon(polygon)
    
    # 2do: dibujar el poligono 2
    render.glColor(0.5, 0, 0.5)  # Cambiar color a
    render.glFillPolygon(polygon_2)
    render.glColor(1, 1, 1)  # Cambiar color a
    render.glDrawPolygon(polygon_2)
    
    # 3ro: dibujar el poligono 3
    render.glColor(0, 0, 1)  # Cambiar color a
    render.glFillPolygon(polygon_3)
    render.glColor(1, 1, 1)  # Cambiar color a
    render.glDrawPolygon(polygon_3)
    
    
    # 4to: dibujar el poligono 4
    render.glColor(0.6,0.4, 0.2)  # Cambiar color a verde
    render.glFillPolygon(polygon_4)
    render.glColor(1, 1, 1)  # Cambiar color a blanco
    render.glDrawPolygon(polygon_4)
    
    # 5to: dibujar el poligono 5
    render.glColor(1, 1, 1)  
    render.glFillPolygon(polygon_5)
    render.glColor(1, 1, 1) 
    render.glDrawPolygon(polygon_5)

    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
exit(0)