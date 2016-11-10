import numpy as np
import cv2
import time
import math
import scipy.stats as st
from PIL import Image
from PIL import ImageChops
import matplotlib.pyplot as plt
#from matplotlib import pyplot as plt

class heliostato:
	
	#lo declaro arriba para poder usarlo abajo xD
	#le paso como parametro la imagen grande, luego la imagen pequeña que tiene que buscar
	#y por ultimo el array donde estan guardadas las proyecciones
	def contener(array, mancha):
		#HAY QUE CAMBIARLOOOOO!!!!*********************************************************************
		#Esta es 
		mediaEntropia = []
		d = Image.fromarray(mancha)
		media = 0
		for c in array:
			divisor = 0
			b = Image.fromarray(c)
			residuoImage = ImageChops.difference(b, d)
			residuoNP = np.array(residuoImage)
			entropia = st.entropy(residuoNP)
			for c in entropia:
				media=media+c
				divisor+=1
			mediaEntropia.append(media/divisor)
		masPequenio = 1000
		pos = -1
		if not mediaEntropia:
			pass
		else:
			for c in mediaEntropia:
				if masPequenio > c:
					masPequenio = c
				pos+=1
		print("Se esta moviendo el heliostato", (pos+1))
		time.sleep(10)
		return pos
		#HASTA AQUI LLEGA EL METODO *****************************************************************
	
	#no deberia tardar mucho en hacer la comprobacion ya que no son imagenes completas sino recortes que contienen la mancha
	def comprobarMancha(array, mancha):
		#comprobamos la mancha que hemos encontrado con cada heliostado dentro del array
		#si ya esta dentro devolvemos True
		#tranformo el array de tipo numpy a un array de tipo Image:
		mediaEntropia = []
		d = Image.fromarray(mancha)
		media = 0
		for c in array:
			divisor = 0
			b = Image.fromarray(c)
			residuoImage = ImageChops.difference(b, d)
			residuoNP = np.array(residuoImage)
			entropia = st.entropy(residuoNP)
			for c in entropia:
				media=media+c
				divisor+=1
			mediaEntropia.append(media/divisor)
		masPequenio = 1000
		if not mediaEntropia:
			pass
		else:
			for c in mediaEntropia:
				if masPequenio > c:
					masPequenio = c
		
		if masPequenio<5:
			#la entropia normalmente es de 3 si es de 5 significa que es una mancha diferente
			return True
		print(masPequenio)
		return False



	#EMPEZAMOS EL PROGRAMA GORDO
	# Cargamos el vídeo
	camara = cv2.VideoCapture("heliostato(2).MOV")

	#*****************
	#INICIALIZAMOS!!!!
	#*****************
	# Inicializamos el primer frame a vacío.
	# Nos servirá para obtener el fondo
	fondo = None
	# Usamos compr[] para determinar si el objeto se ha detenido
	# y establecer un nuevo fondo. La 1ª posicion es la imagen que sera el fondo
	#el resto son comprobaciones
	compr = [None, None, None,None]
	# la variable i la usamos para dar valor a las variables comprobacionX
	i = 0
	j = 0
	#Guarda por el frame por el que va
	numFrame = 0
	#array para guardar la distancia
	distt = [0,0,0,0,0]
	arrayXYWH = [0,0,0,0]
	dist = 100000 #variables para calcular la distancia. luego la introducimos en distt
	#array que guarda cada uno de los heliostatos
	hel = []




	# Recorremos todos los frames
	while True:
		# Obtenemos el frame
		#print(type(weight))
		(grabbed, frame) = camara.read()
	 	
		# Si hemos llegado al final del vídeo salimos
		if not grabbed:
			break
	 	
		# Convertimos a escala de grises
		gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	 	
		# Aplicamos suavizado para eliminar ruido
		gris = cv2.GaussianBlur(gris, (21, 21), 0)
	 	
		# Si todavía no hemos obtenido el fondo, lo obtenemos
		# Será el primer frame que obtengamos
		if fondo is None:
			fondo = gris
			continue

		# Calculo de la diferencia entre el fondo y el frame actual
		resta = cv2.absdiff(fondo, gris)
	 	
		# Aplicamos un umbral
		umbral = cv2.threshold(resta, 50, 255, cv2.THRESH_BINARY)[1]
	 
		# Dilatamos el umbral para tapar agujeros
		umbral = cv2.dilate(umbral, None, iterations=2)
	 
		# Copiamos el umbral para detectar los contornos
		contornosimg = umbral.copy()
	 
		# Buscamos contorno en la imagen
		im, contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	 	#ESTO ESTA PERFECTO ----------------------------------------------------------------------------------------------------------------
	 	#comenzmos de nuevo a detectar el fondo cuando hay mas de 1 proyeccion
		comenzarDeNuevo = True

		comenzarRegistroMovimiento = False
		# Recorremos todos los contornos encontrados
		for c in contornos:
			# Eliminamos los contornos más pequeño
			contorno = cv2.contourArea(c)
			# Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno7
			#w es wigth y h es heigh
			(x1, y1, w, h) = cv2.boundingRect(c)
			#calculamos la distancia entre los puntos (x1,y1) al punto (x2,y2) 
			#numero = (w - x)**2 + (h-y)**2
			numero = w**2 + h**2
			dist = math.sqrt(numero)
			#calculamos el punto (x2,y2):
			y2 = y1 + h
			x2 = x1 + w
			
			manchaNueva = cv2.pyrDown(cv2.pyrDown(gris[y1:y2, x1:x2]))
			#si el contorno es tan pequeño suponemos es algo que no deberia estar...
			if contorno < 3000:
				continue
			#Si cumple los requisitos suponemos que es movimiento. Habria que poner una condicion de si se detecta el movimiento fuera de un cuadrado...
			elif contorno > 3000 and contorno<60000 and comenzarRegistroMovimiento:
				print("AHORA LO CAPTURAMOS")
				#suponemos es movimiento y lo comparamos con el resto de manchas
				pos = comprobar(hel, manchaNueva)
				print("Hay movimiento, creemos que es el heliostado ",(pos+1)) 
				time.sleep(10)

			else:
				# Dibujamos el rectángulo del bounds
				cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
				#AQUI EMPIEZA COMO ESTABLECER UN NUEVO FONDO

				if len(contornos)>1:
					comenzarDeNuevo = True
				if len(contornos)==1 and comenzarDeNuevo==True and distt[0]==distt[1] and distt[0]==distt[2] and arrayXYWH[0]==x1 and arrayXYWH[1]==y1 and arrayXYWH[2]==w and arrayXYWH[3]==h:
					print("Se añadio un fondo!")
					fondo = gris
					comenzarDeNuevo = False
					comenzarRegistroMovimiento = True
				#añadimos el valor actual de x e y
				arrayXYWH[0]=x1
				arrayXYWH[1]=y1
				arrayXYWH[2]=w
				arrayXYWH[3]=h

				#AQUI EMPIEZA COMO INSERTAR LA MANCHA EN LA LISTA DE MANCHAS:

				#print(w, h)
				verdadero = False
				#comprobamos que la distancia sea la misma en varias ocasiones diferentes
				#print("Numero fram = ", numFrame," Distt[k] =", distt[k],"dist = ", dist)
				#print("Ha entrado en el contador")
				#if distt[k]-dist <= 0 and distt[k]-dist >= -0.2:
				if j == 0:
					distt[0]=dist
					j+=1
					#print(j)
				elif j == 1:
					distt[1]=dist
					j+=1
					#print(j)
				elif j==2:
					distt[2]=dist
					j+=1
					#print(j)
				elif j==3:
					#print(distt[0],distt[1], distt[2])
					pri = distt[0]
					seg = distt[1]
					ter = distt[2]
					j=0
					#print(" Los valores son: ",pri, seg, ter)
					if pri==seg and seg==ter and ter==pri:
						#print("cumplio la condicion!!")
						if comprobarMancha(hel, manchaNueva):
							#NO HACEMOS NADA
							#Si es True significa que si esta dentro del array y no queremso añadirlo de nuevo
							continue
						else:
							#esto lo hacemos para evitar meter el contorno de la proyeccion conjunta por varios heliostatos
							# que es nuestro "fondo" aun no establecido
							#Introducimos un elemento mas que es "cualquier cosa" para poder insertar
							#en la siguiente posicion la proxima vez.
							#Le aplicamos dos capas a la piramide
							hel.append(manchaNueva) 
							continue
				else:
					j+=1




		#Hasta aqui funciona bien -------------------------------------------------------------------------------------------------------
				#Ahora detectamos
		#FALTA HACER EL CODIGO PARA CUANDO DETECTA MOVIMIENTO COMPARARLA CON TOOOOOODAS LAS MANCHAS****************************************
		#ESCRIBIR CODIGO


		#**********************************************************************************************************************************

		# Mostramos las imágenes de la cámara, el umbral y la resta
		cv2.imshow("Camara", cv2.pyrDown(cv2.pyrDown(frame)))
		cv2.imshow("Umbral", cv2.pyrDown(cv2.pyrDown(umbral)))
		cv2.imshow("Resta", cv2.pyrDown(cv2.pyrDown(resta)))
		cv2.imshow("Gris", cv2.pyrDown(cv2.pyrDown(gris)))
		cv2.imshow("Fondo", cv2.pyrDown(cv2.pyrDown(fondo)))
		#cv2.imshow("Contorno", contornosimg)

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

#Con esto declaramos una clase y se ejecuta
ejecutar = heliostato
