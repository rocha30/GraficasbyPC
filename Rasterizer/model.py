import random
import numpy as np
from PIL import Image
from MathLib import *

class Model:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.colors = []
        self.texture_coords = []    # ✅ Nuevo: coordenadas UV
        self.texture = None         # ✅ Nuevo: imagen de textura
        self.face_uvs = []          # ✅ Nuevo: UVs por cara
        
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        
        self.vertexShader = None
    
    def GetModelMatrix(self):
        translateMat = TranslationMatrix(self.translation[0], self.translation[1], self.translation[2])
        rotateMat = RotationMatrix(self.rotation[0], self.rotation[1], self.rotation[2])
        scaleMat = ScaleMatrix(self.scale[0], self.scale[1], self.scale[2])
        
        return translateMat * rotateMat * scaleMat
    
    def load_texture(self, filename):
        """Cargar textura desde archivo BMP"""
        try:
            self.texture = Image.open(filename)
            # Convertir a RGB si está en otro formato
            if self.texture.mode != 'RGB':
                self.texture = self.texture.convert('RGB')
            print(f"Textura BMP cargada: {filename} ({self.texture.width}x{self.texture.height})")
        except Exception as e:
            print(f"Error cargando textura BMP {filename}: {e}")
            # Crear textura de fallback (patrón de tablero)
            self.texture = self.create_default_texture()
    
    def create_default_texture(self):
        """Crear textura de tablero por defecto"""
        size = 256
        texture = Image.new('RGB', (size, size))
        pixels = texture.load()
        
        for x in range(size):
            for y in range(size):
                if (x // 32 + y // 32) % 2:
                    pixels[x, y] = (255, 255, 255)  # Blanco
                else:
                    pixels[x, y] = (128, 128, 128)  # Gris
        
        return texture
    
    def get_texture_color(self, u, v):
        """Obtener color de la textura en coordenadas UV"""
        if not self.texture:
            return [1.0, 0.0, 1.0]  # Magenta si no hay textura
        
        # Normalizar coordenadas UV
        u = u % 1.0
        v = v % 1.0
        
        # Convertir a coordenadas de píxel
        x = int(u * (self.texture.width - 1))
        y = int((1.0 - v) * (self.texture.height - 1))  # Flip Y
        
        # Clamp para evitar índices fuera de rango
        x = max(0, min(self.texture.width - 1, x))
        y = max(0, min(self.texture.height - 1, y))
        
        # Obtener color y normalizar a 0-1
        r, g, b = self.texture.getpixel((x, y))
        return [r / 255.0, g / 255.0, b / 255.0]
    
    def load_obj(self, filename):
        """Cargar modelo desde archivo .obj con soporte para texturas"""
        self.vertices = []
        self.faces = []
        self.texture_coords = []
        self.face_uvs = []
        vertex_list = []
        uv_list = []
        
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
                        
                    elif line.startswith('vt '):
                        # Coordenada de textura: vt u v
                        parts = line.split()
                        u, v = float(parts[1]), float(parts[2])
                        uv_list.append([u, v])
                        
                    elif line.startswith('f '):
                        # Cara: f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3
                        parts = line.split()[1:]
                        face_vertices = []
                        face_texture_coords = []
                        
                        for vertex in parts:
                            # Separar índices: vertex/texture/normal
                            indices = vertex.split('/')
                            vertex_index = int(indices[0]) - 1  # OBJ usa índices 1-based
                            face_vertices.append(vertex_index)
                            
                            # Si hay coordenadas de textura
                            if len(indices) > 1 and indices[1]:
                                texture_index = int(indices[1]) - 1
                                face_texture_coords.append(texture_index)
                            else:
                                face_texture_coords.append(0)  # UV por defecto
                        
                        # Si la cara tiene más de 3 vértices, triangularla
                        if len(face_vertices) >= 3:
                            for i in range(1, len(face_vertices) - 1):
                                triangle = [face_vertices[0], face_vertices[i], face_vertices[i + 1]]
                                triangle_uvs = [face_texture_coords[0], face_texture_coords[i], face_texture_coords[i + 1]]
                                self.faces.append(triangle)
                                self.face_uvs.append(triangle_uvs)
            
            # Convertir vértices a formato flat
            self.vertices = []
            for vertex in vertex_list:
                self.vertices.extend(vertex)
            
            # Almacenar coordenadas UV
            self.texture_coords = uv_list
            
            # Si no hay UVs, crear coordenadas por defecto
            if not self.texture_coords:
                print("No se encontraron coordenadas UV, creando por defecto")
                for i in range(len(vertex_list)):
                    self.texture_coords.append([0.5, 0.5])  # Centro de la textura
                
                for i in range(len(self.faces)):
                    self.face_uvs.append([0, 0, 0])  # Usar el primer UV
            
            # Generar colores aleatorios como fallback
            self.colors = []
            for _ in self.faces:
                r = random.random()
                g = random.random() 
                b = random.random()
                self.colors.append([r, g, b])
            
            print(f"Modelo cargado: {len(vertex_list)} vértices, {len(self.faces)} triángulos")
            print(f"Coordenadas UV: {len(self.texture_coords)}")
            
        except FileNotFoundError:
            print(f"ERROR: No se encontró el archivo {filename}")
        except Exception as e:
            print(f"ERROR cargando modelo: {e}")
    
    def scale_to_fit(self, target_size=2.0):
        """Escalar modelo para que quepa en un cubo de tamaño target_size centrado en origen"""
        if not self.vertices:
            return
            
        # Encontrar bounding box 3D
        xs = [self.vertices[i] for i in range(0, len(self.vertices), 3)]
        ys = [self.vertices[i+1] for i in range(0, len(self.vertices), 3)]
        zs = [self.vertices[i+2] for i in range(0, len(self.vertices), 3)]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        
        # Calcular tamaño del modelo en cada dimensión
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        
        # Encontrar la dimensión más grande
        max_size = max(size_x, size_y, size_z)
        
        # Calcular factor de escala
        scale_factor = target_size / max_size if max_size > 0 else 1
        
        # Aplicar escala uniforme
        self.scale = [scale_factor, scale_factor, scale_factor]
        
        # Centrar en origen
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2
        
        self.translation = [
            -center_x * scale_factor,
            -center_y * scale_factor,
            -center_z * scale_factor
        ]
        
        print(f"Modelo escalado 3D: factor={scale_factor:.3f}")
        print(f"Tamaño original: {size_x:.1f} x {size_y:.1f} x {size_z:.1f}")
        print(f"Centro: ({self.translation[0]:.1f}, {self.translation[1]:.1f}, {self.translation[2]:.1f})")