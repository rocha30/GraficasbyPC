import random
import numpy as np
from MathLib import *

class Model:
    def __init__(self):
        self.vertices = []
        self.faces = []       # Nueva: Lista de caras (triángulos)
        self.colors = []      # Nueva: Colores aleatorios por triángulo
        
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        
        self.vertexShader = None
    
    def GetModelMatrix(self):
        translateMat = TranslationMatrix(self.translation[0], self.translation[1], self.translation[2])
        rotateMat = RotationMatrix(self.rotation[0], self.rotation[1], self.rotation[2])
        scaleMat = ScaleMatrix(self.scale[0], self.scale[1], self.scale[2])
        
        return translateMat * rotateMat * scaleMat
    
    def load_obj(self, filename):
        """Cargar modelo desde archivo .obj"""
        self.vertices = []
        self.faces = []
        vertex_list = []  # Lista temporal de vértices
        
        print(f"Cargando modelo: {filename}")
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    if line.startswith('v '):
                        # Vértice: v x y z
                        parts = line.split()
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        vertex_list.append([x, y, z])
                        
                    elif line.startswith('f '):
                        # Cara: f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
                        parts = line.split()[1:]
                        face_vertices = []
                        
                        for vertex in parts:
                            # Extraer solo el índice del vértice (antes del primer '/')
                            vertex_index = int(vertex.split('/')[0]) - 1  # OBJ usa índices 1-based
                            face_vertices.append(vertex_index)
                        
                        # Si la cara tiene más de 3 vértices, triangularla
                        if len(face_vertices) >= 3:
                            for i in range(1, len(face_vertices) - 1):
                                triangle = [face_vertices[0], face_vertices[i], face_vertices[i + 1]]
                                self.faces.append(triangle)
            
            # Convertir vértices a formato flat para el renderer
            self.vertices = []
            for vertex in vertex_list:
                self.vertices.extend(vertex)  # [x1,y1,z1, x2,y2,z2, ...]
            
            # Generar colores aleatorios para cada triángulo
            self.colors = []
            for _ in self.faces:
                r = random.random()
                g = random.random() 
                b = random.random()
                self.colors.append([r, g, b])
            
            print(f"Modelo cargado: {len(vertex_list)} vértices, {len(self.faces)} triángulos")
            
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo {filename}")
        except Exception as e:
            print(f"ERROR cargando modelo: {e}")
    
    def scale_to_fit(self, screen_width, screen_height, margin=50):
        """Escalar modelo para que quepa en pantalla"""
        if not self.vertices:
            return
            
        # Encontrar bounding box
        xs = [self.vertices[i] for i in range(0, len(self.vertices), 3)]
        ys = [self.vertices[i+1] for i in range(0, len(self.vertices), 3)]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Calcular tamaño del modelo
        model_width = max_x - min_x
        model_height = max_y - min_y
        
        # Calcular factor de escala para que quepa en pantalla
        scale_x = (screen_width - margin * 2) / model_width if model_width > 0 else 1
        scale_y = (screen_height - margin * 2) / model_height if model_height > 0 else 1
        scale_factor = min(scale_x, scale_y, 100)  # Máximo 100x
        
        # Aplicar escala
        self.scale = [scale_factor, scale_factor, scale_factor]
        
        # Centrar en pantalla
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        self.translation = [
            screen_width/2 - center_x * scale_factor,
            screen_height/2 - center_y * scale_factor,
            0
        ]
        
        print(f"Modelo escalado: factor={scale_factor:.2f}, centro=({self.translation[0]:.1f}, {self.translation[1]:.1f})")