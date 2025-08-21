import pygame
import os
from core.gl import Renderer
from core.BMP_Writer import GenerateBMP
from core.model import Model
from core.Camera import Camera
from Math.MathLib import *
from Shaders.shaders import *

ASSETS_PATH = os.path.dirname(__file__)
TEXTURES_PATH = os.path.join(ASSETS_PATH, 'assets', 'textures')
MODELS_PATH = os.path.join(ASSETS_PATH, 'assets', 'models')
BACKGROUNDS_PATH = os.path.join(ASSETS_PATH, 'assets', 'backgrounds')

width = 920
height = 850 

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("Rasterizer 2025 - Escena Multi-Modelo")
clock = pygame.time.Clock()

rend = Renderer(screen)

# Cargar fondo
try:
    background_image = pygame.image.load(f"{BACKGROUNDS_PATH}/lego_star_wars.png")
    background_image = pygame.transform.scale(background_image, (width, height))
    has_background_image = True
    print(" Fondo cargado")
except:
    has_background_image = False
    print(" Sin fondo")
#confi de la camara 
camera = Camera()
camera.set_viewport(0, 0, width, height)
camera.set_position(0, 0.5, 15)  
camera.set_target(0, 0, 0)
camera.set_projection(45, width/height, 0.1, 100.0)  
rend.set_camera(camera)

#Vader
objModel1 = Model()
objModel1.load_obj(f"{MODELS_PATH}/DarthVader.obj")
objModel1.scale_to_fit(2.2)  
objModel1.load_texture(f"{TEXTURES_PATH}/Darth.bmp")
objModel1.calculate_lighting_colors()
objModel1.translation = [3, -0.5, -2]  
objModel1.vertexShader = electricVertexShader
objModel1.fragmentShader = electricFragmentShader
rend.models.append(objModel1)

#solo
objModel2 = Model()
objModel2.load_obj(f"{MODELS_PATH}/Solo.obj")
objModel2.scale_to_fit(2.2) 
objModel2.load_texture(f"{TEXTURES_PATH}/solo.bmp")
objModel2.load_texture(f"{TEXTURES_PATH}/soloc.bmp")
objModel2.calculate_lighting_colors()
objModel2.translation = [3, -0.9, 2]  
objModel2.vertexShader = lavaVertexShader 
objModel2.fragmentShader = lavaFragmentShader
objModel2.rotation = [0, 180, 0]
rend.models.append(objModel2)

#Chewbacca
objModel3 = Model()
objModel3.load_obj(f"{MODELS_PATH}/Chewbacca.obj")
objModel3.scale_to_fit(2)
objModel3.load_texture(f"{TEXTURES_PATH}/Chewbaca.bmp")
objModel3.load_texture(f"{TEXTURES_PATH}/Chebacao.bmp")
objModel3.calculate_lighting_colors()
objModel3.translation = [3, 0, 1]
objModel3.vertexShader = crystalVertexShader
objModel3.fragmentShader = crystalFragmentShader
objModel3.rotation = [0, 150, 0]

# Fix: Forzar colores si no se generaron
if len(objModel3.colors) == 0 and len(objModel3.faces) > 0:
    objModel3.colors = [[1.0, 1.0, 1.0] for _ in range(len(objModel3.faces))]

rend.models.append(objModel3)


#Anaki
objModel4 = Model()
objModel4.load_obj(f"{MODELS_PATH}/Anakin.obj")
objModel4.scale_to_fit(2)
objModel4.load_texture(f"{TEXTURES_PATH}/Aface.bmp")
objModel4.load_texture(f"{TEXTURES_PATH}/Apelo.bmp")
objModel4.load_texture(f"{TEXTURES_PATH}/Aropa.bmp")
objModel4.calculate_lighting_colors()
objModel4.translation = [7.5, -1.5, -1.5]
objModel4.vertexShader = lavaVertexShader
objModel4.fragmentShader = lavaFragmentShader
objModel4.rotation = [0, -15, 0]
rend.models.append(objModel4)

# Yoda
objModel5 = Model()
objModel5.load_obj(f"{MODELS_PATH}/YodaGhost.obj")
objModel5.scale_to_fit(2)
objModel5.load_texture(f"{TEXTURES_PATH}/Yoda.bmp")
objModel5.calculate_lighting_colors()
objModel5.translation = [1, 3, 7]
objModel5.vertexShader = hologramShader
objModel5.fragmentShader = hologramFragmentShader
objModel5.rotation = [0, -60, 0]
rend.models.append(objModel5)

# Lista de modelos para controles
models = [objModel1, objModel2, objModel3, objModel4, objModel5]
current_model_index = 0
objModel = models[current_model_index]

print(f" {len(models)} modelos cargados con colores únicos ESTÁTICOS")

# Variables para photoshoot
photo_shots = [
    {"name": "Wide_Shot", "pos": [0, 2, 25], "angle_h": 0, "angle_v": -5},
    {"name": "Low_Angle", "pos": [0, -2, 18], "angle_h": 0, "angle_v": -15},
    {"name": "High_Angle", "pos": [0, 6, 18], "angle_h": 0, "angle_v": 15},
    {"name": "Side_View", "pos": [12, 2, 12], "angle_h": 30, "angle_v": 0},
    {"name": "Close_Up", "pos": [0, 1, 12], "angle_h": 0, "angle_v": 0}
]
current_shot = 0
auto_photo_mode = False

# Controles de cámara
show_zbuffer = False
camera_distance = 20
camera_angle_h = 0
camera_angle_v = -5

show_shaders = False

# ===== BUCLE PRINCIPAL =====
isRunning = True
while isRunning:
    deltaTime = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            # ===== CONTROLES SIMPLIFICADOS =====
            
            if event.key == pygame.K_TAB:
                # Cambiar modelo controlado
                current_model_index = (current_model_index + 1) % len(models)
                objModel = models[current_model_index]
                print(f"Controlando modelo {current_model_index + 1}")
                print(f"Modelo actual: {objModel}")

            elif event.key == pygame.K_z:
                show_zbuffer = not show_zbuffer
                print(f"Z-Buffer: {'ON' if show_zbuffer else 'OFF'}")
                
            elif event.key == pygame.K_g:
                has_background_image = not has_background_image
                print(f"Fondo: {'ON' if has_background_image else 'OFF'}")
                
            elif event.key == pygame.K_r:
                # Reset modelo actual
                objModel.translation = models[current_model_index].__dict__.get('original_translation', [0, 0, 0])
                objModel.rotation = [0, 0, 0]
                objModel.scale = [1, 1, 1]
                print(f"Modelo {current_model_index + 1} reseteado")
                
            elif event.key == pygame.K_c:
                # Reset cámara
                camera.set_position(0, 0, 10)
                camera.set_target(0, 0, 0)
                camera_distance = 10
                camera_angle_h = 0
                camera_angle_v = 0
                print("Cámara reseteada")
                
            elif event.key == pygame.K_t:
                show_shaders = not show_shaders
                print("Modo shaders " if show_shaders else "Modo textura")
                
                for m in models: 
                    if show_shaders: 
                        if m == objModel1:
                            m.vertexShader = electricVertexShader
                            m.fragmentShader = electricFragmentShader
                        elif m == objModel2:
                            m.vertexShader = lavaVertexShader
                            m.fragmentShader = lavaFragmentShader
                        elif m == objModel3:
                            m.vertexShader = hologramShader
                            m.fragmentShader = hologramFragmentShader
                        elif m == objModel4:
                            m.vertexShader = electricVertexShader
                            m.fragmentShader = electricFragmentShader
                    else:
                        # Asigna shaders básicos y activa textura
                        m.vertexShader = vertexShader
                        m.fragmentShader = None
            
            elif event.key == pygame.K_h:
                objModel.vertexShader = hologramShader
                objModel.fragmentShader = hologramFragmentShader
                objModel.apply_hologram_effect()
                print(f"Shader de holograma aplicado al modelo {current_model_index + 1}")

            elif event.key == pygame.K_x:
                if hasattr(objModel, 'original_texture'):
                    objModel.texture = None if objModel.texture else objModel.original_texture
                    print(f"Textura {'OFF' if not objModel.texture else 'ON'}")

            # ===== MODO PHOTOSHOOT =====
            elif event.key == pygame.K_p:
                auto_photo_mode = not auto_photo_mode
                if auto_photo_mode:
                    current_shot = 0
                    print("🎬 Modo photoshoot ACTIVADO - Presiona ESPACIO para tomar fotos")
                else:
                    print("🎬 Modo photoshoot DESACTIVADO")
                    
            elif event.key == pygame.K_SPACE and auto_photo_mode:
                if current_shot < len(photo_shots):
                    shot = photo_shots[current_shot]
                    camera.set_position(shot["pos"][0], shot["pos"][1], shot["pos"][2])
                    camera_angle_h = shot["angle_h"]
                    camera_angle_v = shot["angle_v"]
                    camera.orbit_around_target(camera_angle_h, camera_angle_v, 
                                             ((shot["pos"][0]**2 + shot["pos"][1]**2 + shot["pos"][2]**2)**0.5))
                    
                    # Exportar screenshot
                    pygame.image.save(screen, f"Scene_{shot['name']}.png")
                    GenerateBMP(f"Scene_{shot['name']}.bmp", width, height, 3, rend.frameBuffer)
                    
                    print(f"📸 Foto {current_shot + 1}/{len(photo_shots)}: {shot['name']}")
                    current_shot += 1
                    
                    if current_shot >= len(photo_shots):
                        print("🎬 Photoshoot completado - Todas las fotos guardadas")
                        auto_photo_mode = False
                        current_shot = 0

    # ===== CONTROLES CONTINUOS =====
    keys = pygame.key.get_pressed()

    if not auto_photo_mode:
        # Controles del modelo actual
        if keys[pygame.K_RIGHT]:
            objModel.translation[0] += 3 * deltaTime
        if keys[pygame.K_LEFT]:
            objModel.translation[0] -= 3 * deltaTime
        if keys[pygame.K_UP]:
            objModel.translation[1] += 3 * deltaTime
        if keys[pygame.K_DOWN]:
            objModel.translation[1] -= 3 * deltaTime
        if keys[pygame.K_PAGEUP]:
            objModel.translation[2] += 3 * deltaTime
        if keys[pygame.K_PAGEDOWN]:
            objModel.translation[2] -= 3 * deltaTime

        # Rotación del modelo
        if keys[pygame.K_d]:
            objModel.rotation[1] += 45 * deltaTime
        if keys[pygame.K_a]:
            objModel.rotation[1] -= 45 * deltaTime
        if keys[pygame.K_q]:
            objModel.rotation[2] += 45 * deltaTime
        if keys[pygame.K_e]:
            objModel.rotation[2] -= 45 * deltaTime

        # Escala del modelo
        if keys[pygame.K_w]:
            objModel.scale = [i * (1 + 0.5 * deltaTime) for i in objModel.scale]
        if keys[pygame.K_s]:
            objModel.scale = [i * (1 - 0.5 * deltaTime) for i in objModel.scale]

        # Controles de cámara
        if keys[pygame.K_j]:
            camera_angle_h -= 45 * deltaTime
        if keys[pygame.K_l]:
            camera_angle_h += 45 * deltaTime
        if keys[pygame.K_i]:
            camera_angle_v += 30 * deltaTime
            camera_angle_v = min(80, camera_angle_v)
        if keys[pygame.K_k]:
            camera_angle_v -= 30 * deltaTime
            camera_angle_v = max(-80, camera_angle_v)
        if keys[pygame.K_u]:
            camera_distance -= 5 * deltaTime
            camera_distance = max(2, camera_distance)
        if keys[pygame.K_o]:
            camera_distance += 5 * deltaTime

        camera.orbit_around_target(camera_angle_h, camera_angle_v, camera_distance)

    # ===== RENDERIZADO =====
    if has_background_image:
        screen.blit(background_image, (0, 0))
        rend.has_background_active = True
    else:
        rend.has_background_active = False

    if show_zbuffer:
        rend.glRender()
        rend.glRenderZBuffer()
    else:
        rend.glRender()

    pygame.display.flip()

# Exportar imagen final
GenerateBMP("Final_Scene.bmp", width, height, 3, rend.frameBuffer)
print(" Escena final guardada como Final_Scene.bmp")

pygame.quit()
