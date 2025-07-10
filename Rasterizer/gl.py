import pygame

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = self.screen.get_rect()
        self.currColor = [1, 1, 1]  # Color actual
        self.ClearColor = [0, 0, 0]  # Color de limpieza
        # Inicializar framebuffer - FIXED: [height][width] order
        self.framebuffer = [[self.ClearColor for x in range(self.width)]
                           for y in range(self.height)]
    
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
        color = [int(i * 255) for i in self.ClearColor]
        self.screen.fill(color)
        self.framebuffer = [[self.ClearColor for x in range(self.width)]
                           for y in range(self.height)]
    
    def glPoint(self, x, y, color=None):
        x = round(x)
        y = round(y)
        if (0 <= x < self.width and 0 <= y < self.height):
            color = [int(i * 255) for i in (color or self.currColor)]
            
            # For cartesian coordinates: (0,0) at bottom-left
            # Convert y coordinate: screen_y = height - 1 - cartesian_y
            screen_y = self.height - 1 - y
            
            # Update both screen and framebuffer
            self.screen.set_at((x, screen_y), color)
            self.framebuffer[screen_y][x] = color
    
    def glLine(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx
        
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            dx, dy = dy, dx
        
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        offset = 0
        threshold = dx
        y = y0
        y_step = 1 if y0 < y1 else -1
        
        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x)
            else:
                self.glPoint(x, y)
            
            offset += dy * 2
            if offset >= threshold:
                y += y_step
                threshold += dx * 2
    
    def glDrawPolygon(self, points):
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            self.glLine(x0, y0, x1, y1)
    
    def glFillPolygon(self, points):
        if len(points) < 3:
            return
        
        min_y = min(y for _, y in points)
        max_y = max(y for _, y in points)
        edges = []
        n = len(points)
        
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            
            if y0 == y1:
                continue
            
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            
            inv_slope = (x1 - x0) / (y1 - y0) if (y1 - y0) != 0 else 0
            edges.append((y0, y1, x0, inv_slope))
        
        for y in range(int(min_y), int(max_y) + 1):
            intersections = []
            
            for edge in edges:
                y0_edge, y1_edge, x0_edge, inv_slope = edge
                
                # FIXED: Use < instead of <= to avoid double-counting vertices
                if y0_edge <= y < y1_edge:
                    x_intersection = x0_edge + inv_slope * (y - y0_edge)
                    intersections.append(x_intersection)
            
            intersections.sort()
            
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = int(round(intersections[i]))
                    x_end = int(round(intersections[i + 1]))
                    
                    for x in range(x_start, x_end + 1):
                        self.glPoint(x, y)