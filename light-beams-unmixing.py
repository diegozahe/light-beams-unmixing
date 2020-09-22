import numpy as np
import cv2
import time
import metodos as met
import argparse #necesario para introducir valores por parametro

#light-beams-unmixing.py --video Videos/varios_heliostatos.mp4 --numHeliostats 4 --pyrLevels 0 --iterations 150 --contAniadirMax 50 --entPro 0
# Parametros pasados por el usuario a la hora de ejecutar el codigo
parser = argparse.ArgumentParser(description="Proceso para identificar la proyección saliente.")
parser.add_argument("--video",default="Videos/varios_heliostatos.mp4",help="Directorio del video a analizar")
parser.add_argument("--numHeliostats",default="4",type=int,help="Número de proyecciones para analizar")
parser.add_argument("--pyrLevels",default="0",type=int, #nargs="?",
                     help="Numero de veces que aplicamos el metodo de la piramide.")
parser.add_argument("--iterations",default="150",type=int,help="Establecemos el numero de fotogramas que necesitamos esperar.")
parser.add_argument("--contAniadirMax",default="150",type=int, help="Fotogramas que pasan para capturar el nuevo fondo.")
parser.add_argument("--entPro",default="150",type=int, help="Orden de entrada de las proyecciones.")
args = parser.parse_args() # Devuelve la información de los parámetros definidos previamente

# Una vez iniciado el programa y pasado por parametro las variables obtenemos la hora actual de ejecucion
hora1 = time.time()

# Variables obtenidas por el usuario
video = args.video
cantHel = args.numHeliostats
cantPyrD = args.pyrLevels
contIteracion = args.iterations
contAniadirMax = args.contAniadirMax
entPro = args.entPro

# Inicializamos el primer fotograma a vacío. Nos servirá para obtener el fondo
fondo = None 

# Listas
listaHel = [] 
helCompr = []

# Contadores
iteraciones = 0
contAniadir = 0
cont2 = 0
iteracion = 0

# Variables de control para ir por un condicional u otro dependiendo del 
# progreso del video.
comenzarRegistroMovimiento = False # Comenzamos de nuevo a detectar mas manchas cuando hay mas de 1 proyeccion
comenzarEstablecerFondo = False
add1Mancha = False
add2Mancha = False
noEntrar1Mancha = False
comprMancha = False

#**************************
#** EMPEZAMOS EL PROGRAMA**
#**************************
print("Empezamos la ejecucion del código")

camara = cv2.VideoCapture(video)

#camara = cv2.VideoCapture("Videos/hacesLuzLinterna3.mov") 	# orden de salida: 2, 1 y 3
#entPro = 1 	# Orden de entrada de las proyecciones. Significa que entra de derecha a izquierda.
#cantHel = 3 # Cantidad heliostatos
#cantPyrD = 2 	# Numero de pyrDown
#contIteracion = 15 	# Frames que pasan para capturar una nueva referencia del heliostato entrante
#contAniadirMax = 10 # Frames que pasan para capturar el nuevo fondo


camara = cv2.VideoCapture("Videos/varios_heliostatos.mp4") # orden de salida: 3, 2, 4, 1
entPro = 0 	# Entrada de las proyecciones. Significa que entra de izquierda a derecha.
cantHel = 4 # Cantidad heliostatos
cantPyrD = 0 	# Numero de pyrDown
contIteracion = 150 	# Frames que pasan para capturar una nueva referencia del heliostato entrante
contAniadirMax = 50 # Frames que pasan para capturar el nuevo fondo

while True:
	# Obtenemos el frames
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
		fondo = gris # Establecemos el fondo gris. Solo se hará una vez.
		total = (fondo.shape[0]*fondo.shape[1])/8 # Calculamos la altura y anchura
		umbralFondo = met.umbralizar(gris)
		continue 	

	# Calculo de la diferencia entre el fondo y el frame actual
	resta = cv2.absdiff(fondo, gris)
	umbralResta = met.umbralizar(resta)
	umbralResta = cv2.dilate(umbralResta, None, iterations = 1) #cantDilate
	umbralResta = cv2.erode(umbralResta, None, iterations = 1) #cantErode
	
	# Copiamos el umbral para detectar los contornos
	contornosimg = umbralResta.copy()

	# Buscamos contorno en la imagen. La variable contornosimg cambia! im = contornosimg
	contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

	edges = cv2.Canny(umbralResta,255,255)

	# Variables que usamos para distinguir por colores las proyecciones
	contContornos = 0
	color = ""

	# Comprobamos que la lista este vacia. Si lo está cambiamos la variable comproPAP a false para que cuando se vuelva a salir
	# un trozo de mancha compruebe cual es y no tenga que hacer la comprobacion muchas veces
	#if met.listaVacia(contornos) == True and comprMancha == True:
	#	print("entra")
		# Establecemos un nuevo fondos
	#	fondo = gris # El nuevo fondo sera gris
	#	umbralFondo = met.umbralizar(gris)
	#	comprMancha = False
	#	print("ENTRAAAA")
	#if len(contornos) > 1:
	#	contornos = met.sortContours(contornos)

	
	# Recorremos todos los contornos encontrados
	for c in contornos:
		contContornos += 1
		# Detectamos los contornos
		contorno = cv2.contourArea(c)

		# Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
		(x1, y1, w, h) = cv2.boundingRect(c) # w: es wigth y h: es heigh
			
		# Dibujamos el rectángulo del bounds
		if contContornos == 1:
			color = "VERDE"
			cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)
		if contContornos == 2:
			color = "AZUL"
			cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (255, 0, 0), 2)
		if contContornos >= 3:
			color = "ROJO"
			cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 0, 255), 2)
		
		# Si el contorno es tan pequeño suponemos es algo que no deberia estar...
		if contorno <= 100: #50 video linternas
			continue

		# Esta condicion se usa para ir añadiendo manchas.
		elif comenzarRegistroMovimiento == False:
			# La logica es la siguiente: en el momento en que haya un contorno y aparezca otro, añado el primer contorno a la lista.
			if cantHel == len(listaHel):
				print("Comenzamos a comparar")
				comenzarEstablecerFondo = True
				comenzarRegistroMovimiento = True
			elif len(contornos)>1:
				if contAniadir == contAniadirMax:
					helCompr = []
					for t in contornos:
						(x1, y1, w, h) = cv2.boundingRect(t)
						# Calculamos el punto (x2,y2):
						y2 = y1 + h
						x2 = x1 + w
						manchaNueva = umbralResta[y1:y2, x1:x2]
						helCompr.append(manchaNueva)
					contAniadir = 0	
				else:
					contAniadir+=1
					
				# Condicion para que no entre mas en la condicion de abajo, sino en la siguiente
				if noEntrar1Mancha == True:
					add1Mancha = True
				else:
					add2Mancha = True

			# Una vez que ya se han juntado las 2 primeras manchas en 1, las añadimos a listaHel
			elif len(contornos) == 1 and add2Mancha == True:
				print("Añadidas las dos primeras")
				if entPro == 0: #tenemos que tener en cuenta el oren de entrada de las proyecciones
					listaHel.append(helCompr[1]) # En la posicion 1 esta la mancha que ya estaba antes
					listaHel.append(helCompr[0]) # En la posicion 0 esta la mancha nueva
				else:
					listaHel.append(helCompr[0]) # En la posicion 0 esta la mancha nueva
					listaHel.append(helCompr[1]) # En la posicion 1 esta la mancha que ya estaba antes
				add2Mancha = False
				noEntrar1Mancha = True
				
			# Este condicional solo añade una mancha
			elif len(contornos)==1 and add1Mancha == True:
				print("Añadida la siguiente")
				if entPro == 0: #tenemos que tener en cuenta el oren de entrada de las proyecciones
					listaHel.append(helCompr[0]) # En la posicion 0 esta la mancha nueva
				else:
					listaHel.append(helCompr[1]) # En la posicion 1 esta la mancha que ya estaba antes
				add1Mancha = False

		# Una vez hemos añadido las manchas establecemos el fondo. Damos 150 frame, en el video de las linternas solo 10.
		elif comenzarEstablecerFondo == True:
			if cantHel == len(listaHel):
				#met.visualizarLista(listaHel)
				if iteraciones==contIteracion:
					fondo = gris # El nuevo fondo sera gris
					umbralFondo = met.umbralizar(gris)
					comenzarRegistroMovimiento = True
					comenzarEstablecerFondo = False
				while(iteraciones < contIteracion):
					iteraciones+=1
					(grabbed, frame) = camara.read()
			
		# Si cumple los requisitos suponemos que es movimiento. # Solo tratamos el ultimo contorno de los 3.
		elif contorno < total and comenzarRegistroMovimiento == True and comprMancha == False:
			
			if (entPro == 0 and len(contornos) == 1) or (entPro == 1 and len(contornos) == contContornos):
				if len(contornos) > 1:
					print("Hay", len(contornos), "contornos, analizamos el", str(contContornos)+"º")
				
				# Hacemos una especie de contador para que solo lo haga 1 vez
				# Calculamos el punto (x2,y2):
				y2 = y1 + h
				x2 = x1 + w
				manchaNueva = umbralResta[y1:y2, x1:x2]
				pos = 0
				listaValores, pos, funciona = met.detMaxCoincMedium(listaHel, manchaNueva, entPro)
				
				if pos >= 0:
					iteracion += 1
					print("Analizamos el contorno",color)
					print("Hay movimiento, creemos que es el heliostato ", (pos+1))
					print(listaValores)

			else:
				continue

	# Mostramos las imágenes de la cámara, el umbral y la resta
	cv2.imshow("Camara",frame)
	cv2.imshow("Edges", edges)
	cv2.imshow("UmbralResta", umbralResta)
	cv2.imshow("Gris", gris)
	

	# Capturamos una tecla para salir
	key=cv2.waitKey(1)&0xFF	
	
	# Tiempo de espera para que se vea bien
	time.sleep(0.015)

	# Si ha pulsado la letra s, salimos
	if key == ord("s"):
		# Si forzamos la salida del programa calcularemos el tiempo de ejecucion y lo mostraremos por consola
		hora2 = time.time()
		break

	key = cv2.waitKey(1) & 0xFF
	if key == ord("k"):
		time.sleep(10)

# Calculamos el tiempo de ejecucion y lo mostramos por consola
hora2 = time.time()

print("Ha tardado un total de: ",hora2-hora1)

# Liberamos la cámara y cerramos todas las ventanas
camara.release()
cv2.destroyAllWindows()

