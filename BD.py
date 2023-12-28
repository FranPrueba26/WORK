
##### Codigo para cargar y manejar la base de datos en el servidor web #######


#### Librerias necesarias #####
import pymysql ##### Trabajar con mysql
import base64 #### Trabaja con base64
from datetime import date #### Trabaja con la fecha
from datetime import datetime, timedelta
from threading import Thread
from time import sleep
import os ### libreria de sistema operativo 

a=1 ## El activador, despues de procesar la imagen la activa para cargarla
cont = 0 ## Contador de la funcion  
Cont_Dia_anterior = 0 # Contador para el dia 0


####Imagen de Prueba (Se tiene que buscar en donde se va a almacenar la imagen) ####

Imagen = open('/home/fran/WORK/c.png','rb') ##### localizacion de la imagen a abir en formato de lectura de byte 


#### Abrir la base de datos en local por el momento #####
DB = pymysql.connect(
  host="localhost",
  user="root",
  password="260499",
  database="DB_Detector_Placas" 
)

Cursor = DB.cursor()### puntero que va a realizar las instrucciones

######Clase para la llamada a una hora determinada#######
##SACADO DE> https://es.stackoverflow.com/questions/38195/ejecutar-fragmento-de-c%C3%B3digo-a-una-hora-fecha-determinada-en-un-script-en-ejecuc##

class Temporizador(Thread):
    def __init__(self, hora, delay, funcion):
        # El constructor recibe como parámetros:
        ## hora = en un string con formato hh:mm:ss y es la hora a la que queremos que se ejecute la función.
        ## delay = tiempo de espera entre comprobaciones en segundos.
        ## funcion = función a ejecutar.

        super(Temporizador, self).__init__()
        self._estado = True
        self.hora = hora
        self.delay = delay
        self.funcion = funcion

    def stop(self):
        self._estado = False

    def run(self):
        # Pasamos el string a dato tipo datetime
        aux = datetime.strptime(self.hora, '%H:%M:%S')
        # Obtenemos la fecha y hora actuales.
        hora = datetime.now()
        # Sustituimos la hora por la hora a ejecutar la función.
        hora = hora.replace(hour = aux.hour, minute=aux.minute, second=aux.second, microsecond = 0)
        # Comprobamos si la hora ya a pasado o no, si ha pasado sumamos un dia (hoy ya no se ejecutará).
        if hora <= datetime.now():
            hora += timedelta(days=1)
        print('Ejecución automática iniciada')
        print('Proxima ejecución programada el {0} a las {1}'.format(hora.date(),  hora.time()))

        # Iniciamos el ciclo:
        while self._estado:
            # Comparamos la hora actual con la de ejecución y ejecutamos o no la función.
            ## Si se ejecuta sumamos un dia a la fecha objetivo.
            if hora <= datetime.now():
                self.funcion()
                print('Ejecución programada ejecutada el {0} a las {1}'.format(hora.date(),  hora.time()))
                hora += timedelta(days=1)
                print('Próxima ejecución programada el {0} a las {1}'.format(hora.date(),  hora.time()))

            # Esperamos x segundos para volver a ejecutar la comprobación.
            sleep(self.delay)

        #Si usamos el método stop() salimos del ciclo y el hilo terminará.
        else:
             print('Ejecución automática finalizada')

###### Funcion a ser llamada ########
def Insertar_Vehiculo(NumPlac, Fecha, Hora, Nota, NomImag, Imag): #Inserta las variables en la tabla de Placas
    global cont
    cont = cont + 1 
    sql = "insert into Placas (NumeroDePlaca, Fecha, Hora, Nota, NombreImagen, Imagen) values ('{}','{}','{}','{}','{}','{}')".format(NumPlac, Fecha, Hora, Nota, NomImag, Imag) ### codigo sql
    Cursor.execute (sql) ## instruccion a ejecutar
    DB.commit() ## guardar la base de datos
    #Cursor.execute("SELECT * FROM Placas") ## ejecutar esta secuencia sql que se mete en la tabla de PLacas
    #Fetch = Cursor.fetchall() ## hace un llamado a todos los datos de la tabla
    #for x in Fetch: ### imprime el Fetch con un for 
    #    print(x)
    return cont

def Insertar_Log(Fecha, NPlacas, NError, NCorrecta): #Inserta las variables en la tabla de Log
    sql = "insert into Log (Fecha, CantidadDePlacas, DeteccionErronea, DeteccionCorrecta) values ('{}','{}','{}','{}')".format(Fecha, NPlacas, NError, NCorrecta) ### codigo sql
    Cursor.execute (sql) ## instruccion a ejecutar
    DB.commit() ## guardar la base de datos
    #Cursor.execute("SELECT * FROM Log") ## ejecutar esta secuencia sql que se mete en la tabla de Log
    #Fetch = Cursor.fetchall() ## hace un llamado a todos los datos de la tabla
    #for x in Fetch: ### imprime el Fetch con un for 
    #    print(x)
    
def Guardar_Registro_Log(Registro): #Guardar el registro de Log
    with open("/home/fran/WORK/text/text.txt","a") as file: #Selecciona el lugar en donde se va a almacenar el registro LOG en este caso un txt
        file.write(Registro+"\n") #Funcion para escribir el registro con un salto de linea. 

def Seleccionar_Ultimo_Log():#Selecciona el ultimo registro de Log
    sql = "select * from Log order by id desc limit 1;" #Selecciona el ultimo registro de la tabla de Log
    Cursor.execute(sql) #ejecuta el codigo
    Fetch = Cursor.fetchall() ## hace un llamado a todos los datos de la tabla
    text = "{}".format(Fetch[0]) #convierte la funcion Fetch a un un formato de texto para que pueda ser escrita en el txt
    text = text.lstrip('(') #quita el primer parentesis 
    text = text.rstrip(')') #quita el primer parentesis 
    text = text.split(',') #Separa el text en varios textos por el parametro de la coma
    text = '|'+ " " + text[0]+' |'+text[1]+' /'+text[2]+' /'+text[3]+' |'+text[4]+' |'+text[5]+' |'+text[6]+' |' #Junta todos los txt necesarios
    text = text.replace('datetime.date','') #quita "datetime.date" del archivo de texto
    #for x in Fetch: ### imprime el Fetch con un for 
    #    print(x)
    Guardar_Registro_Log(text) #Llamar a la funcion 

    #TENGO QUE COMPROBAR QUE EL ULTIMO SEA SUBSIGUIENTE AL PENULTIMO 

def Conversor_Imagen_Base64(Imagen):#Conversion de la imagen a Base64

    image_read = Imagen.read() # Almacena la lectura de la imagen en la variable expuesta
    image_64_encode = base64.encodestring(image_read) #Codifica la imagen a base 64 
    #print (image_64_encode) #imprime el resultado obtenido
    text = image_64_encode.decode('utf-8') #tranforma el arreglo de byte a un texto
    #print(text) #imprime el texto
    return text #Devuelve el texto

def Guardar_Imagen(ID):#Guarda la imagen seleccionada
    sql = 'SELECT * FROM Placas WHERE id = {}'.format(ID) #Selecciona por el parametro id de la tabala Placas #####Modifica el ID
    Cursor.execute(sql) #ejecuta el codigo ### TENGO QUE REVISAR POR QUE NO SE PUEDEN DOS PARAMETROS
    Fetch = Cursor.fetchall() ## hace un llamado a todos los datos de la tabla
    for u in Fetch:
        #print('%d - %s' % (u[0], u[1]))#imprime el Fetch
        Decode_Imagen(u[0], u[-1]) #Manda a la funcion Decode_Imagen el parametro id y la imagen

    #TENGO QUE COMPROBAR QUE EL ULTIMO SEA SUBSIGUIENTE AL PENULTIMO 

def Decode_Imagen(ID, IMagen_Base):#Decodifica la imagen a jpg de Base64
    image_64_decode = base64.decodestring(IMagen_Base) # Decodifica la imagen en base
    image_result = open('/home/fran/WORK/Imag/Registro_By_ID_.png', 'wb') # Crea una imagen que se pueda escribir y deposita alli el valor de la decodificacion ### revisar el format
    image_result.write(image_64_decode) # El resultado de la imagen queda guardada
    Renombrar_Imagen(ID,"/home/fran/WORK/Imag/Registro_By_ID_.png")

def Renombrar_Imagen(ID,filename):#Renombra la imagen para que aparezca la ID en el nombre del archivo
    splitted = os.path.splitext(filename) #Separa la ubicacion del archivo de la extencion 
    new_filename = f'{splitted[0]} {ID}{splitted[1]}' #cancatena el viejo nombre del archivo con la ID de la imagen
    os.rename(filename, new_filename) #renombra la imagen

def Guardar_Registro_Placas(Registro): #Guardar el registro de Log
    with open("/home/fran/WORK/text/text2.txt","a") as file: #Selecciona el lugar en donde se va a almacenar el registro LOG en este caso un txt
        file.write(Registro+"\n") #Funcion para escribir el registro con un salto de linea. 

def Seleccionar_Ultima_Placa(): #Selecciona el ultimo registro de Placas
    sql = "select * from Placas order by id desc limit 1;" #Selecciona el ultimo registro de la tabla de Log
    Cursor.execute(sql) #ejecuta el codigo
    Fetch = Cursor.fetchall() ## hace un llamado a todos los datos de la tabla
    text = "{}".format(Fetch[0]) #convierte la funcion Fetch a un un formato de texto para que pueda ser escrita en el txt
    text = text.lstrip('(') #quita el primer parentesis 
    text = text.split(',') #Separa el text en varios textos por el parametro de la coma
    text = '|'+ " " + text[0]+' |'+text[1]+' |'+text[2]+' /'+text[3]+' /'+text[4]+' |'+text[5]+' |'+text[6]+' |'+text[7]+' |' #Junta todos los txt necesarios
    text = text.replace('datetime.date','') #quita "datetime.date" del archivo de texto
    
    #for x in Fetch: ### imprime el Fetch con un for 
    #    print(x)
    Guardar_Registro_Placas(text) #Llamar a la funcion 

    #TENGO QUE COMPROBAR QUE EL ULTIMO SEA SUBSIGUIENTE AL PENULTIMO 
    #ELIMINAR LOS PARENTESIS Y PONER || PARA QUE QUEDE MAS BONITO TOD
    #Eliminar las comas

def Crear_Log(B, Cont_Dia_anterior, Cont_Dia_actual): #####Esta es la funcion que se va a llamar una vez al dia####
    NError = 0
    NCorrecta = 0
    Cont = Cont_Dia_actual
    Count = Cursor.execute("SELECT * FROM Placas") #Contador de numero de filas de la tabla placa Me da el numero total 
    Count_Aux = Count - Cont_Dia_anterior # contador auxiliar para delimitar cuantos son del dia actual
    if Count_Aux == Cont_Dia_actual: #Condicional que establece que si  el numero de filas es igual al numero de llamados la funcion es correcta
        NCorrecta = Cont_Dia_actual # igualacion del numero correcto de placas
        NError = 0 #error igual a cero
    else: # Caso contrario hay un error en una o varias de las filas y se resta el numero de veces llamadas menos el numero de lineas
        NError= Cont_Dia_actual - Count_Aux #El numero de veces llamadas debera ser siempre mayor o igual al numero de lineas
        NCorrecta = Cont_Dia_actual - NError # EL numero correcto va a ser el dia actual menos el error
    Insertar_Log(B, Cont, NError, NCorrecta)

def Dia_anterio ():
    Cont_Dia_anterior = Cursor.execute("SELECT * FROM Placas") #Contador de numero de filas de la tabla placa, se hace este proceso para saber cuantas filas hay del dia anterior y asegurar que siempre sea mayor  
    Cont_Dia_anterior = Cont_Dia_anterior # El contador del ultimo registro del dia anteriro +1 
    return Cont_Dia_anterior

def Ejecución():
    global Cont_Dia_anterior #primera llamada
    Crear_Log(B,Cont_Dia_anterior, Cont_Dia_actual)
    Seleccionar_Ultimo_Log()
    Cont_Dia_anterior = Dia_anterio ()

#####Variables######

A = 'HASXA25' ## guarda la variable de la placa en A
B = date.today() ## guarda la variable del dia en B
C = datetime.now().time() ## guarda la variable de la hora en C
D = "NA" ## guarda la variable de la Nota en D
E = "NomImag" ## guarda la variable del nombre de la imagen en E
F = Conversor_Imagen_Base64(Imagen) ## guarda la variable de la imagen en F

####Llamar a la funcion con las variables#####

t = Temporizador('23:08:00',1,Ejecución)# Instanciamos nuestra clase Temporizador
t.start() #Iniciamos el hilo

while a<100:
    Cont_Dia_actual = Insertar_Vehiculo(A, B, C, D, E, F)
    print(a)
    sleep(1)
    a = a+1

#Guardar_Imagen(145)## modificar el numero con un fetch del ultimo y listo 
#Seleccionar_Ultima_Placa()

###### Guardar y cerrar ####
#Cursor.close()
#DB.close()

#################   Ver si puedo ver las imagnes que se cargaron a mysql ##########3    Cont_Dia_actual
