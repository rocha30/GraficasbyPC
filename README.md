# Rasterizador 2025 - Proyecto de Renderizado de Polígonos

## ✨ Descripción

Este proyecto es un rasterizador de software en Python que permite cargar modelos `.obj`, aplicar texturas y shaders personalizados, y renderizar escenas a archivos `.bmp`. El sistema utiliza un motor gráfico propio y algoritmos clásicos de gráficos por computadora para dibujar y rellenar polígonos.

---

## 🚀 Instalación y Ejecución

### Requisitos

- Python 3.7+
- Librería `pygame`
- Modelos `.obj` y texturas (`.bmp`, `.png`, `.jpg`)

### Instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repo>
   cd GraficasbyPC/Rasterizer
   ```

2. Crea y activa el entorno virtual:
   ```bash
   python3 -m venv pygame_env
   source pygame_env/bin/activate
   ```

3. Instala dependencias:
   ```bash
   pip install pygame
   ```

### Ejecución

```bash
python3 Rasterizer2025.py
```

---

## 🎮 Controles

| Tecla        | Acción                                     |
| ------------ | ------------------------------------------ |
| TAB          | Cambiar modelo seleccionado                |
| ← → ↑ ↓      | Mover modelo seleccionado (X/Y)            |
| Page Up/Down | Mover modelo en profundidad (Z)            |
| W / S        | Escalar modelo seleccionado                |
| A / D        | Rotar modelo en Y                          |
| Q / E        | Rotar modelo en Z                          |
| J / L        | Rotar cámara horizontal                    |
| I / K        | Rotar cámara vertical                      |
| U / O        | Acercar/alejar cámara                      |
| T            | Alternar entre modo shaders y modo textura |
| Z            | Mostrar/ocultar Z-buffer                   |
| G            | Mostrar/ocultar fondo                      |
| R            | Resetear modelo seleccionado               |
| C            | Resetear cámara                            |
| P            | Activar modo foto                          |
| Espacio      | Tomar foto (en modo foto)                  |
| ESC          | Salir                                      |

---

## 🔧 Componentes Principales

- **Main.py**: Script principal, configuración de escena y controles.
- **core/gl.py**: Motor de renderizado, algoritmos de dibujo y relleno.
- **core/model.py**: Clase para cargar y transformar modelos `.obj`.
- **core/Camera.py**: Sistema de cámara y proyección.
- **Shaders/shaders.py**: Shaders personalizados para efectos visuales.
- **assets/models/**: Modelos `.obj` para la escena.
- **assets/textures/**: Texturas de imagen para los modelos.

---

## 🎨 Texturas y Shaders

- Puedes aplicar texturas a cada modelo usando archivos de imagen.
- Cada modelo puede tener un shader distinto (holograma, eléctrico, lava, cristal, etc.).
- Con la tecla `T` puedes alternar entre ver solo texturas o ver los efectos de los shaders.

---

## 📚 Objetivos Académicos

- Cargar y renderizar modelos `.obj` con texturas.
- Aplicar transformaciones (traslación, rotación, escala) a cada modelo.
- Implementar y alternar shaders personalizados.
- Renderizar la escena a archivos `.bmp`.

---

## 🐛 Solución de Problemas

- **No se ven modelos**: Verifica rutas y nombres de archivos `.obj` y texturas.
- **Carga lenta**: Usa modelos con menos de 20,000 triángulos.
- **Textura incorrecta**: Revisa las coordenadas UV del modelo y el formato de la imagen.
- **Error de módulo**: Instala `pygame` y activa el entorno virtual.

---

## 📄 Licencia

Proyecto educativo. Puedes usar y modificar el código para aprender gráficos por computadora.

---

## 👨‍💻 Créditos

Desarrollado por Mario Rocha - 23501 para el curso de Gráficas por Computadora 2025.

