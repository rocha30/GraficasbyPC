POINTS = 0
LINES = 1
TRIANGLES = 2

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = self.screen.get_rect()

        self.glColor(1,1,1)
        self.glClearColor(0,0,0)

        self.glClear()

        self.primitiveType = TRIANGLES
        self.models = []
        self.camera = None

        self.activeModelMatrix = None
        self.activeVertexShader = None
        
    def set_camera(self, camera):
        """Asignar una cámara al renderizador"""
        self.camera = camera
        if camera:
            camera.set_viewport(0, 0, self.width, self.height)

    def glClearColor(self, r, g, b):
        # 0 - 1
        r = min(1, max(0,r))
        g = min(1, max(0,g))
        b = min(1, max(0,b))

        self.clearColor = [r,g,b]

    def glColor(self, r, g, b):
        # 0 - 1
        r = min(1, max(0,r))
        g = min(1, max(0,g))
        b = min(1, max(0,b))

        self.currColor = [r,g,b]

    def glClear(self):
        color = [int(i * 255) for i in self.clearColor]
        self.screen.fill(color)

        self.frameBuffer = [[color for y in range(self.height)]
                            for x in range(self.width)]
        
        # Inicializar z-buffer con valores muy grandes (infinito)
        self.zBuffer = [[float('inf') for y in range(self.height)]
                       for x in range(self.width)]

    def glPoint(self, x, y, color = None, z = 0):
        # Pygame empieza a renderizar desde la esquina
        # superior izquierda, hay que voltear la Y

        x = round(x)
        y = round(y)

        if (0 <= x < self.width) and (0 <= y < self.height):
            # Test de profundidad: solo dibujar si este pixel está más cerca
            if z < self.zBuffer[x][y]:
                self.zBuffer[x][y] = z
                
                color = [int(i * 255) for i in (color or self.currColor) ]

                self.screen.set_at((x,self.height - 1 - y ), color)
                self.frameBuffer[x][y] = color

    def glLine(self, p0, p1, color = None):
        # Algoritmo de Lineas de Bresenham con interpolación de Z
        x0, y0, z0 = p0[0], p0[1], p0[2] if len(p0) > 2 else 0
        x1, y1, z1 = p1[0], p1[1], p1[2] if len(p1) > 2 else 0

        # Si el punto 0 es igual que el punto 1, solamente dibujar un punto
        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0, color, z0)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            z0, z1 = z1, z0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.75
        m = dy / dx
        y = y0

        # Interpolación de Z a lo largo de la línea
        total_distance = abs(x1 - x0)

        for x in range(round(x0), round(x1) + 1):
            # Calcular t para interpolación
            if total_distance > 0:
                t = abs(x - x0) / total_distance
            else:
                t = 0
            
            # Interpolar Z
            z = z0 + t * (z1 - z0)
            
            if steep:
                self.glPoint(y, x, color or self.currColor, z)
            else:
                self.glPoint(x, y, color or self.currColor, z)

            offset += m

            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1

                limit += 1

    def glTriangle(self, A, B, C, model=None, face_idx=None):
        # Triángulo con z-buffer y texturas usando coordenadas baricéntricas
        # A, B, C deben tener formato [x, y, z]
        
        # Asegurar que tenemos coordenadas z
        if len(A) < 3: A = [A[0], A[1], 0]
        if len(B) < 3: B = [B[0], B[1], 0]
        if len(C) < 3: C = [C[0], C[1], 0]
        
        # Encontrar bounding box
        min_x = max(0, min(A[0], B[0], C[0]))
        max_x = min(self.width - 1, max(A[0], B[0], C[0]))
        min_y = max(0, min(A[1], B[1], C[1]))
        max_y = min(self.height - 1, max(A[1], B[1], C[1]))
        
        # Calcular área del triángulo para coordenadas baricéntricas
        def triangle_area(p1, p2, p3):
            return abs((p1[0] * (p2[1] - p3[1]) + 
                       p2[0] * (p3[1] - p1[1]) + 
                       p3[0] * (p1[1] - p2[1])) / 2)
        
        total_area = triangle_area(A, B, C)
        
        if total_area == 0:
            return  # Triángulo degenerado
        
        # Obtener coordenadas UV si hay textura
        uv_a = uv_b = uv_c = None
        if model and hasattr(model, 'texture') and model.texture and face_idx is not None:
            if face_idx < len(model.face_uvs):
                uv_indices = model.face_uvs[face_idx]
                if len(uv_indices) >= 3:
                    uv_a = model.texture_coords[uv_indices[0]] if uv_indices[0] < len(model.texture_coords) else [0, 0]
                    uv_b = model.texture_coords[uv_indices[1]] if uv_indices[1] < len(model.texture_coords) else [0, 0]
                    uv_c = model.texture_coords[uv_indices[2]] if uv_indices[2] < len(model.texture_coords) else [0, 0]
        
        # Para cada pixel en el bounding box
        for x in range(int(min_x), int(max_x) + 1):
            for y in range(int(min_y), int(max_y) + 1):
                P = [x, y]
                
                # Calcular coordenadas baricéntricas
                area_PBC = triangle_area(P, B, C)
                area_APC = triangle_area(A, P, C)
                area_ABP = triangle_area(A, B, P)
                
                # Coordenadas baricéntricas
                alpha = area_PBC / total_area
                beta = area_APC / total_area
                gamma = area_ABP / total_area
                
                # Verificar si el punto está dentro del triángulo
                if alpha >= 0 and beta >= 0 and gamma >= 0 and abs(alpha + beta + gamma - 1) < 0.01:
                    # Interpolar Z usando coordenadas baricéntricas
                    z = alpha * A[2] + beta * B[2] + gamma * C[2]
                    
                    # Determinar color del pixel
                    color = self.currColor
                    
                    # Si hay textura Y colores de lighting, combinarlos
                    if uv_a and uv_b and uv_c and model and hasattr(model, 'colors') and face_idx is not None and face_idx < len(model.colors):
                        u = alpha * uv_a[0] + beta * uv_b[0] + gamma * uv_c[0]
                        v = alpha * uv_a[1] + beta * uv_b[1] + gamma * uv_c[1]
                        texture_color = model.get_texture_color(u, v)
                        lighting_color = model.colors[face_idx]
                        
                        # Multiplicar textura por lighting (ambos en rango 0-1)
                        color = [
                            texture_color[0] * lighting_color[0],
                            texture_color[1] * lighting_color[1], 
                            texture_color[2] * lighting_color[2]
                        ]
                    
                    # Si solo hay textura (sin lighting)
                    elif uv_a and uv_b and uv_c and model:
                        u = alpha * uv_a[0] + beta * uv_b[0] + gamma * uv_c[0]
                        v = alpha * uv_a[1] + beta * uv_b[1] + gamma * uv_c[1]
                        texture_color = model.get_texture_color(u, v)
                        color = texture_color
                    
                    # Si solo hay lighting (sin textura)
                    elif hasattr(model, 'colors') and face_idx is not None and face_idx < len(model.colors):
                        color = model.colors[face_idx]
                    
                    self.glPoint(x, y, color, z)

    def glRender(self):
        for model in self.models:
            # Por cada modelo en la lista, los dibujo
            # Agarrar su matriz modelo y vertexshader
            self.activeModelMatrix = model.GetModelMatrix()
            self.activeVertexShader = model.vertexShader

            # Aqui vamos a guardar todos los vertices y su info correspondiente
            vertexBuffer = []

            # Si el modelo tiene caras definidas (archivo .obj), usar esas
            if hasattr(model, 'faces') and model.faces:
                self.render_with_faces(model, vertexBuffer)
            else:
                # Fallback: renderizado secuencial original
                for i in range(0, len(model.vertices), 3):
                    x = model.vertices[i]
                    y = model.vertices[i + 1]
                    z = model.vertices[i + 2]

                    # Si contamos con un Vertex Shader, se manda cada vertice
                    # para transformalos. Recordar pasar las matrices necesarias
                    # para usarlas dentro del shader
                    if self.activeVertexShader:
                        # Pasar matrices de cámara al shader
                        kwargs = {"modelMatrix": self.activeModelMatrix}
                        
                        if self.camera:
                            kwargs["viewMatrix"] = self.camera.get_view_matrix()
                            kwargs["projectionMatrix"] = self.camera.get_projection_matrix()
                            kwargs["viewportMatrix"] = self.camera.get_viewport_matrix()
                        
                        x, y, z = self.activeVertexShader([x,y,z], **kwargs)

                    vertexBuffer.append(x)
                    vertexBuffer.append(y)
                    vertexBuffer.append(z)

                self.glDrawPrimitives(vertexBuffer, 3)

    def render_with_faces(self, model, vertexBuffer):
        """Renderizar usando las caras del modelo con texturas y z-buffer"""
        # Procesar todos los vértices primero
        for i in range(0, len(model.vertices), 3):
            x = model.vertices[i]
            y = model.vertices[i + 1]
            z = model.vertices[i + 2]

            if self.activeVertexShader:
                # Pasar matrices de cámara al shader
                kwargs = {"modelMatrix": self.activeModelMatrix}
                
                if self.camera:
                    kwargs["viewMatrix"] = self.camera.get_view_matrix()
                    kwargs["projectionMatrix"] = self.camera.get_projection_matrix()
                    kwargs["viewportMatrix"] = self.camera.get_viewport_matrix()
                
                x, y, z = self.activeVertexShader([x,y,z], **kwargs)
            
            vertexBuffer.append([x, y, z])

        # Renderizar cada cara con su textura correspondiente
        for face_idx, face in enumerate(model.faces):
            if len(face) >= 3:
                # Obtener vértices del triángulo
                v1 = vertexBuffer[face[0]]
                v2 = vertexBuffer[face[1]] 
                v3 = vertexBuffer[face[2]]
                
                # Usar color base del modelo
                if hasattr(model, 'texture') and model.texture:
                    # Si hay textura, usar color neutro - el lighting se aplica por pixel
                    self.glColor(1.0, 1.0, 1.0)
                else:
                    # Si no hay textura, usar el color de lighting directamente
                    if hasattr(model, 'colors') and face_idx < len(model.colors):
                        color = model.colors[face_idx]
                        self.glColor(color[0], color[1], color[2])
                    else:
                        # Fallback a color aleatorio si no hay lighting
                        self.glColor(1.0, 1.0, 1.0)
                
                # Renderizar según el tipo de primitiva
                if self.primitiveType == TRIANGLES:
                    self.glTriangle(v1, v2, v3, model, face_idx)
                elif self.primitiveType == LINES:
                    self.glLine(v1, v2)
                    self.glLine(v2, v3)
                    self.glLine(v3, v1)
                elif self.primitiveType == POINTS:
                    self.glPoint(v1[0], v1[1], None, v1[2])
                    self.glPoint(v2[0], v2[1], None, v2[2])
                    self.glPoint(v3[0], v3[1], None, v3[2])

    def glDrawPrimitives(self, buffer, vertexOffset):
        # El buffer es un listado de valores que representan
        # toda la informacion de un vertice (posicion, coordenadas
        # de textura, normales, color, etc.). El VertexOffset se
        # refiere a cada cuantos valores empieza la informacion
        # de un vertice individual
        # Se asume que los primeros tres valores de un vertice
        # corresponden a Posicion.

        if self.primitiveType == POINTS:
            # Si son puntos, revisamos el buffer en saltos igual
            # al Vertex Offset. El valor X, Y, Z de cada vertice
            # corresponden a los primeros tres valores.
            for i in range(0, len(buffer), vertexOffset):
                x = buffer[i]
                y = buffer[i + 1]
                z = buffer[i + 2] if vertexOffset > 2 else 0
                self.glPoint(x, y, None, z)

        elif self.primitiveType == LINES:
            # Si son lineas, revisamos el buffer en saltos igual
            # a 3 veces el Vertex Offset, porque cada trio corresponde
            # a un triangulo. 
            for i in range(0, len(buffer), vertexOffset * 3):
                for j in range(3):
                    # Hay que dibujar la linea de un vertice al siguiente
                    x0 = buffer[i + vertexOffset * j + 0]
                    y0 = buffer[i + vertexOffset * j + 1]
                    z0 = buffer[i + vertexOffset * j + 2] if vertexOffset > 2 else 0

                    # En caso de que sea el ultimo vertices, el siguiente
                    # seria el primero
                    x1 = buffer[i + vertexOffset * ((j + 1) % 3) + 0]
                    y1 = buffer[i + vertexOffset * ((j + 1) % 3) + 1]
                    z1 = buffer[i + vertexOffset * ((j + 1) % 3) + 2] if vertexOffset > 2 else 0

                    self.glLine([x0,y0,z0], [x1,y1,z1])

        elif self.primitiveType == TRIANGLES:
            # Si son triangulos revisamos el buffer en saltos igual
            # a 3 veces el Vertex Offset, porque cada trio corresponde
            # a un triangulo. 
            for i in range(0, len(buffer), vertexOffset * 3):
                # Necesitamos tres vertices para mandar a dibujar el triangulo.
                # Cada vertice necesita todos sus datos, la cantidad de estos
                # datos es igual a VertexOffset
                A = [ buffer[i + j + vertexOffset * 0] for j in range(vertexOffset) ]
                B = [ buffer[i + j + vertexOffset * 1] for j in range(vertexOffset) ]
                C = [ buffer[i + j + vertexOffset * 2] for j in range(vertexOffset) ]

                self.glTriangle(A,B,C)
                
                
    def glRenderZBuffer(self):
        """Renderizar el z-buffer como imagen en escala de grises para debug"""
        # Encontrar rango de valores Z
        min_z = float('inf')
        max_z = float('-inf')
        
        for x in range(self.width):
            for y in range(self.height):
                if self.zBuffer[x][y] != float('inf'):
                    min_z = min(min_z, self.zBuffer[x][y])
                    max_z = max(max_z, self.zBuffer[x][y])
        
        if min_z == float('inf'):
            return  # No hay geometría renderizada
        
        # Normalizar y renderizar
        z_range = max_z - min_z if max_z != min_z else 1
        
        for x in range(self.width):
            for y in range(self.height):
                if self.zBuffer[x][y] != float('inf'):
                    # Normalizar valor Z (0 = negro/cerca, 1 = blanco/lejos)
                    normalized_z = (self.zBuffer[x][y] - min_z) / z_range
                    intensity = int(normalized_z * 255)
                    color = [intensity, intensity, intensity]
                    
                    self.screen.set_at((x, self.height - 1 - y), color)
                    self.frameBuffer[x][y] = color