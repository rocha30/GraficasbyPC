import numpy as np 
from Math.MathLib import * 

class Camera:
    def __init__(self):
        self.position = [0, 0, 3]
        self.target = [0, 0, 0]
        self.up = [0, 1, 0]
        
        self.fov = 45  # Field of view in degrees
        self.aspect = 1.0  # Aspect ratio
        self.near = 0.1  # Near clipping plane
        self.far = 50.0  # Far clipping plane

        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 720
        self.viewport_height = 720
        
        
    def set_position(self, x, y, z): 
        self.position = [x, y, z]
    
    def set_target(self, x, y, z):
        self.target = [x, y, z]
        
    def set_up(self, x, y, z):
        self.up = [x, y, z]
        
    def set_projection(self, fov, aspect, near, far):
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
        
    def set_viewport(self, x, y, width, height):
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_width = width
        self.viewport_height = height
        
    def get_view_matrix(self):
        """Obtener matriz de vista"""
        return ViewMatrix(self.position, self.target, self.up)
    
    def get_projection_matrix(self):
        """Obtener matriz de proyección"""
        return ProjectionMatrix(self.fov, self.aspect, self.near, self.far)
    
    def get_viewport_matrix(self):
        """Obtener matriz de viewport"""
        return ViewportMatrix(self.viewport_x, self.viewport_y, 
                            self.viewport_width, self.viewport_height)
    
    def orbit_around_target(self, horizontal_angle, vertical_angle, distance):
        """Orbitar alrededor del target"""
        h_rad = horizontal_angle * np.pi / 180
        v_rad = vertical_angle * np.pi / 180
        
        # Calcular nueva posición
        x = self.target[0] + distance * np.cos(v_rad) * np.cos(h_rad)
        y = self.target[1] + distance * np.sin(v_rad)
        z = self.target[2] + distance * np.cos(v_rad) * np.sin(h_rad)
        
        self.position = [x, y, z]
    
    def move_forward(self, distance):
        """Mover cámara hacia adelante/atrás"""
        forward = np.array(self.target) - np.array(self.position)
        forward = forward / np.linalg.norm(forward)
        
        new_pos = np.array(self.position) + forward * distance
        self.position = new_pos.tolist()
    
    def move_right(self, distance):
        """Mover cámara hacia la derecha/izquierda"""
        forward = np.array(self.target) - np.array(self.position)
        forward = forward / np.linalg.norm(forward)
        
        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)
        
        new_pos = np.array(self.position) + right * distance
        self.position = new_pos.tolist()
    
    def move_up(self, distance):
        """Mover cámara hacia arriba/abajo"""
        up = np.array(self.up)
        up = up / np.linalg.norm(up)
        
        new_pos = np.array(self.position) + up * distance
        self.position = new_pos.tolist()
        
        