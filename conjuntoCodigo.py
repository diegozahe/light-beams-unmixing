import numpy as np
import cv2
import time
import math
import metodos as met





#*********************
# DECLARAMOS VARIABLES
#*********************

# Cargamos el vídeo
camara = cv2.VideoCapture("varios_heliostatos.mp4")
fondo = None # Inicializamos el primer frame a vacío. Nos servirá para obtener el fondo

# Listas
listaHel = []
listaTamañoHel = []
listaHel1 = [[],[],[],[]]
# Contadores
contHel = 0
iteraciones = 0

# Variables de control
comenzarRegistroMovimiento = False # Comenzamos de nuevo a detectar mas manchas cuando hay mas de 1 proyeccion
comenzarEstablecerFondo = False
add1Mancha = False
add2Mancha = False
noEntrar1Mancha = False
comprPAP = False


#ToDo
cantHel = 4
cantPyrD = 0

#**************************
#** EMPEZAMOS EL PROGRAMA**
#**************************

#ORDEN DE SALIDA:
#3, 2, 4, 1

while True:
	hora1 = time.time()
	# Obtenemos el frame
	#print(type(weight))
	(grabbed, frame) = camara.read()
 	
	# Si hemos llegado al final del vídeo salimos
	if not grabbed:
		break
 	
 	#bucle para reducir la imagen tantas veces como queramos
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
		total = total/8
		umbralFondo = met.umbralizar(gris)
		continue 	

	# Aplicamos un umbral
	umbral = met.umbralizar(gris)

	# Dilatamos el umbral para tapar agujeros
	umbral = cv2.dilate(umbral, None, iterations = 2)

	if comenzarRegistroMovimiento == True:
		# Calculo de la diferencia entre el fondo y el frame actual
		resta = cv2.absdiff(fondo, gris)
		umbral = met.umbralizar(resta)
	else:
		# Calculo la diferencia entre el fondo y el frame actual BINARIZADO
		resta = cv2.absdiff(umbralFondo, umbral)
	
	# Copiamos el umbral para detectar los contornos
	contornosimg = umbral.copy()

	# Buscamos contorno en la imagen. La variable contornosimg cambia!
	im, contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
	
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
		if contorno <= 500:
			continue

		# Si cumple los requisitos suponemos que es movimiento. Habria que poner una condicion de si se detecta el movimiento fuera de un cuadrado...
		elif contorno > 500 and contorno<total and comenzarRegistroMovimiento == True:
			# Hacemos una especie de contador para que solo lo haga 1 vez
			if comprPAP == False:
				# Calculamos el punto (x2,y2):
				y2 = y1 + h
				x2 = x1 + w
				manchaNueva = gris[y1:y2, x1:x2]
				#met.visualizarLista(listaHel, manchaNueva)
				pos = 0
				#pos = met.comprobarPAP2(listaHel, manchaNueva)
				pos = met.lorenzo(listaHel, manchaNueva)
				print("Hay movimiento, creemos que es el heliostato ",(pos+1))
				comprPAP = True

		# Una vez hemos añadido las manchas establecemos el fondo
		elif comenzarEstablecerFondo == True:
			# TIENES QUE CAMBIAR A PARTIR DE AQUI!!***********************************************************************************************************
			if cantHel == contHel:
				if iteraciones==150:
					fondo = gris # El nuevo fondo será
					umbralFondo = met.umbralizar(gris)
					comenzarRegistroMovimiento = True
				while(iteraciones<150):
					iteraciones+=1
					(grabbed, frame) = camara.read()
			# TIENES QUE CAMBIAR HASTA AQUI*******************************************************************************************************************

		# Esta condicion se usa para ir añadiendo manchas.
		elif comenzarRegistroMovimiento == False:
			# La logica es la siguiente: en el momento en que haya un contorno y aparezca otro, añado el primer contorno a la lista.
			if cantHel == contHel:
				print("Comenzamos a comparar")
				comenzarEstablecerFondo = True
			elif len(contornos)>1:
				helCompr = []
				for t in contornos:
					(x1, y1, w, h) = cv2.boundingRect(t)
					#calculamos el punto (x2,y2):
					y2 = y1 + h
					x2 = x1 + w
					manchaNu = gris[y1:y2, x1:x2]
					helCompr.append(manchaNu)
				# Condicion para que no entre mas en la condicion de abajo, sino en la siguiente
				if noEntrar1Mancha == True:
					add1Mancha = True
				else:
					add2Mancha = True
			elif len(contornos)==1 and add2Mancha == True:
				listaHel.append(helCompr[1]) # En la posicion 1 esta la mancha que ya estaba antes
				listaHel.append(helCompr[0]) # En la posicion 0 esta la mancha nueva
				add2Mancha = False
				noEntrar1Mancha = True
				contHel += 2
			elif len(contornos)==1 and add1Mancha == True:
				listaHel.append(helCompr[0])
				add1Mancha = False
				contHel += 1
		
	# Mostramos las imágenes de la cámara, el umbral y la resta
	cv2.imshow("Camara", frame)
	# cv2.imshow("Umbral", umbral)
	# cv2.imshow("Resta", resta)

	# Capturamos una tecla para salir
	key = cv2.waitKey(1) & 0xFF
	
	# Tiempo de espera para que se vea bien
	time.sleep(0.015)

	# Si ha pulsado la letra s, salimos
	if key == ord("s"):
		break

	hora2 = time.time()
	hora3 = hora2-hora1
	#print(1/hora3)
# Liberamos la cámara y cerramos todas las ventanas
camara.release()
cv2.destroyAllWindows()
