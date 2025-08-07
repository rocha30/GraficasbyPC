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


def fragmentShaderWithBarycentric(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader que usa coordenadas baricéntricas para iluminación suave"""
    import math
    
    try:
        # Obtener modelo del kwargs
        model = kwargs.get('model')
        face_idx = kwargs.get('face_idx')
        
        # Color base
        base_colors = [
            [1.0, 0.8, 0.6],  # Naranja cálido
            [0.8, 1.0, 0.6],  # Verde claro
            [0.6, 0.8, 1.0],  # Azul claro
            [1.0, 0.6, 0.8],  # Rosa
            [0.9, 0.9, 0.7],  # Amarillo suave
        ]
        
        # Seleccionar color base según índice de cara
        if face_idx is not None:
            base_color = base_colors[face_idx % len(base_colors)]
        else:
            base_color = [0.9, 0.7, 0.5]  # Naranja por defecto
        
        # Si hay colores de lighting precalculados, MEZCLARLOS con el color base
        if model and hasattr(model, 'colors') and face_idx is not None and face_idx < len(model.colors):
            lighting_color = model.colors[face_idx]
            # Mezclar colores en lugar de reemplazar
            base_color = [
                (base_color[0] + lighting_color[0]) * 0.5,
                (base_color[1] + lighting_color[1]) * 0.5,
                (base_color[2] + lighting_color[2]) * 0.5
            ]
        
        # Calcular posición del fragmento usando coordenadas baricéntricas
        frag_pos = [
            u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
            u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1], 
            u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
        ]
        
        # ILUMINACIÓN MÁS FUERTE
        # Simular múltiples luces
        light_dirs = [
            [-1, 1, 1],   # Luz principal
            [1, 0.5, 0.8], # Luz de relleno
            [0, -1, 0.5]   # Luz desde abajo
        ]
        
        # Calcular normal del triángulo
        edge1 = [vertex_b[0] - vertex_a[0], vertex_b[1] - vertex_a[1], vertex_b[2] - vertex_a[2]]
        edge2 = [vertex_c[0] - vertex_a[0], vertex_c[1] - vertex_a[1], vertex_c[2] - vertex_a[2]]
        
        # Producto cruz para normal
        normal = [
            edge1[1] * edge2[2] - edge1[2] * edge2[1],
            edge1[2] * edge2[0] - edge1[0] * edge2[2], 
            edge1[0] * edge2[1] - edge1[1] * edge2[0]
        ]
        
        # Normalizar normal
        normal_length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
        if normal_length > 0:
            normal = [n / normal_length for n in normal]
        else:
            normal = [0, 0, 1]  # Normal por defecto
        
        # Calcular iluminación de múltiples fuentes
        total_lighting = 0.5  # Luz ambiente más fuerte
        
        for light_dir in light_dirs:
            # Normalizar dirección de luz
            light_length = (light_dir[0]**2 + light_dir[1]**2 + light_dir[2]**2)**0.5
            light_dir_norm = [l / light_length for l in light_dir]
            
            # Producto punto para intensidad de luz
            dot_product = max(0, normal[0] * light_dir_norm[0] + normal[1] * light_dir_norm[1] + normal[2] * light_dir_norm[2])
            total_lighting += dot_product * 0.4  # Cada luz contribuye menos
        
        # Asegurar que la iluminación no sea demasiado baja
        total_lighting = max(0.6, min(1.3, total_lighting))
        
        # VARIACIÓN ESPACIAL para más interés visual
        spatial_variation = 0.1 * math.sin(frag_pos[0] * 0.1) * math.cos(frag_pos[1] * 0.08)
        total_lighting += spatial_variation
        
        # Aplicar iluminación al color base
        final_color = [
            min(1.0, base_color[0] * total_lighting),
            min(1.0, base_color[1] * total_lighting),
            min(1.0, base_color[2] * total_lighting)
        ]
        
        return final_color
        
    except Exception as e:
        print(f"Error en fragmentShaderWithBarycentric: {e}")
        return [1.0, 0.7, 0.4]  # Naranja cálido por defecto en lugar de gris
    
    
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
    """Vertex shader con distorsión más variada"""
    transformed_vertex = vertexShader(vertex, **kwargs)
    
    import time
    import math
    time_factor = time.time() * 1.2
    
    # MÚLTIPLES FRECUENCIAS para crear distorsión más interesante
    # Ondas grandes (movimiento principal)
    big_wave_x = 2.0 * math.sin(vertex[1] * 0.02 + time_factor)
    big_wave_y = 1.5 * math.cos(vertex[0] * 0.015 + time_factor * 0.8)
    
    # Ondas medianas (detalle)
    med_wave_x = 1.0 * math.sin(vertex[1] * 0.08 + time_factor * 1.5)
    med_wave_y = 0.8 * math.cos(vertex[0] * 0.06 + time_factor * 1.2)
    
    # Ondas pequeñas (textura)
    small_wave_x = 0.3 * math.sin(vertex[1] * 0.2 + time_factor * 2.0)
    small_wave_y = 0.2 * math.cos(vertex[0] * 0.25 + time_factor * 2.5)
    
    # COMBINAR todas las ondas
    total_noise_x = big_wave_x + med_wave_x + small_wave_x
    total_noise_y = big_wave_y + med_wave_y + small_wave_y
    
    # Distorsión en Z más sutil
    noise_z = 0.5 * math.sin(vertex[0] * 0.05 + vertex[1] * 0.03 + time_factor * 0.9)
    
    transformed_vertex[0] += total_noise_x
    transformed_vertex[1] += total_noise_y
    transformed_vertex[2] += noise_z
    
    return transformed_vertex

def hologramFragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader para holograma con variación POR FRAGMENTO"""
    import time
    import math
    
    # Calcular posición del fragmento
    frag_pos = [
        u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
        u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1], 
        u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
    ]
    
    time_factor = time.time()
    
    # AUMENTAR VARIACIÓN ESPACIAL - cada área tendrá colores diferentes
    # Usar múltiples factores para crear patrones más complejos
    spatial_factor1 = frag_pos[0] * 0.05 + frag_pos[1] * 0.03  # Era 0.01, ahora 0.05
    spatial_factor2 = frag_pos[1] * 0.04 + frag_pos[2] * 0.06
    spatial_factor3 = frag_pos[0] * 0.03 + frag_pos[2] * 0.04
    
    # MÚLTIPLES ONDAS DE COLOR que se mueven por el modelo
    color_wave1 = (time_factor * 0.5 + spatial_factor1) % 1.0
    color_wave2 = (time_factor * 0.7 + spatial_factor2) % 1.0  
    color_wave3 = (time_factor * 0.3 + spatial_factor3) % 1.0
    
    # CALCULAR COMPONENTES RGB usando las ondas
    red_component = 0.3 + 0.7 * math.sin(color_wave1 * 6.28)      # 0.3 a 1.0
    green_component = 0.3 + 0.7 * math.cos(color_wave2 * 6.28)    # 0.3 a 1.0  
    blue_component = 0.3 + 0.7 * math.sin(color_wave3 * 6.28 + 2.1)  # 0.3 a 1.0 con offset
    
    # NORMALIZAR para evitar colores demasiado oscuros
    total = red_component + green_component + blue_component
    if total > 0:
        red_component = red_component / total * 1.8    # Amplificar
        green_component = green_component / total * 1.8
        blue_component = blue_component / total * 1.8
    
    # EFECTO DE PARPADEO/INTENSIDAD
    intensity = 0.6 + 0.4 * math.sin(time_factor * 3 + spatial_factor1 * 10)
    
    # LÍNEAS DE ESCANEO que se mueven
    scan_effect = 1.0
    scan_line = math.sin(frag_pos[1] * 0.1 + time_factor * 8) 
    if scan_line > 0.8:
        scan_effect = 1.5  # Líneas más brillantes
    elif scan_line < -0.8:
        scan_effect = 0.7  # Líneas más oscuras
    
    # COLOR FINAL con variación suave
    final_color = [
        min(1.0, red_component * intensity * scan_effect),
        min(1.0, green_component * intensity * scan_effect),
        min(1.0, blue_component * intensity * scan_effect)
    ]
    
    for i in range(3):
        if not (0.0 <= final_color[i] <= 1.0):
            final_color[i] = 0.5
    
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

def resetToDefaultShaders(model):
    """Resetear modelo a shaders por defecto (limpio)"""
    model.vertexShader = vertexShader  # Shader básico
    model.fragmentShader = None        # Sin fragment shader personalizado
    
    # LIMPIAR TEXTURA TAMBIÉN para evitar interferencias
    model.texture = None
    
    # Restaurar colores de iluminación originales si existen
    if hasattr(model, 'original_lighting_colors'):
        model.colors = model.original_lighting_colors.copy()
    else:
        # Recalcular iluminación básica
        model.calculate_lighting_colors()
    
    print("Shaders y textura reseteados a configuración básica")

def crystalVertexShader(vertex, **kwargs):
    """Vertex shader para efecto de cristal mágico con facetas"""
    import time
    import math
    
    # Usar transformaciones básicas primero
    transformed_vertex = vertexShader(vertex, **kwargs)
    
    # Factor de tiempo más lento para cristal
    time_factor = time.time() * 0.6
    
    # EFECTO DE CRISTALIZACIÓN - pequeñas rotaciones facetadas
    # Crear "facetas" basadas en la posición del vértice
    facet_id = int((vertex[0] + vertex[1] + vertex[2]) * 0.5) % 8  # 8 facetas diferentes
    
    # Rotación sutil para cada faceta
    facet_rotation = facet_id * 0.785  # 45 grados por faceta
    
    # Movimiento de cristal flotante muy sutil
    float_x = 0.1 * math.sin(time_factor + facet_rotation)
    float_y = 0.08 * math.cos(time_factor * 0.8 + facet_rotation * 0.5)
    float_z = 0.05 * math.sin(time_factor * 1.2 + facet_rotation * 0.7)
    
    # BRILLO CRISTALINO - pequeñas expansiones en las puntas
    distance_from_center = (vertex[0]**2 + vertex[1]**2 + vertex[2]**2)**0.5
    sparkle_factor = 0.02 * math.sin(time_factor * 3 + distance_from_center * 2)
    
    # Aplicar efectos
    transformed_vertex[0] += float_x + sparkle_factor
    transformed_vertex[1] += float_y + sparkle_factor
    transformed_vertex[2] += float_z + sparkle_factor
    
    return transformed_vertex

def crystalFragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader para cristal mágico con efectos iridiscentes"""
    import time
    import math
    
    try:
        # Calcular posición del fragmento
        frag_pos = [
            u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
            u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1], 
            u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
        ]
        
        time_factor = time.time()
        
        # 1. EFECTO FRESNEL - bordes más brillantes
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
        
        # Vector vista (simplificado)
        view_dir = [0, 0, 1]  # Mirando hacia Z
        
        # Producto punto para Fresnel
        fresnel = abs(normal[0] * view_dir[0] + normal[1] * view_dir[1] + normal[2] * view_dir[2])
        fresnel = 1.0 - fresnel  # Invertir para que bordes sean más brillantes
        
        # 2. IRIDISCENCIA - colores que cambian según ángulo y posición
        # Usar la posición y normal para crear variación de color
        iridescent_factor = (frag_pos[0] * 0.1 + frag_pos[1] * 0.08 + frag_pos[2] * 0.12 + time_factor * 0.5) % 1.0
        
        # Mapeo de colores iridiscentes (como prisma)
        if iridescent_factor < 0.16:  # Rojo
            base_color = [1.0, 0.3, 0.5]
        elif iridescent_factor < 0.33:  # Naranja
            base_color = [1.0, 0.6, 0.2]
        elif iridescent_factor < 0.5:   # Amarillo
            base_color = [1.0, 1.0, 0.3]
        elif iridescent_factor < 0.66:  # Verde
            base_color = [0.3, 1.0, 0.5]
        elif iridescent_factor < 0.83:  # Azul
            base_color = [0.3, 0.7, 1.0]
        else:  # Morado
            base_color = [0.8, 0.3, 1.0]
        
        # 3. EFECTOS DE CRISTAL
        # Reflexos internos
        internal_reflection = 0.3 + 0.2 * math.sin(frag_pos[0] * 0.5 + frag_pos[1] * 0.3 + time_factor * 2)
        
        # Partículas de luz flotantes
        light_particles = 0.0
        for i in range(3):  # 3 partículas
            particle_x = 20 * math.sin(time_factor * (0.8 + i * 0.3) + i * 2.1)
            particle_y = 15 * math.cos(time_factor * (1.0 + i * 0.2) + i * 1.5)
            distance = ((frag_pos[0] - particle_x)**2 + (frag_pos[1] - particle_y)**2)**0.5
            if distance < 5:
                light_particles += (5 - distance) / 5 * 0.3
        
        # 4. BRILLO CRISTALINO
        crystal_glow = 0.4 + 0.3 * math.sin(time_factor * 1.8 + frag_pos[2] * 0.1)
        
        # 5. COMBINACIÓN FINAL
        # Base iridiscente
        final_color = [
            base_color[0] * (0.6 + internal_reflection),
            base_color[1] * (0.6 + internal_reflection),
            base_color[2] * (0.6 + internal_reflection)
        ]
        
        # Aplicar Fresnel (bordes brillantes)
        fresnel_boost = 1.0 + fresnel * 1.5
        final_color = [c * fresnel_boost for c in final_color]
        
        # Agregar partículas de luz
        final_color = [c + light_particles for c in final_color]
        
        # Aplicar brillo cristalino
        final_color = [c * crystal_glow for c in final_color]
        
        # Clamp final
        final_color = [max(0.0, min(1.0, c)) for c in final_color]
        
        return final_color
        
    except Exception as e:
        print(f"Error en crystalFragmentShader: {e}")
        return [0.8, 0.9, 1.0]  # Azul cristal por defecto

def electricVertexShader(vertex, **kwargs):
    """Vertex shader para efecto de tormenta eléctrica con sacudidas"""
    import time
    import math
    import random
    
    # Usar transformaciones básicas primero
    transformed_vertex = vertexShader(vertex, **kwargs)
    
    # Factor de tiempo rápido para efectos eléctricos
    time_factor = time.time() * 4
    
    # SACUDIDAS ELÉCTRICAS - movimiento errático y rápido
    # Usar posición del vértice como seed para randomness consistente
    vertex_seed = int((vertex[0] + vertex[1] + vertex[2]) * 100) % 1000
    
    # Pulsos eléctricos principales - grandes y espasmódicos
    electric_pulse = math.sin(time_factor * 3 + vertex_seed * 0.01)
    if electric_pulse > 0.7:  # Solo en picos altos
        # Sacudida fuerte cuando hay "descarga"
        shock_x = 3.0 * math.sin(time_factor * 15 + vertex_seed * 0.1)
        shock_y = 2.5 * math.cos(time_factor * 12 + vertex_seed * 0.15) 
        shock_z = 1.5 * math.sin(time_factor * 18 + vertex_seed * 0.08)
    else:
        # Movimiento eléctrico sutil entre descargas
        shock_x = 0.3 * math.sin(time_factor * 8 + vertex_seed * 0.05)
        shock_y = 0.25 * math.cos(time_factor * 6 + vertex_seed * 0.07)
        shock_z = 0.2 * math.sin(time_factor * 10 + vertex_seed * 0.04)
    
    # ARCOS ELÉCTRICOS - conectar vértices cercanos con distorsión
    arc_factor = 0.5 * math.sin(time_factor * 2 + vertex[0] * 0.1 + vertex[1] * 0.08)
    
    # Aplicar efectos eléctricos
    transformed_vertex[0] += shock_x + arc_factor
    transformed_vertex[1] += shock_y + arc_factor * 0.5
    transformed_vertex[2] += shock_z + arc_factor * 0.3
    
    return transformed_vertex

def electricFragmentShader(vertex_a, vertex_b, vertex_c, u, v, w, **kwargs):
    """Fragment shader para tormenta eléctrica con rayos y chispas"""
    import time
    import math
    import random
    
    try:
        # Calcular posición del fragmento
        frag_pos = [
            u * vertex_a[0] + v * vertex_b[0] + w * vertex_c[0],
            u * vertex_a[1] + v * vertex_b[1] + w * vertex_c[1], 
            u * vertex_a[2] + v * vertex_b[2] + w * vertex_c[2]
        ]
        
        time_factor = time.time()
        
        # 1. BASE ELÉCTRICA - azul profundo con variaciones
        base_electric = [0.1, 0.3, 0.8]  # Azul eléctrico base
        
        # 2. RAYOS ELÉCTRICOS - líneas brillantes que aparecen/desaparecen
        # Crear patrones de rayos usando funciones trigonométricas
        lightning_pattern1 = math.sin(frag_pos[0] * 0.5 + frag_pos[1] * 0.3 + time_factor * 8)
        lightning_pattern2 = math.cos(frag_pos[1] * 0.7 + frag_pos[2] * 0.4 + time_factor * 12)
        lightning_pattern3 = math.sin(frag_pos[0] * 0.3 + frag_pos[2] * 0.6 + time_factor * 6)
        
        # Detectar "rayos" donde los patrones se alinean
        lightning_intensity = 0.0
        
        # Rayo horizontal
        if abs(lightning_pattern1) > 0.85:
            lightning_intensity += 0.6
            
        # Rayo vertical  
        if abs(lightning_pattern2) > 0.9:
            lightning_intensity += 0.8
            
        # Rayo diagonal
        if abs(lightning_pattern3) > 0.88:
            lightning_intensity += 0.5
            
        # Rayos que se cruzan = descarga mayor
        if abs(lightning_pattern1) > 0.85 and abs(lightning_pattern2) > 0.85:
            lightning_intensity += 1.2
        
        # 3. PULSOS ELÉCTRICOS - toda la superficie pulsa
        electric_pulse = 0.3 + 0.4 * math.sin(time_factor * 4)
        super_pulse = 0.0
        
        # Super pulso ocasional (como relámpago mayor)
        pulse_trigger = math.sin(time_factor * 0.8)
        if pulse_trigger > 0.85:
            super_pulse = 0.8 * (pulse_trigger - 0.85) / 0.15  # 0 a 0.8
        
        # 4. ARCOS ELÉCTRICOS - conexiones entre puntos
        arc_distance = ((frag_pos[0] % 10)**2 + (frag_pos[1] % 8)**2)**0.5
        arc_pattern = math.sin(arc_distance * 0.8 + time_factor * 10)
        
        arc_intensity = 0.0
        if arc_pattern > 0.75:
            arc_intensity = (arc_pattern - 0.75) / 0.25 * 0.4  # 0 a 0.4
        
        # 5. CHISPAS - puntos brillantes aleatorios
        spark_seed = int((frag_pos[0] + frag_pos[1] + frag_pos[2]) * 50) % 100
        spark_time = (time_factor * 20 + spark_seed) % 3.14159
        
        spark_intensity = 0.0
        if math.sin(spark_time) > 0.95:  # Chispas muy esporádicas
            spark_intensity = 0.6
        
        # 6. COMBINACIÓN DE COLORES
        # Color base eléctrico
        electric_blue = [0.1 + electric_pulse * 0.3, 0.4 + electric_pulse * 0.4, 0.9 + electric_pulse * 0.1]
        
        # Rayos = azul brillante a blanco
        if lightning_intensity > 0:
            # Transición azul eléctrico → blanco según intensidad
            lightning_white = min(1.0, lightning_intensity)
            electric_blue[0] += lightning_white * 0.8  # Más rojo para blanco
            electric_blue[1] += lightning_white * 0.6  # Más verde para blanco
            electric_blue[2] = min(1.0, electric_blue[2] + lightning_white * 0.1)
        
        # Super pulso = blanco puro
        if super_pulse > 0:
            electric_blue = [
                min(1.0, electric_blue[0] + super_pulse * 0.9),
                min(1.0, electric_blue[1] + super_pulse * 0.9), 
                min(1.0, electric_blue[2] + super_pulse * 0.9)
            ]
        
        # Arcos = azul cyan brillante
        if arc_intensity > 0:
            electric_blue[1] = min(1.0, electric_blue[1] + arc_intensity)  # Más verde
            electric_blue[2] = min(1.0, electric_blue[2] + arc_intensity * 0.5)
        
        # Chispas = blanco puro
        if spark_intensity > 0:
            electric_blue = [
                min(1.0, electric_blue[0] + spark_intensity),
                min(1.0, electric_blue[1] + spark_intensity),
                min(1.0, electric_blue[2] + spark_intensity)
            ]
        
        # 7. INTENSIDAD FINAL
        final_intensity = 0.6 + electric_pulse + lightning_intensity + arc_intensity + spark_intensity + super_pulse
        final_intensity = min(1.0, final_intensity)
        
        final_color = [
            electric_blue[0] * final_intensity,
            electric_blue[1] * final_intensity,
            electric_blue[2] * final_intensity
        ]
        
        # Clamp final
        final_color = [max(0.0, min(1.0, c)) for c in final_color]
        
        return final_color
        
    except Exception as e:
        print(f"Error en electricFragmentShader: {e}")
        return [0.1, 0.5, 1.0]  # Azul eléctrico por defecto


