import pygame

class Renderer(object): 
    def __init__(self, screen):
        self.screen = screen 
        _,_, self.width, self.height = self.screen.get_rect()
        
        self.currColor = [1, 1, 1]  # Color actual
        self.ClearColor = [0, 0, 0]  # Color de limpieza
        
        # Inicializar framebuffer
        self.framebuffer = [[self.ClearColor for y in range(self.height)] 
                            for x in range(self.width)]
        
    def glClearColor(self, r, g, b): 
        # Normalizar valores entre 0-1 
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))
        
        self.ClearColor = [r, g, b]
    
    def glColor(self, r, g, b):
        # Establecer color actual
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))
        
        self.currColor = [r, g, b]
    def glClear(self):
        color = [int(i*255) for i in self.ClearColor]
        self.screen.fill(color)
        
        self.framebuffer = [[self.ClearColor for y in range(self.height)] 
                            for x in range(self.width)]
        
    def glPoint(self, x, y, color=None):
        x = round(x)
        y = round(y)
        if (0 <= x < self.width and
            0 <= y < self.height):
        
            color = [int(i*255) for i in (color or self.currColor)]
            
            self.screen.set_at((x, self.height - 1 - y), color)
            self.framebuffer[y][x] = color