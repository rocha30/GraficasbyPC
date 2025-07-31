import numpy as np
from math import pi, sin, cos, isclose, tan



def TranslationMatrix(x, y, z):
	
	return np.matrix([[1, 0, 0, x],
					  [0, 1, 0, y],
					  [0, 0, 1, z],
					  [0, 0, 0, 1]])



def ScaleMatrix(x, y, z):
	
	return np.matrix([[x, 0, 0, 0],
					  [0, y, 0, 0],
					  [0, 0, z, 0],
					  [0, 0, 0, 1]])



def RotationMatrix(pitch, yaw, roll):
	
	# Convertir a radianes
	pitch *= pi/180
	yaw *= pi/180
	roll *= pi/180
	
	# Creamos la matriz de rotaciÛn para cada eje.
	pitchMat = np.matrix([[1,0,0,0],
						  [0,cos(pitch),-sin(pitch),0],
						  [0,sin(pitch),cos(pitch),0],
						  [0,0,0,1]])
	
	yawMat = np.matrix([[cos(yaw),0,sin(yaw),0],
						[0,1,0,0],
						[-sin(yaw),0,cos(yaw),0],
						[0,0,0,1]])
	
	rollMat = np.matrix([[cos(roll),-sin(roll),0,0],
						 [sin(roll),cos(roll),0,0],
						 [0,0,1,0],
						 [0,0,0,1]])
	
	return pitchMat * yawMat * rollMat

def ViewMatrix (eye, at, up): 
    eye = np.array(eye)
    at = np.array(at)
    up = np.array(up)
    
    forward = at - eye # vector hacia donde mira 
    forward = forward / np.linalg.norm(forward) # normalizar

    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    up = np.cross(right, forward) # recalcular el vector up
    forward = -forward # invertir el vector forward
    
    rotation = np.matrix([
		[right[0], right[1], right[2], 0],
		[up[0], up[1], up[2], 0],
		[forward[0], forward[1], forward[2], 0],
		[0, 0, 0, 1]
	])
    
    translation = TranslationMatrix(-eye[0], -eye[1], -eye[2])
    
    return rotation * translation

def ProjectionMatrix(fov, aspect, near, far):
	for_rad = fov * pi / 180
	f = 1 / tan(for_rad / 2)
	return np.matrix([
		[f / aspect, 0, 0, 0],
		[0, f, 0, 0],
		[0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
		[0, 0, -1, 0]
	])
 
def LookAtMatrix(eye, target, up): 
    return ViewMatrix(eye, target, up)

def ViewportMatrix(x, y, width, height):
    """Create viewport transformation matrix"""
    return np.matrix([
        [width/2, 0, 0, x + width/2],
        [0, height/2, 0, y + height/2],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])