import random
import numpy as np
from PIL import Image
from MathLib import *

class Model:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.colors = []
        self.texture_coords = []    
        self.texture = None         
        self.face_uvs = []          
        
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
        """Cargar textura desde archivo BMP únicamente"""
        # Verificar que el archivo tenga extensión .bmp
        if not filename.lower().endswith('.bmp'):
            print(f"ERROR: Solo se permiten archivos BMP. Archivo recibido: {filename}")
            print("Creando textura procedural simple...")
            self.texture = self.create_simple_texture()
            return
            
        try:
            self.texture = Image.open(filename)
            # Verificar que realmente sea un archivo BMP
            if self.texture.format != 'BMP':
                print(f"ERROR: El archivo no es un BMP válido. Formato detectado: {self.texture.format}")
                print("Creando textura procedural simple...")
                self.texture = self.create_simple_texture()
                return
                
            # Convertir a RGB si está en otro formato
            if self.texture.mode != 'RGB':
                self.texture = self.texture.convert('RGB')
            print(f"Textura BMP cargada exitosamente: {filename} ({self.texture.width}x{self.texture.height})")
        except Exception as e:
            print(f"Error cargando textura BMP {filename}: {e}")
            print("Creando textura procedural simple...")
            self.texture = self.create_simple_texture()
    
    def create_simple_texture(self):
        """Crear una textura procedural simple"""
        size = 512
        texture = Image.new('RGB', (size, size))
        pixels = texture.load()
        
        for x in range(size):
            for y in range(size):
                # Gradiente simple
                r = int((x / size) * 255)
                g = int((y / size) * 255) 
                b = int(((x + y) / (size * 2)) * 255)
                pixels[x, y] = (r, g, b)
        
        print(f"Textura procedural creada: {size}x{size}")
        return texture
    
    def get_texture_color(self, u, v):
        """Obtener color de la textura en coordenadas UV"""
        if not self.texture:
            return [0.8, 0.8, 0.8]  # Gris claro si no hay textura
        
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
    
    def debug_uv_coordinates(self, face_idx=0):
        """Función de debug para verificar coordenadas UV de una cara específica"""
        if face_idx < len(self.face_uvs) and self.texture_coords:
            uv_indices = self.face_uvs[face_idx]
            print(f"Cara {face_idx} - Índices UV: {uv_indices}")
            for i, uv_idx in enumerate(uv_indices):
                if uv_idx < len(self.texture_coords):
                    u, v = self.texture_coords[uv_idx]
                    print(f"  Vértice {i}: UV({u:.3f}, {v:.3f})")
                    color = self.get_texture_color(u, v)
                    print(f"    Color: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f})")
        
        # Estadísticas generales de UV
        if self.texture_coords:
            us = [uv[0] for uv in self.texture_coords]
            vs = [uv[1] for uv in self.texture_coords]
            print(f"Rango U: {min(us):.3f} a {max(us):.3f}")
            print(f"Rango V: {min(vs):.3f} a {max(vs):.3f}")
    
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
    
    def calculate_lighting_colors(self):
        """Calcular colores con iluminación para cada cara"""
        if not self.faces:
            return
            
        # Configuración de luz
        light_pos = [5, 5, 5]      # Posición de la luz
        light_color = [1, 1, 1]    # Color blanco
        ambient_strength = 0.5     # Luz ambiente más alta para preservar texturas
        
        self.colors = []
        
        for i, face in enumerate(self.faces):
            # Obtener vértices de la cara
            v0_idx = face[0] * 3
            v1_idx = face[1] * 3  
            v2_idx = face[2] * 3
            
            vertex_a = [self.vertices[v0_idx], self.vertices[v0_idx+1], self.vertices[v0_idx+2]]
            vertex_b = [self.vertices[v1_idx], self.vertices[v1_idx+1], self.vertices[v1_idx+2]]
            vertex_c = [self.vertices[v2_idx], self.vertices[v2_idx+1], self.vertices[v2_idx+2]]
            
            # Calcular normal del triángulo
            edge1 = [vertex_b[0] - vertex_a[0], vertex_b[1] - vertex_a[1], vertex_b[2] - vertex_a[2]]
            edge2 = [vertex_c[0] - vertex_a[0], vertex_c[1] - vertex_a[1], vertex_c[2] - vertex_a[2]]
            
            # Producto cruz para obtener normal
            normal = [
                edge1[1] * edge2[2] - edge1[2] * edge2[1],
                edge1[2] * edge2[0] - edge1[0] * edge2[2], 
                edge1[0] * edge2[1] - edge1[1] * edge2[0]
            ]
            
            # Normalizar
            normal_length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
            if normal_length > 0:
                normal = [n / normal_length for n in normal]
            else:
                normal = [0, 1, 0]
            
            # Centro del triángulo
            center = [
                (vertex_a[0] + vertex_b[0] + vertex_c[0]) / 3,
                (vertex_a[1] + vertex_b[1] + vertex_c[1]) / 3,
                (vertex_a[2] + vertex_b[2] + vertex_c[2]) / 3
            ]
            
            # Vector hacia la luz
            light_dir = [
                light_pos[0] - center[0],
                light_pos[1] - center[1], 
                light_pos[2] - center[2]
            ]
            
            # Normalizar dirección de luz
            light_length = (light_dir[0]**2 + light_dir[1]**2 + light_dir[2]**2)**0.5
            if light_length > 0:
                light_dir = [ld / light_length for ld in light_dir]
            
            # Calcular intensidad diffusa
            diffuse = max(0, normal[0] * light_dir[0] + normal[1] * light_dir[1] + normal[2] * light_dir[2])
            
            # Intensidad final (más sutil)
            final_intensity = ambient_strength + (1 - ambient_strength) * diffuse
            
            # Color base de la textura
            base_color = [0.7, 0.6, 0.5]  # Color por defecto
            
            # Si hay textura, obtener color promedio más representativo
            if self.texture and i < len(self.face_uvs):
                uv_indices = self.face_uvs[i]
                if len(uv_indices) >= 3:
                    # Usar múltiples puntos de muestreo para mejor representación
                    colors = []
                    sample_points = [
                        (0.33, 0.33),  # Centro del triángulo
                        (0.5, 0.25),   # Otros puntos
                        (0.25, 0.5),
                        (0.6, 0.6)
                    ]
                    
                    for su, sv in sample_points:
                        # Interpolar coordenadas UV
                        uv_a = self.texture_coords[uv_indices[0]] if uv_indices[0] < len(self.texture_coords) else [0, 0]
                        uv_b = self.texture_coords[uv_indices[1]] if uv_indices[1] < len(self.texture_coords) else [0, 0]
                        uv_c = self.texture_coords[uv_indices[2]] if uv_indices[2] < len(self.texture_coords) else [0, 0]
                        
                        sw = 1.0 - su - sv  # Coordenada baricéntrica restante
                        
                        tex_u = sw * uv_a[0] + su * uv_b[0] + sv * uv_c[0]
                        tex_v = sw * uv_a[1] + su * uv_b[1] + sv * uv_c[1]
                        
                        color = self.get_texture_color(tex_u, tex_v)
                        colors.append(color)
                    
                    if colors:
                        # Promedio de múltiples muestras
                        base_color = [
                            sum(c[0] for c in colors) / len(colors),
                            sum(c[1] for c in colors) / len(colors),
                            sum(c[2] for c in colors) / len(colors)
                        ]
            
            # Aplicar iluminación de forma más sutil
            final_color = [
                min(1.0, max(0.0, base_color[0] * light_color[0] * final_intensity)),
                min(1.0, max(0.0, base_color[1] * light_color[1] * final_intensity)),
                min(1.0, max(0.0, base_color[2] * light_color[2] * final_intensity))
            ]
            
            self.colors.append(final_color)
        
        # Debug: Mostrar algunos colores calculados
        print(f"Colores con iluminación mejorada calculados: {len(self.colors)} caras")
        if self.colors:
            print(f"Primeros 3 colores: {self.colors[:3]}")
            print(f"Intensidades promedio: R={sum(c[0] for c in self.colors[:10])/min(10, len(self.colors)):.3f}, "
                  f"G={sum(c[1] for c in self.colors[:10])/min(10, len(self.colors)):.3f}, "
                  f"B={sum(c[2] for c in self.colors[:10])/min(10, len(self.colors)):.3f}")

    def test_dramatic_lighting(self):
        """Crear iluminación dramática para prueba"""
        print("Aplicando iluminación dramática de prueba...")
        
        # Colores extremos para poder ver la diferencia
        light_color = [1.0, 1.0, 0.8]  # Luz amarillenta
        dark_color = [0.1, 0.1, 0.2]   # Azul muy oscuro
        
        self.colors = []
        
        for i, face in enumerate(self.faces):
            # Alternar entre claro y oscuro basado en el índice
            if i % 3 == 0:
                self.colors.append(light_color.copy())
            elif i % 3 == 1:
                self.colors.append(dark_color.copy())
            else:
                self.colors.append([0.5, 0.5, 0.5])  # Gris medio
        
        print(f"Colores dramáticos aplicados: {len(self.colors)} caras")
        print(f"Patrón: Claro({light_color}) -> Oscuro({dark_color}) -> Gris")

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