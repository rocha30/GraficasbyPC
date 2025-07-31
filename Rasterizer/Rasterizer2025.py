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
camera.set_position(0, 0, 10)     # Cámara alejada del origen
camera.set_target(0, 0, 0)       # Mirando al centro
camera.set_projection(45, width/height, 0.1, 50.0)

# Asignar cámara al renderer
rend.set_camera(camera)

# Cargar modelo desde archivo .obj
objModel = Model()
objModel.load_obj("centauro.obj")
objModel.scale_to_fit(2.0)  # Auto-escalar y centrar
texture_file = "centauro.bmp"  
objModel.load_texture(texture_file)  

objModel.translation = [0, 0, 0]  # Centrar en origen
objModel.vertexShader = vertexShader

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
camera_angle_h = 0  # Ángulo horizontal
camera_angle_v = 0  # Ángulo vertical

print("Controles:")
print("1, 2, 3: Cambiar modo de renderizado (POINTS, LINES, TRIANGLES)")
print("Flechas: Mover modelo")
print("A/D: Rotar modelo en Z")
print("Q/E: Rotar modelo en Y")
print("W/S: Escalar modelo")
print("I/K: Mover cámara arriba/abajo")
print("J/L: Orbitar cámara horizontalmente")
print("U/O: Acercar/alejar cámara")
print("Z: Mostrar/ocultar z-buffer")
print("R: Reset posición")
print("C: Reset cámara")
print("P: Modo automático de photoshoot (4 tomas)")
print("T: Cambiar entre textura y colores aleatorios")

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
                    print("Usando colores aleatorios")
                else:
                    objModel.load_texture(texture_file)
                    print("Usando textura")
            elif event.key == pygame.K_p:
                # Modo photoshoot automático
                auto_photo_mode = not auto_photo_mode
                if auto_photo_mode:
                    current_shot = 0
                    print("Modo photoshoot ACTIVADO - Presiona ESPACIO para siguiente toma")
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
                        print("¡Photoshoot completado! 4 imágenes guardadas.")
                        auto_photo_mode = False
                        current_shot = 0
            elif event.key == pygame.K_r:
                # Reset posición del modelo
                objModel.translation = [0, 0, 0]
                objModel.rotation = [0, 0, 0]
                objModel.scale = [1, 1, 1]
                print("Modelo reseteado")
            elif event.key == pygame.K_c:
                # Reset cámara
                camera.set_position(0, 0, 10)
                camera.set_target(0, 0, 0)
                camera_distance = 10
                camera_angle_h = 0
                camera_angle_v = 0
                print("Cámara reseteada")

    keys = pygame.key.get_pressed()

    # Solo procesar controles manuales si no estamos en modo photo
    if not auto_photo_mode:
        # Controles del modelo
        if keys[pygame.K_RIGHT]:
            objModel.translation[0] += 2 * deltaTime
        if keys[pygame.K_LEFT]:
            objModel.translation[0] -= 2 * deltaTime
        if keys[pygame.K_UP]:
            objModel.translation[1] += 2 * deltaTime
        if keys[pygame.K_DOWN]:
            objModel.translation[1] -= 2 * deltaTime

        # Controles de profundidad del modelo
        if keys[pygame.K_PAGEUP]:
            objModel.translation[2] += 2 * deltaTime
        if keys[pygame.K_PAGEDOWN]:
            objModel.translation[2] -= 2 * deltaTime

        # Controles de rotación del modelo
        if keys[pygame.K_d]:
            objModel.rotation[2] += 45 * deltaTime
        if keys[pygame.K_a]:
            objModel.rotation[2] -= 45 * deltaTime
        if keys[pygame.K_q]:
            objModel.rotation[1] += 45 * deltaTime
        if keys[pygame.K_e]:
            objModel.rotation[1] -= 45 * deltaTime

        # Controles de escala del modelo
        if keys[pygame.K_w]:
            objModel.scale = [i * (1 + deltaTime) for i in objModel.scale]
        if keys[pygame.K_s]:
            objModel.scale = [i * (1 - deltaTime) for i in objModel.scale]

        # Controles de cámara
        if keys[pygame.K_j]:  # Orbitar izquierda
            camera_angle_h -= 90 * deltaTime
        if keys[pygame.K_l]:  # Orbitar derecha
            camera_angle_h += 90 * deltaTime
        if keys[pygame.K_i]:  # Orbitar arriba
            camera_angle_v += 45 * deltaTime
            camera_angle_v = min(80, camera_angle_v)  # Limitar ángulo
        if keys[pygame.K_k]:  # Orbitar abajo
            camera_angle_v -= 45 * deltaTime
            camera_angle_v = max(-80, camera_angle_v)  # Limitar ángulo
        if keys[pygame.K_u]:  # Acercar
            camera_distance -= 5 * deltaTime
            camera_distance = max(1, camera_distance)  # No muy cerca
        if keys[pygame.K_o]:  # Alejar
            camera_distance += 5 * deltaTime

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
print("Imagen exportada como output.bmp")

pygame.quit()
