import numpy as np
import cv2
import time
import math
from matplotlib import pyplot as plt


# Lo declaro arriba para poder usarlo abajo xD
# Es como el anterior comprobarPAP pero reduzco la busqueda al borde izquierdo
def comprobarPAP2(array, mancha):
	array2 = aumentarLista(array,None) 
	listaMancha = []
	hora1 = time.time()
	for k in array2:
		hora5 = time.time()
		lista = []
		for x in range(0,3):#mancha.shape[0]
			for y in range(0,k.shape[1]):
				cont = 0
				for x2 in range(0,mancha.shape[0]):
					for y2 in range(0,mancha.shape[1]):
						if (mancha.shape[1]+y)<=k.shape[1] and (mancha.shape[0]+x)<=k.shape[0]:
							if mancha[x2][y2] == k[x+x2][y+y2]:
								cont+=1		
						else:
							break
				lista.append(cont)
		listaMancha.append(max(lista))
		hora4 = time.time()
		#print("Procesamiento de la mancha:", (hora4-hora5),"segundos.")
	print("elementos en listaMancha",listaMancha[0],listaMancha[1],listaMancha[2],listaMancha[3])
	hora2 = time.time()
	#print("ComprobarPAP dura", (hora2-hora1), "segundos.")
	return listaMancha.index(max(listaMancha))

# Metodo para añadir una cantidad de ceros a la izquierda.
def aumentarLista(lista, cantidad):
	if cantidad == None:
		cantidad=2
	listaFinal = []
	listaFinalAux = []
	lista1 = []
	lista2 = []
	# Llenamos una lista con la cantidad de 0 que queremos añadir
	for x in range(0,cantidad):#mancha.shape[0]
		lista1.append(0)

	for x in lista:
		for y in x:
			lista2 = lista1.copy()		# Copiamos la lista llena de 0
			lista3 = y.copy().tolist()	# Convertimos la numpy.ndarray en una lista
			lista2.extend(lista3)		# Juntamos las dos listas 
			listaFinalAux.append(lista2)# Añadimos en una lista todas las listas con los 0s ya añadidos
		listaFinal.append(np.array(listaFinalAux)) # Añadimos en una lista normal la lista de tipo ndarray
		listaFinalAux = []
	return listaFinal


# metodo para pintar las manchas
def visualizarLista(lista):
	lista1 = ["mancha1.jpg","mancha2.jpg","mancha3.jpg","mancha4.jpg"]
	i=0
	for x in lista:
		cv2.imwrite(lista1[i], x)
		i+=1
	#cv2.imwrite("berruga.jpg", mancha)

# Metodo que devuelve el umbral introduciendo una imagen
def umbralizar(gris):
	return cv2.threshold(gris, 100, 255, cv2.THRESH_BINARY)[1] 

# 120 para varios_heliostatos
# 150 para 
# 120 para hacesLuzLinterna3
	
# Este metodo te devuelve el umbral apartir de un tono de gris.
def umbralNum(gris, num):
	return cv2.threshold(gris, num, 255, cv2.THRESH_BINARY)[1]

# Metodo para saber cuando una lista esta vacia. 
# Intentamos obtener el primer elemento, si salta la excepcion es que esta vacia
def listaVacia(lista):
	try: 
		listt = lista[0] 
		return False
	except:
		return True

def detMaxCoinc(lista, manchaNueva):
	listaValores = []
	funciona = True
	for x in lista:
		img = x
		w, h = manchaNueva.shape[::-1]
		# Apply template Matching
		if x.shape[0]<manchaNueva.shape[0] or x.shape[1]<manchaNueva.shape[1]:
			funciona = False
			listaValores.append(0)
			continue
		res = cv2.matchTemplate(img, manchaNueva, cv2.TM_CCOEFF) #'cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED'
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		listaValores.append(max_val)
	
	if not listaValores:
		return listaValores, -1, False
	# Comprobamos que haya diferencia entre los valores del array	
	#elif max(listaValores) <= (min(listaValores)+100):
		#return listaValores, -1, False
	else:
		return listaValores, listaValores.index(max(listaValores)), funciona

def detMaxCoincMedium(lista, manchaNueva, entPro):
	manchaNueva = getMedium(manchaNueva, entPro)

	listaValores = []
	listaValoresRes = []
	diccionario = {}
	funciona = True
	i = 0
	for x in lista:
		x = getMedium(x, entPro)
		img = x
		w, h = manchaNueva.shape[::-1]
		# Apply template Matching
		if x.shape[0]<manchaNueva.shape[0] or x.shape[1]<manchaNueva.shape[1]:
			funciona = False
			listaValores.append(0)
			i+=1
			continue
		res = cv2.matchTemplate(img, manchaNueva, cv2.TM_CCOEFF) #'cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED', TM_SQDIFF

		listaValoresRes.append(res)
		#diccionario[i] = res
		i+=1

		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		listaValores.append(max_val)

	if not listaValores:
		return listaValores, -1, False
	# Comprobamos que haya diferencia entre los valores del array	
	elif max(listaValores) <= (min(listaValores)+100):
		return listaValores, -1, False
	else:
		return listaValores, listaValores.index(max(listaValores)), funciona

def getMedium(img, entPro):
	# Calculamos las coordenadas para partir la imagen a la mitad
	(x1, y1, w, h) = cv2.boundingRect(img)
	#calculamos el punto (x2,y2):
	y2 = y1 + h
	x2 = x1 + w
	# punto medio
	x3 = (x1+x2)/2

	if entPro == 0:
		manchaNueva = img[y1:y2, x1:int(x3)]
	else:
		manchaNueva = img[y1:y2, int(x3):x2]
	return manchaNueva

def lorenzo2(lista, mancha):
	listaValores = []
	for x in lista:
		img = x
		cv2.imshow("Camara", img)
		img2 = img.copy()
		template = mancha
		w, h = template.shape[::-1]
		# Apply template Matching
		res = cv2.matchTemplate(img,template, cv2.TM_CCOEFF) #'cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED'
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		res2 = res.copy().tolist()
		mayor = res2.count(max(res2))
		listaValores.append(mayor)
		print(mayor, max_val)
		print(listaValores)

		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)
		cv2.rectangle(img,top_left, bottom_right, 255, 2)
		plt.subplot(121),plt.imshow(res,cmap = 'gray')
		plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
		plt.subplot(122),plt.imshow(img,cmap = 'gray')
		plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
		plt.show()	

	return listaValores.index(max(listaValores))

def sortContours(cnts):
	diccionario = {}
	result = []
	for c in cnts:
		# Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
		(x1, y1, w, h) = cv2.boundingRect(c)
		diccionario[x1] = c

	dictionary_items = diccionario.items() 
	sorted_items = sorted(dictionary_items)
	for x, c in sorted_items:
		result.append(c)

	return result
