#!/usr/bin/env python3
"""
Script de prueba para cargar modelo y textura sin interfaz gráfica
"""

# Simular PIL para probar sin instalarlo
class MockImage:
    def __init__(self, mode, size):
        self.mode = mode
        self.width, self.height = size
        self._pixels = {}
    
    def load(self):
        return self
    
    def __setitem__(self, key, value):
        self._pixels[key] = value
    
    def getpixel(self, coord):
        return self._pixels.get(coord, (128, 128, 128))

class MockPIL:
    class Image:
        @staticmethod
        def open(filename):
            raise FileNotFoundError(f"Archivo no encontrado: {filename}")
        
        @staticmethod
        def new(mode, size):
            return MockImage(mode, size)

# Reemplazar PIL temporalmente
import sys
sys.modules['PIL'] = MockPIL()
sys.modules['PIL.Image'] = MockPIL.Image

# Importar nuestro modelo
try:
    from model import Model
    
    print("=== PRUEBA DE CARGA DE MODELO ===")
    
    # Crear modelo
    model = Model()
    
    # Cargar archivo OBJ
    model.load_obj("centauro.obj")
    
    # Intentar cargar textura (fallará y usará procedural)
    model.load_texture("test_texture.png")
    
    # Escalar modelo
    model.scale_to_fit(2.0)
    
    print(f"\n✅ Modelo cargado exitosamente!")
    print(f"   - Vértices: {len(model.vertices)//3}")
    print(f"   - Caras: {len(model.faces)}")
    print(f"   - UVs: {len(model.texture_coords)}")
    print(f"   - Textura: {'Sí' if model.texture else 'No'}")
    
    # Probar obtener color de textura
    if model.texture:
        color = model.get_texture_color(0.5, 0.5)
        print(f"   - Color de prueba (UV 0.5,0.5): {color}")
    
    print(f"\n📐 Transformaciones:")
    print(f"   - Escala: {model.scale}")
    print(f"   - Traslación: {model.translation}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
