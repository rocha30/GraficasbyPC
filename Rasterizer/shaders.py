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
