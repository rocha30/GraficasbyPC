# Rasterizador 2025 - Proyecto de Renderizado de Polígonos

Un motor de rasterización 2D personalizado construido con Python y Pygame, que incluye sistemas de coordenadas matemáticas y algoritmos de relleno de polígonos por líneas de barrido.

## 🎯 Descripción del Proyecto

Este proyecto implementa un rasterizador de software desde cero, capaz de renderizar y rellenar polígonos complejos usando algoritmos gráficos personalizados. El renderizador usa un sistema de coordenadas con origen en la esquina inferior izquierda (coordenadas matemáticas) en lugar de la convención típica de gráficos por computadora (superior izquierda).

## ✨ Características

- **Renderizado de Polígonos Personalizado**: Dibuja y rellena polígonos complejos con múltiples vértices
- **Sistema de Coordenadas Matemáticas**: (0,0) comienza en la esquina inferior izquierda como en matemáticas
- **Algoritmo de Relleno por Líneas de Barrido**: Relleno eficiente de polígonos usando tablas de aristas
- **Soporte para Múltiples Polígonos**: Renderiza múltiples polígonos con diferentes colores simultáneamente
- **Algoritmo de Líneas de Bresenham**: Trazado eficiente de líneas para contornos de polígonos
- **Gestión de Framebuffer**: Framebuffer personalizado para control a nivel de píxel

## 🚀 Comenzando

### Requisitos Previos

- Python 3.7+
- Librería pygame

### Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd /ruta/a/tu/proyecto/Rasterizer
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv pygame_env
   ```

3. **Activar entorno virtual**
   ```bash
   source pygame_env/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install pygame
   ```

### Ejecutar el Proyecto

#### Rasterizador Básico
```bash
source pygame_env/bin/activate && python3 Rasterizer2025.py
```

#### Versión Avanzada del Lab (con controles interactivos)
```bash
cd Lab1 && source ../pygame_env/bin/activate && python3 main.py
```

## 🎮 Controles (Versión Lab1)

- **ESPACIO**: Alternar entre polígonos individuales
- **B**: Mostrar/ocultar ambos polígonos simultáneamente
- **F**: Alternar entre modo relleno y contorno
- **V**: Mostrar/ocultar marcadores de vértices
- **ESC/Cerrar**: Salir de la aplicación

## 📁 Estructura del Proyecto

```
Rasterizer/
├── Rasterizer2025.py      # Aplicación principal de renderizado
├── gl.py                  # Motor de renderizado principal
├── Lab1/
│   ├── main.py           # Demo interactivo de polígonos
│   └── ren.py            # Renderizador mejorado con más características
├── pygame_env/           # Entorno virtual
└── README.md            # Este archivo
```

## 🔧 Componentes Principales

### Clase Renderer (`gl.py`)

**Métodos Principales:**
- `glPoint(x, y)` - Dibujar píxeles individuales
- `glLine(x0, y0, x1, y1)` - Dibujar líneas usando algoritmo de Bresenham
- `glDrawPolygon(points)` - Dibujar contornos de polígonos
- `glFillPolygon(points)` - Rellenar polígonos usando algoritmo de líneas de barrido
- `glColor(r, g, b)` - Establecer color de dibujo actual
- `glClear()` - Limpiar la pantalla

**Sistema de Coordenadas:**
- Origen (0,0) en la esquina inferior izquierda
- Eje Y positivo apunta hacia arriba
- Dimensiones de pantalla: 960x540 píxeles

### Polígonos de Ejemplo

El proyecto incluye varios polígonos predefinidos para pruebas:

```python
# Polígono complejo de 10 vértices
polygon = [
    (165, 380), (185, 360), (180, 330), (207, 345),
    (233, 330), (230, 360), (250, 380), (220, 385),
    (205, 410), (193, 383)
]

# Cuadrilátero simple
polygon_2 = [(321, 335), (288, 286), (339, 251), (374, 302)]

# Triángulo
polygon_3 = [(377, 249), (411, 197), (436, 249)]

# Forma compleja de 18 vértices
polygon_4 = [
    (413, 177), (448, 159), (502, 88), (553, 53), (535, 36), 
    (676, 37), (660, 52), (750, 145), (761, 179), (672, 192), 
    (659, 214), (615, 214), (632, 230), (580, 230), (597, 215), 
    (552, 214), (517, 144), (466, 180)
]
```

## 🎨 Sistema de Colores

Los colores se especifican usando valores RGB normalizados (0.0 a 1.0):

```python
render.glColor(1, 0, 0)     # Rojo
render.glColor(0, 1, 0)     # Verde
render.glColor(0, 0, 1)     # Azul
render.glColor(1, 1, 1)     # Blanco
render.glColor(0.5, 0.5, 0.5) # Gris
```

## 🔬 Implementación Técnica

### Algoritmo de Relleno de Polígonos por Líneas de Barrido

1. **Construcción de Tabla de Aristas**: Construir tabla de aristas del polígono con coordenadas Y y pendientes
2. **Recorrido por Líneas de Barrido**: Para cada línea horizontal (coordenada Y):
   - Encontrar intersecciones con las aristas del polígono
   - Ordenar puntos de intersección
   - Rellenar entre pares de intersecciones

### Transformación de Coordenadas Matemáticas

```python
# Convertir de coordenadas matemáticas a coordenadas de pantalla
pantalla_y = altura - 1 - matematica_y
```

### Gestión de Framebuffer

Sistema de doble buffer con pantalla y framebuffer interno para datos de píxeles.

## 🎯 Casos de Uso

- **Educación en Gráficos por Computadora**: Aprender algoritmos de rasterización
- **Desarrollo de Juegos**: Entender conceptos de renderizado de bajo nivel
- **Visualización de Algoritmos**: Ver algoritmos de líneas de barrido y trazado de líneas en acción
- **Motores Gráficos Personalizados**: Base para construir renderizadores personalizados

## 🐛 Solución de Problemas

### Problemas Comunes

1. **"ModuleNotFoundError: No module named 'pygame'"**
   ```bash
   source pygame_env/bin/activate
   pip install pygame
   ```

2. **"No se ven polígonos"**
   - Verificar que los polígonos estén dentro de los límites de pantalla (0-960, 0-540)
   - Verificar sistema de coordenadas (Y aumenta hacia arriba)

3. **"Entorno virtual no funciona"**
   ```bash
   # Recrear entorno
   rm -rf pygame_env
   python3 -m venv pygame_env
   source pygame_env/bin/activate
   pip install pygame
   ```

## 📚 Objetivos de Aprendizaje

Este proyecto demuestra:
- **Algoritmos de Rasterización**: Conversión de formas geométricas a píxeles
- **Transformaciones de Sistemas de Coordenadas**: Coordenadas matemáticas vs. gráficos por computadora
- **Algoritmos de Líneas de Barrido**: Técnicas eficientes de relleno de polígonos
- **Algoritmo de Bresenham**: Optimización de trazado de líneas
- **Pipeline de Renderizado por Software**: Entender funcionalidad de GPU a nivel de software



## 📄 Licencia

Este proyecto está creado con fines educativos. Siéntete libre de usar y modificar para aprender conceptos de gráficos por computadora.

