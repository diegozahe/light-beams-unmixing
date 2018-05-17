import numpy as np
import cv2
import time
import math
import metodos as met
import argparse #necesario para introducir valores por parametro 

# INICIO LEYENDA
# Las variables de control empezaran por VC_
# Las variables que pueden ser modificadas por el usuario empezaran por VU_
# Las variables que se usen como contadores empezaran por C_
# Las variables que solo se modifican 1 vez durante todo el programa empezará por E_ (estatico)
# FIN LEYENDA

#INSTRUCCIONES PARA MODIFICAR EL COMANDO QUE LANZA LA APLICACION
#_____ prog -> para cambiar el nombre del comando que lanza este programa.
#_____description -> info sobre lo que hace el programa

parser = argparse.ArgumentParser(prog="calibration",description="Process for identifying heliostats.")

parser.add_argument("--numHeliostats",default="4",type=int,help="set the number of heliostats to calibrate at once")
parser.add_argument("--pyrLevels",default="0",type=int, #nargs="?",
                     help="set how many times the Pyramid method will be applied to source")
args = parser.parse_args()

# Variables obtenidas por el usuario
cantHel = args.numHeliostats
cantPyrD = args.pyrLevels

# Cargamos el vídeo
#camara = cv2.VideoCapture("Videos/video_paint3.mp4") (si usas este video cambia los parametros de numHeliostats a 3)
camara = cv2.VideoCapture("Videos/varios_heliostatos.mp4")
fondo = None # Inicializamos el primer frame a vacío. Nos servirá para obtener el fondo

# Listas
listaHel = []
listaTamañoHel = []

# Contadores
contHel = 0
iteraciones = 0
contAnadir = 0
cont2 = 0

# Variables de control
comenzarRegistroMovimiento = False # Comenzamos de nuevo a detectar mas manchas cuando hay mas de 1 proyeccion
comenzarEstablecerFondo = False
add1Mancha = False
add2Mancha = False
noEntrar1Mancha = False
comprPAP = False

#**************************
#** EMPEZAMOS EL PROGRAMA**
#**************************

#ORDEN DE SALIDA:
#3, 2, 4, 1

while True:
	# Obtenemos el frame
	(grabbed, frame) = camara.read()
 	
	# Si hemos llegado al final del vídeo salimos
	if not grabbed:
		break
 	
 	# Bucle para reducir la imagen tantas veces como queramos
	for x in range(0,cantPyrD):
 		frame = cv2.pyrDown(frame)

	# Convertimos a escala de grises
	gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

 	# Aplicamos suavizado para eliminar ruido
	gris = cv2.GaussianBlur(gris, (21, 21), 0)

	# Si todavía no hemos obtenido el fondo, lo obtenemos. Será el primer frame que obtengamos
	if fondo is None:
		fondo = gris
		total = fondo.shape[0]*fondo.shape[1] #calculamos la altura y anchura
		umbralFondo = met.umbralizar(gris)
		continue 	

	# Calculo de la diferencia entre el fondo y el frame actual
	resta = cv2.absdiff(fondo, gris)

	# Umbralizamos la imagen defencia
	umbral = met.umbralizar(resta)
		
	# Copiamos el umbral para detectar los contornos
	contornosimg = umbral.copy()

	# Buscamos contorno en la imagen. La variable contornosimg cambia! im = contornosimg
	im, contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
	
	edges = cv2.Canny(umbral,255,255)

	# Comprobamos que la lista este vacia. Si lo esta cambiamos la variable comproPAP a false para que cuando se vuelva a salir
	# un trozo de mancha compruebe cual es y no tenga que hacer la comprobacion muchas veces
	if met.listaVacia(contornos) == True and comprPAP == True:
		comprPAP = False

	# Recorremos todos los contornos encontrados
	for c in contornos:
		# Eliminamos los contornos más pequeño
		contorno = cv2.contourArea(c)
		
		# Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
		(x1, y1, w, h) = cv2.boundingRect(c) # w: es wigth y h: es heigh
		
		# Dibujamos el rectángulo del bounds
		cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
		
		# Si el contorno es tan pequeño suponemos es algo que no deberia estar...
		if contorno <= 300:
			continue
		# Si cumple los requisitos suponemos que es movimiento. 
		# Habria que poner una condicion de si se detecta el movimiento fuera de un cuadrado...
		elif contorno > 300 and comenzarRegistroMovimiento == True:
			# Hacemos una especie de contador para que solo lo haga 1 vez
			if comprPAP == False:
				# Calculamos el punto (x2,y2):
				y2 = y1 + h
				x2 = x1 + w
				manchaNueva = edges[y1:y2, x1:x2]
				pos = 0
				pos, funciona = met.lorenzo(listaHel, manchaNueva)
				if funciona!=False:
					print("Hay movimiento, creemos que es el heliostato ",(pos+1))
				#time.sleep(10)
				if cont2==30 or funciona == False:
					comprPAP = True
					cont2=0
					funciona = True
				else:
					cont2+=1

		# Una vez hemos añadido las manchas establecemos el fondo. Damos 150 frame 
		elif comenzarEstablecerFondo == True:
			if cantHel == contHel:
				if iteraciones==150:
					fondo = gris # El nuevo fondo sera gris
					umbralFondo = met.umbralizar(gris)
					comenzarRegistroMovimiento = True
				while(iteraciones<150):
					iteraciones+=1
					(grabbed, frame) = camara.read()

		# Esta condicion se usa para ir añadiendo manchas.
		elif comenzarRegistroMovimiento == False:
			# La logica es la siguiente: en el momento en que haya un contorno y aparezca otro, 
			# añado el primer contorno a la lista.
			if cantHel == contHel:
				print("Comenzamos a comparar") # Mensaje para controlar por que parte del programa va.
				comenzarEstablecerFondo = True
				met.visualizarLista(listaHel)

			elif len(contornos)>1:
				if contAnadir == 20:
					helCompr = []
					for t in contornos:
						(x1, y1, w, h) = cv2.boundingRect(t)
						#calculamos el punto (x2,y2):
						y2 = y1 + h
						x2 = x1 + w
						manchaNu = edges[y1:y2, x1:x2]
						helCompr.append(manchaNu)
						#print(contAnadir)
						contAnadir = 0

				else:
					contAnadir+=1
				# Condicion para que no entre mas en la condicion de abajo, sino en la siguiente
				if noEntrar1Mancha == True:
					add1Mancha = True
				else:
					add2Mancha = True

			# Una vez que ya se han juntado las 2 primeras manchas en 1, las añadimos a listaHel
			elif len(contornos)==1 and add2Mancha == True:
				listaHel.append(helCompr[1]) # En la posicion 1 esta la mancha que ya estaba antes
				listaHel.append(helCompr[0]) # En la posicion 0 esta la mancha nueva
				add2Mancha = False
				noEntrar1Mancha = True
				contHel += 2
				#print("añadimos!!!")

			# Este condicional solo añade una mancha
			elif len(contornos)==1 and add1Mancha == True:
				listaHel.append(helCompr[0])
				add1Mancha = False
				contHel += 1
				#print("añadimos!!!")
		
	# Mostramos las imágenes de la cámara, el umbral y la resta
	cv2.imshow("Camara", frame)
	cv2.imshow("Edges", edges)
	cv2.imshow("Umbral", umbral)
	cv2.imshow("Resta", resta)
	cv2.imshow("Fondo", fondo)
	
	# Capturamos una tecla para salir
	key = cv2.waitKey(1) & 0xFF
	
	# Tiempo de espera para que se vea bien
	time.sleep(0.015)

	# Si ha pulsado la letra s, salimos
	if key == ord("s"):
		break

# Liberamos la cámara y cerramos todas las ventanas
camara.release()
cv2.destroyAllWindows()

