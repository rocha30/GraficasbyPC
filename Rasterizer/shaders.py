import numpy as np

def vertexShader(vertex, **kwargs):
    # Se lleva a cabo por vertice

    # Recibimos las matrices
    modelMatrix = kwargs.get("modelMatrix")
    viewMatrix = kwargs.get("viewMatrix") 
    projectionMatrix = kwargs.get("projectionMatrix")
    viewportMatrix = kwargs.get("viewportMatrix")

    # Agregamos un componente W al vertice como numpy array
    vt = np.array([vertex[0], vertex[1], vertex[2], 1]).reshape(4, 1)

    # Transformamos el vertices por todas las matrices en el orden correcto
    # Orden: Model -> View -> Projection -> Viewport
    if modelMatrix is not None:
        vt = modelMatrix @ vt
    
    if viewMatrix is not None:
        vt = viewMatrix @ vt
        
    if projectionMatrix is not None:
        vt = projectionMatrix @ vt
        
    # Dividir por W para proyección perspectiva
    if vt[3, 0] != 0:
        vt = vt / vt[3, 0]
    
    if viewportMatrix is not None:
        vt = viewportMatrix @ vt

    # Extraer coordenadas con límites de seguridad
    x = float(vt[0, 0])
    y = float(vt[1, 0])
    z = float(vt[2, 0])
    
    # Limitar coordenadas para evitar bucles infinitos
    x = max(-10000, min(10000, x))
    y = max(-10000, min(10000, y))
    z = max(-10000, min(10000, z))
    
    # Verificar valores válidos
    if not (np.isfinite(x) and np.isfinite(y) and np.isfinite(z)):
        return [0, 0, 0]
    
    return [x, y, z]


def lightingVertexShader(vertex, **kwargs):
    """Vertex shader que también calcula posición mundial para iluminación"""
    modelMatrix = kwargs.get("modelMatrix")
    viewMatrix = kwargs.get("viewMatrix") 
    projectionMatrix = kwargs.get("projectionMatrix")
    viewportMatrix = kwargs.get("viewportMatrix")

    # Calcular posición mundial (antes de las transformaciones de cámara)
    vt_world = np.array([vertex[0], vertex[1], vertex[2], 1]).reshape(4, 1)
    if modelMatrix is not None:
        vt_world = modelMatrix @ vt_world
    
    # Guardar posición mundial para iluminación
    world_pos = [float(vt_world[0, 0]), float(vt_world[1, 0]), float(vt_world[2, 0])]
    
    # Continuar con transformaciones normales
    vt = np.array([vertex[0], vertex[1], vertex[2], 1]).reshape(4, 1)

    if modelMatrix is not None:
        vt = modelMatrix @ vt
    if viewMatrix is not None:
        vt = viewMatrix @ vt
    if projectionMatrix is not None:
        vt = projectionMatrix @ vt
        
    if vt[3, 0] != 0:
        vt = vt / vt[3, 0]
    
    if viewportMatrix is not None:
        vt = viewportMatrix @ vt

    x = float(vt[0, 0])
    y = float(vt[1, 0])
    z = float(vt[2, 0])
    
    x = max(-10000, min(10000, x))
    y = max(-10000, min(10000, y))
    z = max(-10000, min(10000, z))
    
    if not (np.isfinite(x) and np.isfinite(y) and np.isfinite(z)):
        return [0, 0, 0]
    
    return [x, y, z]


def fragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader con iluminación básica"""
    # Configuración de luz
    light_pos = [5, 5, 5]      # Posición de la luz
    light_color = [1, 1, 1]    # Color blanco
    ambient_strength = 0.3     # Luz ambiente
    
    # Obtener color base de la textura o color sólido
    model = kwargs.get("model")
    base_color = [0.7, 0.7, 0.7]  # Color gris por defecto
    
    if model and hasattr(model, 'texture') and model.texture:
        # Calcular coordenadas UV interpoladas
        face_idx = kwargs.get("face_idx")
        if face_idx is not None and face_idx < len(model.face_uvs):
            uv_indices = model.face_uvs[face_idx]
            if len(uv_indices) >= 3:
                # Interpolar coordenadas UV usando coordenadas baricéntricas
                uv_a = model.texture_coords[uv_indices[0]] if uv_indices[0] < len(model.texture_coords) else [0, 0]
                uv_b = model.texture_coords[uv_indices[1]] if uv_indices[1] < len(model.texture_coords) else [0, 0]
                uv_c = model.texture_coords[uv_indices[2]] if uv_indices[2] < len(model.texture_coords) else [0, 0]
                
                # Interpolación baricéntrica
                tex_u = u * uv_a[0] + v * uv_b[0] + w * uv_c[0]
                tex_v = u * uv_a[1] + v * uv_b[1] + w * uv_c[1]
                
                base_color = model.get_texture_color(tex_u, tex_v)
    
    # Calcular normal del triángulo
    # Vectores del triángulo
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
        normal = [0, 1, 0]  # Normal por defecto
    
    # Calcular posición del fragmento interpolada
    frag_pos = [
        u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
        u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1],
        u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
    ]
    
    # Vector desde fragmento hacia la luz
    light_dir = [
        light_pos[0] - frag_pos[0],
        light_pos[1] - frag_pos[1], 
        light_pos[2] - frag_pos[2]
    ]
    
    # Normalizar dirección de luz
    light_length = (light_dir[0]**2 + light_dir[1]**2 + light_dir[2]**2)**0.5
    if light_length > 0:
        light_dir = [ld / light_length for ld in light_dir]
    
    # Calcular intensidad diffusa (Lambert)
    diffuse = max(0, normal[0] * light_dir[0] + normal[1] * light_dir[1] + normal[2] * light_dir[2])
    
    # Combinar luz ambiente y diffusa
    final_intensity = ambient_strength + (1 - ambient_strength) * diffuse
    
    # Aplicar iluminación al color base
    final_color = [
        min(1.0, base_color[0] * light_color[0] * final_intensity),
        min(1.0, base_color[1] * light_color[1] * final_intensity),
        min(1.0, base_color[2] * light_color[2] * final_intensity)
    ]
    
    return final_color


def simpleVertexShader(vertex, **kwargs):
    """Shader más simple para debugging"""
    modelMatrix = kwargs.get("modelMatrix")
    
    vt = np.array([vertex[0], vertex[1], vertex[2], 1]).reshape(4, 1)
    
    if modelMatrix is not None:
        vt = modelMatrix @ vt
        if vt[3, 0] != 0:
            vt = vt / vt[3, 0]
    
    x = float(vt[0, 0])
    y = float(vt[1, 0])
    z = float(vt[2, 0])
    
    # Aplicar límites también al shader simple
    x = max(-1000, min(1000, x))
    y = max(-1000, min(1000, y))
    z = max(-1000, min(1000, z))
    
    return [x, y, z]
