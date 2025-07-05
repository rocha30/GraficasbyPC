import pygame 
from gl import Renderer
width = int(1920/2) 
height = int(1080/2)
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
rend = Renderer(screen)
rend.glClearColor(0,0, 1)  # Set clear color to a dark gray
rend.glColor(1, 0, 0)


isRUNNING = True

while isRUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRUNNING = False
    rend.glClear() 
    rend.glPoint(width/2, height/2)  # Draw a point in the center of the screen
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
exit(0)