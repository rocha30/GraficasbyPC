import numpy as np

def vertexShader(vertex, **kwargs):
    

    modelMatrix = kwargs.get("modelMatrix")
    viewMatrix = kwargs.get("viewMatrix") 
    projectionMatrix = kwargs.get("projectionMatrix")
    viewportMatrix = kwargs.get("viewportMatrix")

    
    vt = np.array([vertex[0], vertex[1], vertex[2], 1]).reshape(4, 1)


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

def hologramShader(vertex, **kwargs):
    """Vertex shader para efecto de holograma"""
    # Usar el vertex shader básico para transformaciones
    transformed_vertex = vertexShader(vertex, **kwargs)
    
    # Agregar ligera distorsión holográfica
    import time
    time_factor = time.time() * 2  # Velocidad de animación
    
    # Distorsión sutil basada en posición y tiempo
    noise_x = 0.5 * np.sin(vertex[1] * 0.1 + time_factor)
    noise_y = 0.3 * np.cos(vertex[0] * 0.1 + time_factor * 1.2)
    
    transformed_vertex[0] += noise_x
    transformed_vertex[1] += noise_y
    
    return transformed_vertex

def hologramFragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader para efecto de holograma"""
    import time
    import math
    
    # Calcular posición del fragmento
    frag_pos = [
        u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
        u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1],
        u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
    ]
    
    # Factor de tiempo para animación
    time_factor = time.time()
    
    # 1. EFECTO IRIDISCENTE - colores que cambian según posición
    hue = (frag_pos[1] * 0.01 + time_factor * 0.5) % 1.0
    
    # Convertir HSV a RGB para colores iridiscentes
    def hsv_to_rgb(h, s, v):
        h = h * 6.0
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i == 0: return [v, t, p]
        elif i == 1: return [q, v, p]
        elif i == 2: return [p, v, t]
        elif i == 3: return [p, q, v]
        elif i == 4: return [t, p, v]
        else: return [v, p, q]
    
    # Color base iridiscente
    base_color = hsv_to_rgb(hue, 0.8, 0.9)
    
    # 2. LÍNEAS DE ESCANEO horizontales
    scan_line = math.sin(frag_pos[1] * 0.5 + time_factor * 3) * 0.3 + 0.7
    
    # 3. EFECTO DE FRESNEL (bordes más brillantes)
    # Calcular normal del triángulo
    edge1 = [vertex_b[0] - vertex_a[0], vertex_b[1] - vertex_a[1], vertex_b[2] - vertex_a[2]]
    edge2 = [vertex_c[0] - vertex_a[0], vertex_c[1] - vertex_a[1], vertex_c[2] - vertex_a[2]]
    
    # Producto cruz para normal
    normal = [
        edge1[1] * edge2[2] - edge1[2] * edge2[1],
        edge1[2] * edge2[0] - edge1[0] * edge2[2],
        edge1[0] * edge2[1] - edge1[1] * edge2[0]
    ]
    
    # Normalizar
    normal_length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
    if normal_length > 0:
        normal = [n / normal_length for n in normal]
    
    # Vector hacia la cámara (simplificado)
    view_dir = [0, 0, 1]  # Asumiendo cámara mirando hacia -Z
    
    # Producto punto para efecto Fresnel
    fresnel = 1.0 - abs(normal[0] * view_dir[0] + normal[1] * view_dir[1] + normal[2] * view_dir[2])
    fresnel = fresnel ** 2  # Hacer el efecto más pronunciado
    
    # 4. EFECTO DE RUIDO/GLITCH ocasional
    noise = math.sin(frag_pos[0] * 0.7 + frag_pos[1] * 0.3 + time_factor * 4) * 0.1 + 0.9
    
    # 5. COMBINAR TODOS LOS EFECTOS
    final_color = [
        min(1.0, base_color[0] * scan_line * noise + fresnel * 0.5),
        min(1.0, base_color[1] * scan_line * noise + fresnel * 0.3),
        min(1.0, base_color[2] * scan_line * noise + fresnel * 0.8)
    ]
    
    # Asegurar que mantenga la vibración holográfica
    intensity = 0.7 + 0.3 * math.sin(time_factor * 2)
    final_color = [c * intensity for c in final_color]
    
    return final_color



def lavaVertexShader(vertex, **kwargs):
    """Vertex shader para efecto de lava con deformación"""
    import time
    import math
    
    # Usar transformaciones básicas primero
    transformed_vertex = vertexShader(vertex, **kwargs)
    
    # Factor de tiempo para animación
    time_factor = time.time() * 0.8  # Velocidad más lenta para lava
    
    # Deformación de lava - ondas que burbujean
    bubble_x = 0.3 * math.sin(vertex[1] * 0.5 + time_factor) * math.cos(vertex[2] * 0.3 + time_factor * 0.7)
    bubble_y = 0.2 * math.cos(vertex[0] * 0.4 + time_factor * 1.2) * math.sin(vertex[2] * 0.6 + time_factor)
    bubble_z = 0.15 * math.sin(vertex[0] * 0.3 + vertex[1] * 0.4 + time_factor * 1.5)
    
    # Aplicar deformación
    transformed_vertex[0] += bubble_x
    transformed_vertex[1] += bubble_y
    transformed_vertex[2] += bubble_z
    
    return transformed_vertex

def lavaFragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader para efecto de lava"""
    import time
    import math
    
    # Calcular posición del fragmento
    frag_pos = [
        u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
        u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1],
        u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
    ]
    
    # Factor de tiempo para animación
    time_factor = time.time()
    
    # 1. PATRÓN BASE DE LAVA - múltiples capas de ruido
    noise1 = math.sin(frag_pos[0] * 0.1 + frag_pos[1] * 0.15 + time_factor * 0.3)
    noise2 = math.cos(frag_pos[1] * 0.08 + frag_pos[2] * 0.12 + time_factor * 0.5)
    noise3 = math.sin(frag_pos[0] * 0.05 + frag_pos[2] * 0.07 + time_factor * 0.2)
    
    # Combinar ruidos para crear patrón de lava
    lava_pattern = (noise1 + noise2 + noise3) / 3.0
    
    # 2. GRADIENTE DE TEMPERATURA - de rojo oscuro a amarillo brillante
    temperature = (lava_pattern + 1.0) * 0.5  # Normalizar a 0-1
    
    # Agregar variación temporal para "burbujas calientes"
    hot_spots = math.sin(frag_pos[0] * 0.3 + time_factor * 2) * math.cos(frag_pos[1] * 0.25 + time_factor * 1.8)
    temperature += hot_spots * 0.3
    
    # Clamp temperatura
    temperature = max(0.0, min(1.0, temperature))
    
    # 3. MAPEO DE COLOR BASADO EN TEMPERATURA
    if temperature < 0.3:
        # Lava fría - rojo muy oscuro/negro
        base_color = [temperature * 0.8, 0.0, 0.0]
    elif temperature < 0.6:
        # Lava caliente - rojo a naranja
        t = (temperature - 0.3) / 0.3
        base_color = [0.8 + t * 0.2, t * 0.4, 0.0]
    elif temperature < 0.85:
        # Lava muy caliente - naranja a amarillo
        t = (temperature - 0.6) / 0.25
        base_color = [1.0, 0.4 + t * 0.5, t * 0.3]
    else:
        # Lava extremadamente caliente - amarillo brillante
        t = (temperature - 0.85) / 0.15
        base_color = [1.0, 0.9 + t * 0.1, 0.3 + t * 0.7]
    
    # 4. EFECTO DE BRILLO/INCANDESCENCIA
    glow_intensity = 0.7 + 0.3 * math.sin(time_factor * 1.5 + frag_pos[0] * 0.1)
    
    # 5. VENAS DE LAVA MÁS CALIENTE
    vein1 = math.sin(frag_pos[0] * 0.2 + frag_pos[1] * 0.1 + time_factor * 0.4)
    vein2 = math.cos(frag_pos[1] * 0.15 + frag_pos[2] * 0.2 + time_factor * 0.6)
    
    if abs(vein1) < 0.1 or abs(vein2) < 0.15:
        # Venas más calientes - amarillo/blanco
        base_color[0] = min(1.0, base_color[0] + 0.3)
        base_color[1] = min(1.0, base_color[1] + 0.4)
        base_color[2] = min(1.0, base_color[2] + 0.2)
        glow_intensity *= 1.5
    
    # 6. APLICAR BRILLO FINAL
    final_color = [
        min(1.0, base_color[0] * glow_intensity),
        min(1.0, base_color[1] * glow_intensity),
        min(1.0, base_color[2] * glow_intensity)
    ]
    
    return final_color