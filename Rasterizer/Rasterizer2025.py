import pygame
from gl import *
from BMP_Writer import GenerateBMP
from model import Model
from shaders import *
from Camera import *

width = 720
height = 720 

screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("Rasterizer 2025 - Modelo 3D OBJ Texturizado con Cámara")
clock = pygame.time.Clock()

rend = Renderer(screen)

# Crear y configurar cámara
camera = Camera()
camera.set_viewport(0, 0, width, height)
camera.set_position(0, 0, 8)     # Cámara alejada del origen
camera.set_target(0, 0, 0)       # Mirando al centro
camera.set_projection(45, width/height, 0.1, 50.0)

# Asignar cámara al renderer
rend.set_camera(camera)

# Cargar modelo desde archivo .obj
objModel = Model()
objModel.load_obj("centauro.obj")  # Cambiar a modelo más simple
objModel.scale_to_fit(4.0)  # Auto-escalar y centrar

objModel.load_texture("texura.bmp")  # Cargar textura

# Calcular iluminación
objModel.calculate_lighting_colors()

objModel.translation = [0, -1.5, 0]  # Centrar en origen
objModel.vertexShader = vertexShader  # Usar shader básico (lighting ya está en colores)

rend.models.append(objModel)

# Variables para photoshoot automático
photo_shots = [
    {"name": "Medium_Shot", "pos": [0, 0, 8], "angle_h": 0, "angle_v": 0},
    {"name": "Low_Angle", "pos": [0, -3, 6], "angle_h": 0, "angle_v": -30},
    {"name": "High_Angle", "pos": [0, 3, 6], "angle_h": 0, "angle_v": 30},
    {"name": "Dutch_Angle", "pos": [3, 0, 6], "angle_h": 30, "angle_v": 0}
]
current_shot = 0
auto_photo_mode = False

# Controles adicionales
show_zbuffer = False
camera_distance = 10
camera_angle_h = 0  
camera_angle_v = 0  

isRunning = True
while isRunning:
    deltaTime = clock.tick(60)/ 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                rend.primitiveType = POINTS
                print("Modo: POINTS")
            elif event.key == pygame.K_2:
                rend.primitiveType = LINES
                print("Modo: LINES")
            elif event.key == pygame.K_3:
                rend.primitiveType = TRIANGLES
                print("Modo: TRIANGLES")
            elif event.key == pygame.K_z:
                show_zbuffer = not show_zbuffer
                print(f"Z-Buffer: {'ON' if show_zbuffer else 'OFF'}")
            elif event.key == pygame.K_t:
                # Toggle entre textura y colores
                if hasattr(objModel, 'texture') and objModel.texture:
                    objModel.texture = None
                    
                else:
                    objModel.load_texture("lava.bmp")  
                    
            elif event.key == pygame.K_p:
                # Modo photoshoot automático
                auto_photo_mode = not auto_photo_mode
                if auto_photo_mode:
                    current_shot = 0
                    
                else:
                    print("Modo photoshoot DESACTIVADO")
                    
            elif event.key == pygame.K_SPACE and auto_photo_mode:
                # Siguiente toma en modo photoshoot
                if current_shot < len(photo_shots):
                    shot = photo_shots[current_shot]
                    camera.set_position(shot["pos"][0], shot["pos"][1], shot["pos"][2])
                    camera_angle_h = shot["angle_h"]
                    camera_angle_v = shot["angle_v"]
                    camera.orbit_around_target(camera_angle_h, camera_angle_v, 
                                             ((shot["pos"][0]**2 + shot["pos"][1]**2 + shot["pos"][2]**2)**0.5))
                    
                    # Exportar screenshot
                    pygame.image.save(screen, f"{shot['name']}.png")
                    GenerateBMP(f"{shot['name']}.bmp", width, height, 3, rend.frameBuffer)
                    
                    print(f"Toma {current_shot + 1}/4: {shot['name']} - Imagen guardada")
                    current_shot += 1
                    
                    if current_shot >= len(photo_shots):
                        
                        auto_photo_mode = False
                        current_shot = 0
            elif event.key == pygame.K_r:
                # Reset posición del modelo
                objModel.translation = [0, 0, 0]
                objModel.rotation = [0, 0, 0]
                objModel.scale = [1, 1, 1]
                
            elif event.key == pygame.K_c:
                # Reset cámara
                camera.set_position(0, 0, 10)
                camera.set_target(0, 0, 0)
                camera_distance = 10
                camera_angle_h = 0
                camera_angle_v = 0
                
            elif event.key == pygame.K_l:
                # Recalcular iluminación
                objModel.calculate_lighting_colors()
            
            
            elif event.key == pygame.K_f:
                
                from shaders import resetToDefaultShaders, lightingVertexShader, fragmentShaderWithBarycentric
                resetToDefaultShaders(objModel)  # Limpiar primero
                
                # Aplicar nuevos shaders
                objModel.vertexShader = lightingVertexShader
                objModel.fragmentShader = fragmentShaderWithBarycentric
                print("Iluminación avanzada aplicada! (Vertex + Fragment)")
                
            elif event.key == pygame.K_v:
                
                from shaders import resetToDefaultShaders, lavaVertexShader, lavaFragmentShader
                resetToDefaultShaders(objModel)  # Limpiar primero
                
                
                objModel.vertexShader = lavaVertexShader
                objModel.fragmentShader = lavaFragmentShader
                print("Shader de lava aplicado! El modelo ahora parece lava derretida")
                
            elif event.key == pygame.K_b:
                # DEBUG: Verificar que las funciones existen
                try:
                    from shaders import resetToDefaultShaders, hologramShader, hologramFragmentShader
                    print("✓ Shaders importados correctamente")
                    
                    resetToDefaultShaders(objModel)
                    print("✓ Reset completado")
                    
                    objModel.texture = None
                    objModel.vertexShader = hologramShader
                    objModel.fragmentShader = hologramFragmentShader
                    
                    print("✓ Shaders asignados")
                    print(f"Fragment shader es: {objModel.fragmentShader}")
                    
                except ImportError as e:
                    print(f"ERROR: No se pueden importar shaders: {e}")
                except Exception as e:
                    print(f"ERROR: {e}")
                
            elif event.key == pygame.K_0:
                # MODO BÁSICO: LIMPIAR TODO
                from shaders import resetToDefaultShaders
                resetToDefaultShaders(objModel)  # Limpiar shaders
                
                # Remover textura y crear colores simples
                objModel.texture = None
                objModel.colors = []
                for i in range(len(objModel.faces)):
                    if i % 4 == 0:
                        objModel.colors.append([1.0, 0.0, 0.0])  # Rojo
                    elif i % 4 == 1:
                        objModel.colors.append([0.0, 1.0, 0.0])  # Verde  
                    elif i % 4 == 2:
                        objModel.colors.append([0.0, 0.0, 1.0])  # Azul
                    else:
                        objModel.colors.append([1.0, 1.0, 0.0])  # Amarillo
                print("Modo básico: colores sólidos sin shaders")
                
            elif event.key == pygame.K_m: 
                try: 
                    from shaders import resetToDefaultShaders, crystalVertexShader, crystalFragmentShader
                    resetToDefaultShaders(objModel)  # Limpiar primero
                    
                    objModel.texture = None 
                    objModel.vertexShader = crystalVertexShader
                    objModel.fragmentShader = crystalFragmentShader
                    print("Shader de cristal aplicado! El modelo ahora parece un cristal brillante")
                except ImportError as e:
                    print(f"ERROR: No se pueden importar shaders: {e}")
                except Exception as e:
                    print(f"ERROR: {e}")



    keys = pygame.key.get_pressed()

    # Solo procesar controles manuales si no estamos en modo photo
    if not auto_photo_mode:
        # Controles del modelo (más suaves)
        if keys[pygame.K_RIGHT]:
            objModel.translation[0] += 0.5 * deltaTime  # Reducido de 2 a 0.5
        if keys[pygame.K_LEFT]:
            objModel.translation[0] -= 0.5 * deltaTime  # Reducido de 2 a 0.5
        if keys[pygame.K_UP]:
            objModel.translation[1] += 0.5 * deltaTime  # Reducido de 2 a 0.5
        if keys[pygame.K_DOWN]:
            objModel.translation[1] -= 0.5 * deltaTime  # Reducido de 2 a 0.5

        # Controles de profundidad del modelo
        if keys[pygame.K_PAGEUP]:
            objModel.translation[2] += 0.5 * deltaTime  # Reducido de 2 a 0.5
        if keys[pygame.K_PAGEDOWN]:
            objModel.translation[2] -= 0.5 * deltaTime  # Reducido de 2 a 0.5

        # Controles de rotación del modelo (más suaves)
        if keys[pygame.K_d]:
            objModel.rotation[2] += 15 * deltaTime  # Reducido de 45 a 15
        if keys[pygame.K_a]:
            objModel.rotation[2] -= 15 * deltaTime  # Reducido de 45 a 15
        if keys[pygame.K_q]:
            objModel.rotation[1] += 15 * deltaTime  # Reducido de 45 a 15
        if keys[pygame.K_e]:
            objModel.rotation[1] -= 15 * deltaTime  # Reducido de 45 a 15

        # Controles de escala del modelo (más suaves)
        if keys[pygame.K_w]:
            objModel.scale = [i * (1 + 0.3 * deltaTime) for i in objModel.scale]  # Reducido el factor
        if keys[pygame.K_s]:
            objModel.scale = [i * (1 - 0.3 * deltaTime) for i in objModel.scale]  # Reducido el factor

        # Controles de cámara (mucho más suaves)
        if keys[pygame.K_j]:  # Orbitar izquierda
            camera_angle_h -= 20 * deltaTime  # Reducido de 90 a 20
        if keys[pygame.K_l]:  # Orbitar derecha
            camera_angle_h += 20 * deltaTime  # Reducido de 90 a 20
        if keys[pygame.K_i]:  # Orbitar arriba
            camera_angle_v += 10 * deltaTime  # Reducido de 45 a 10
            camera_angle_v = min(80, camera_angle_v)  # Limitar ángulo
        if keys[pygame.K_k]:  # Orbitar abajo
            camera_angle_v -= 10 * deltaTime  # Reducido de 45 a 10
            camera_angle_v = max(-80, camera_angle_v)  # Limitar ángulo
        if keys[pygame.K_u]:  # Acercar
            camera_distance -= 1.5 * deltaTime  # Reducido de 5 a 1.5
            camera_distance = max(1, camera_distance)  # No muy cerca
        if keys[pygame.K_o]:  # Alejar
            camera_distance += 1.5 * deltaTime  # Reducido de 5 a 1.5


        # Actualizar posición de cámara usando órbita
        camera.orbit_around_target(camera_angle_h, camera_angle_v, camera_distance)

    # Renderizar
    rend.glClear()
    
    if show_zbuffer:
        # Renderizar normalmente primero
        rend.glRender()
        # Luego mostrar z-buffer
        rend.glRenderZBuffer()
    else:
        # Renderizado normal
        rend.glRender()

    pygame.display.flip()

# Exportar imagen final
GenerateBMP("output.bmp", width, height, 3, rend.frameBuffer)


pygame.quit()
