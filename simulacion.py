from dataclasses import dataclass
from random import random
from scipy import stats
import sys

### ALIAS DE TIPO ###
Tiempo = int
Dinero = int

### CONSTANTES ###
unaSemana: Tiempo = 7 * 24 * 60
highValue = sys.maxsize # máximo valor de entero posible en Python

### ESTRUCTURAS DE DATOS ###
@dataclass
class Estado:
    dineroDisponible: Dinero = 0
    cantidadSolicitudesExclusivasEnCola: int = 0
    def imprimir(self):
        print(" --- ESTADO --- ")
        print(f"Dinero disponible: {self.dineroDisponible}")
        print(f"Cantidad de solicitudes exclusivas en cola: {self.cantidadSolicitudesExclusivasEnCola}")
        print("\n")

@dataclass
class Control:
    intervaloEntreSubidas: Tiempo
    precioSuscripcion: Dinero
    def imprimir(self):
        print(" --- VARIABLES DE CONTROL --- ")
        print(f"Intervalo entre subidas: {self.intervaloEntreSubidas}")
        print(f"Precio de suscripcion: {self.precioSuscripcion}")
        print("\n")

@dataclass
class VariablesAuxiliares:
    sumatoriaDineroGastado = 0
    compras = 0
    totalPropinas = 0
    arrepentidos = 0
    contenidoTotalSubido: int = 0
    def imprimir(self):
        print(" --- VARIABLES AUXILIARES --- ")
        print(f"Sumatoria de dinero gastado: {self.sumatoriaDineroGastado}")
        print(f"Cantidad de compras: {self.compras}")
        print(f"Cantidad de arrepentidos: {self.arrepentidos}")
        print(f"Total de propinas: {self.totalPropinas}")
        print("\n")

@dataclass
class Resultados:
    gananciasAnuales: float
    engagement: float
    porcentajeDePropinas: float
    costoDeProduccionAnual: float

    def __init__(self, estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoFinal: Tiempo):
        self.costoDeProduccionAnual = variablesAuxiliares.sumatoriaDineroGastado / (tiempoFinal / 60 / 24 / 30 / 12)
        self.gananciasAnuales = (dineroGanado(estado, variablesAuxiliares) - variablesAuxiliares.sumatoriaDineroGastado) / (tiempoFinal / 60 / 24 / 30 / 12)
        self.porcentajeDePropinas = 100 * variablesAuxiliares.totalPropinas / dineroGanado(estado, variablesAuxiliares) if dineroGanado(estado, variablesAuxiliares) != 0 else 0
        self.engagement = (variablesAuxiliares.compras - variablesAuxiliares.arrepentidos) * 100 / variablesAuxiliares.compras if variablesAuxiliares.compras != 0 else 0

    def imprimirEnVariasLineas(self):
        print(" --- RESULTADOS --- ")
        print(f"Ganancias anuales: {self.gananciasAnuales:.2f}") # lo más importante que queremos maximizar
        print(f"Porcentaje de propinas en los ingresos totales: {self.porcentajeDePropinas:.2f}%")
        print(f"Engagement: {self.engagement:.2f}%") # también es importante maximizar, es un indicador más a largo plazo
        print(f"Costo de Produccion Anual: {self.costoDeProduccionAnual:.2f}")
        print("\n")

    def imprimir(self):
        print(f"Ganancias anuales: {self.gananciasAnuales:.2f}, Porcentaje de propinas en los ingresos: {self.porcentajeDePropinas:.2f}%, Engagement: {self.engagement:.2f}%, Costo de Produccion Anual: {self.costoDeProduccionAnual:.2f}")
    
    def imprimirSinCostoDeProduccionAnual(self):
        print(f"Ganancias anuales: {self.gananciasAnuales:.2f}, Porcentaje de propinas en los ingresos: {self.porcentajeDePropinas:.2f}%, Engagement: {self.engagement:.2f}%")

@dataclass
class SalidaSimulacion:
    estado: Estado
    resultados: Resultados

    def imprimir(self):
        self.estado.imprimir()
        self.resultados.imprimirEnVariasLineas()

class Datos:
    def intervaloEntreCompras(self):
        c = 0.6992732706985292
        loc = 0
        scale = 21.92617425196091
        # Generamos valores aleatorios que siguen la distribución Weibull Min
        return int(stats.weibull_min.rvs(c, loc, scale, random_state=None))

    def montoPropina(self) -> Dinero:
        dgamma = 0.26918309159509146
        loc = 19.99999999999999
        scale = 19.08326487029376
        random_value = -1
        while random_value < 0:
            random_value = int(stats.dgamma.rvs(dgamma, loc, scale, random_state=None))
        return random_value
    
    def precioAceptableSuscripcion(self) -> Dinero:
        parametros = {'a': 2.1073297452845834, 'loc': 28.178771593939764, 'scale': 2.8079889625195245}
        random_value = -1
        while random_value < 0:
            random_value = int(stats.dgamma.rvs(**parametros, random_state=None))
        return random_value

class TiempoActual:
    tiempo: Tiempo
    def __init__(self, tiempoInicial: Tiempo):
        self.tiempo = tiempoInicial
    def avanzarTiempoA(self, tiempo: Tiempo):
        self.tiempo = tiempo

class TablaDeEventosFuturos:
    tiempoProximaCompra: Tiempo = 0
    tiempoProximoContenidoASubir: Tiempo = 0
    tiempoProximaSubidaSolicitudExclusiva: Tiempo = 0

    def proximoEvento(self):
        TEF = [(self.tiempoProximaCompra, eventoCompra),
            (self.tiempoProximoContenidoASubir, eventoSubidaContenido),
            (self.tiempoProximaSubidaSolicitudExclusiva, eventoSubidaSolicitudExclusiva)]
        return min(TEF, key = lambda x: x[0] )[1] # Busca el tiempo de proximo evento más cercano (o sea el minimo), agarra su evento asociado, y crea una instancia nueva

### EVENTOS ###
def eventoSubidaSolicitudExclusiva(estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, control: Control, tef: TablaDeEventosFuturos):
    tiempoActual.avanzarTiempoA(tef.tiempoProximaSubidaSolicitudExclusiva)
    costoDeProd = costoDeProduccion()
    gastarDinero(costoDeProd, estado, variablesAuxiliares)
    estado.cantidadSolicitudesExclusivasEnCola -= 1
    if(estado.cantidadSolicitudesExclusivasEnCola >= 1):
        tef.tiempoProximaSubidaSolicitudExclusiva = tiempoActual.tiempo + unaSemana
    else:
        tef.tiempoProximaSubidaSolicitudExclusiva = highValue

def eventoSubidaContenido(estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, control: Control, tef: TablaDeEventosFuturos):
    tiempoActual.avanzarTiempoA(tef.tiempoProximoContenidoASubir)
    tef.tiempoProximoContenidoASubir = tiempoActual.tiempo + control.intervaloEntreSubidas
    variablesAuxiliares.contenidoTotalSubido += 1
    costoProd = costoDeProduccion()
    gastarDinero(costoProd, estado, variablesAuxiliares)

def suscripcion(control: Control, estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, tef: TablaDeEventosFuturos):
    ganarDinero(control.precioSuscripcion, estado)

def propina(control: Control, estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, tef: TablaDeEventosFuturos):
    montoPropina = Datos().montoPropina()
    ganarDinero(montoPropina, estado)
    variablesAuxiliares.totalPropinas += montoPropina

def compraSolicitudExclusiva( control: Control, estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, tef: TablaDeEventosFuturos):
    estado.cantidadSolicitudesExclusivasEnCola += 1
    ganarDinero(30, estado)
    if (estado.cantidadSolicitudesExclusivasEnCola == 1):
        tef.tiempoProximaSubidaSolicitudExclusiva = tiempoActual.tiempo + unaSemana

def eventoCompra(estado: Estado, variablesAuxiliares: VariablesAuxiliares, tiempoActual: TiempoActual, control: Control, tef: TablaDeEventosFuturos):
    tiempoActual.avanzarTiempoA(tef.tiempoProximaCompra)
    intervaloEntreCompras = Datos().intervaloEntreCompras()
    tef.tiempoProximaCompra = tiempoActual.tiempo + intervaloEntreCompras
    variablesAuxiliares.compras += 1
    if (arrepentido(variablesAuxiliares.contenidoTotalSubido, estado.dineroDisponible, tiempoActual)):
        variablesAuxiliares.arrepentidos += 1
        return
    tipoDeCompra = eleccionAleatoria(
        [(0.7, suscripcion),
            (0.2, propina),
            (0.1, compraSolicitudExclusiva)])
    if (tipoDeCompra == suscripcion and arrepentidoDeSuscribirse(control.precioSuscripcion)):
        variablesAuxiliares.arrepentidos += 1
        return
    tipoDeCompra(control, estado, variablesAuxiliares, tiempoActual, tef)

### FUNCIONES AUXILIARES ###
def ganarDinero(dinero, estado):
    estado.dineroDisponible += dinero

def gastarDinero(dinero, estado, variablesAuxiliares):
    estado.dineroDisponible -= dinero
    variablesAuxiliares.sumatoriaDineroGastado += dinero

def dineroGanado(estado, variablesAuxiliares):
    # DineroDisponible = DineroGanado - DineroGastado => DineroGanado = DineroDisponible + DineroGastado
    return estado.dineroDisponible + variablesAuxiliares.sumatoriaDineroGastado

def costoDeProduccion() -> Dinero:
    return eleccionAleatoria(
        [(0.1, 20), # Album: 10 por ciento de probabilidad, 20 dolares
         (0.5, 5), # Foto: 50 por ciento de probabilidad, 5 dolares
         (0.4, 10)]) # Video: 40 por ciento de probabilidad, 10 dolares

def arrepentido(contenidoTotalSubido: int, dineroDisponible: Dinero, tiempoActual: TiempoActual) -> bool:
    return arrepentidoPorNoSerTopCreator(dineroDisponible, tiempoActual) or arrepentidoPorPocoContenido(contenidoTotalSubido, tiempoActual.tiempo)

def arrepentidoPorNoSerTopCreator(dineroDisponible, tiempoActual) -> bool:
    return not topCreator(dineroDisponible, tiempoActual) and random() < 0.4

def arrepentidoDeSuscribirse(precioSuscripcion: Dinero) -> bool:
    return arrepentidoPorPrecioCaro(precioSuscripcion)

def arrepentidoPorPrecioCaro(precioSuscripcion: Dinero) -> bool:
    precioLimiteParaEseCliente = Datos().precioAceptableSuscripcion()
    return precioSuscripcion > precioLimiteParaEseCliente # Si el precio que cobramos es mayor a lo que esta dispuesto a pagar, se arrepiente y no compra

def arrepentidoPorPocoContenido(contenidoTotalSubido: int, tiempoActual: Tiempo) -> bool:
    # Si sube en promedio 0 contenidos por mes, la probabilidad de arrepentirse es 1. Si sube 10 contenidos por mes o más, la probabilidad de arrepentirse es 0.
    if tiempoActual == 0:
        return False
    contenidoPromedioPorMes = contenidoTotalSubido / (tiempoActual / 60 / 24 / 30)
    return random() < (1 - min(contenidoPromedioPorMes, 10) / 10)

def topCreator(dineroGanado: Dinero, tiempoActual: TiempoActual) -> bool:
    if tiempoActual.tiempo == 0:
        return False
    gananciaPromedioPorMes = dineroGanado / ( tiempoActual.tiempo / 60 / 24 / 30 / 12 )
    return gananciaPromedioPorMes > 100_000

def eleccionAleatoria(probabilidadesConOpciones):
    sumaProbabilidades = sum(probabilidad for probabilidad, opcion in probabilidadesConOpciones)
    if ( sumaProbabilidades > 1.001 or sumaProbabilidades < 0.999):
        raise ValueError("Las probabilidades no suman 1, suman " + str(sumaProbabilidades) + ". Probabilidades: " + str(probabilidadesConOpciones))
    r = random()
    probabilidadAcumulada = 0
    for probabilidad, opcion in probabilidadesConOpciones:
        probabilidadAcumulada += probabilidad # por ej cuando se usa en la suscripcion, probabilidadAcumulada empieza siendo 0.7, después es 0.9 y después 1 (entra seguro, es como el else)
        if r <= probabilidadAcumulada:
            return opcion
    return probabilidadesConOpciones[-1][1] # Retorna la ultima opcion (igual no deberia llegar a esta linea porque las probabilidades suman 1)

def eleccionAleatoriaBinaria(probabilidad, valorSiExito, valorSiFracaso):
    return eleccionAleatoria([(probabilidad, valorSiExito), (1 - probabilidad, valorSiFracaso)])

def dias(n: int) -> Tiempo:
    return n * 24 * 60

def meses(n: int) -> Tiempo:
    return dias(30) * n

def anios(n: int) -> Tiempo:
    return meses(12) * n

### RUTINA PRINCIPAL ###
def simulacion(tiempoFinal: Tiempo, intervaloEntreSubidas: Tiempo, precioSuscripcion: Dinero) -> Resultados:
    tiempoActual: TiempoActual = TiempoActual(0)
    tef: TablaDeEventosFuturos = TablaDeEventosFuturos()
    estado: Estado = Estado()
    variablesAuxiliares: VariablesAuxiliares = VariablesAuxiliares()
    control = Control(intervaloEntreSubidas, precioSuscripcion)
    while (tiempoActual.tiempo < tiempoFinal):
        proxEvento = tef.proximoEvento()
        proxEvento(estado, variablesAuxiliares, tiempoActual, control, tef)
    return Resultados(estado, variablesAuxiliares, tiempoActual.tiempo)

def simularEImprimirResultados(tiempoFinal: Tiempo, intervaloEntreSubidas: Tiempo, precioSuscripcion: Dinero):
    Control(intervaloEntreSubidas, precioSuscripcion).imprimir()
    simulacion(tiempoFinal, intervaloEntreSubidas, precioSuscripcion).imprimirEnVariasLineas()

def simularVariasVeces(meses):
  simulaciones = [simulacion(tiempoFinal=meses(meses), intervaloEntreSubidas=60 * 2, precioSuscripcion=5) for i in range(5)]
  print("rentabilidad")
  for sim in simulaciones:
      print(sim.gananciasAnuales)
  print("engagement")
  for sim in simulaciones:
      print(sim.engagement)
  print("porcentaje de propinas")
  for sim in simulaciones:
      print(sim.porcentajeDePropinas)

  print("variabilidad rentabilidad")
  print(max(simulaciones, key = lambda x: x.gananciasAnuales).gananciasAnuales - min(simulaciones, key = lambda x: x.gananciasAnuales).gananciasAnuales)

  print("variabilidad engagement")
  print(max(simulaciones, key = lambda x: x.engagement).engagement - min(simulaciones, key = lambda x: x.engagement).engagement)

  print("variabilidad porcentaje de propinas")
  print(max(simulaciones, key = lambda x: x.porcentajeDePropinas).porcentajeDePropinas - min(simulaciones, key = lambda x: x.porcentajeDePropinas).porcentajeDePropinas)

# --- EJECUCION DE LA SIMULACION - COPIADO DEL GOOGLE COLLAB --- #

def simularVariasVecesConDistintosTiempos():
    # Ejecuto varias veces la simulación con distintos tiempos finales, para ver qué tiempo final es suficiente para tener resultados 
    # consistentes, sin aumentar demasiado el tiempo de procesamiento.
    simularVariasVeces(1)
    simularVariasVeces(30)
    simularVariasVeces(60)
    simularVariasVeces(120)
    # Conclusión: es suficiente ejecutar la simulación con un tiempo final de 30 meses.

def ejecucionesSimulacion():
    # Probamos ejecutar con distintos valores de las variables de control. Variamos individualmente las dos variables, para encontrar el valor óptimo de ambas.

    # --- Varío el intervalo entre subidas, manteniendo el precio de suscripción fijo en 5 dólares ---
    # Buscamos el mejor intervalo entre subidas, dejando fijo el parámetro del precio de la suscripción, y analizando cómo varían los resultados.
    # El mejor valor para el intervalo entre subidas es 3 días. Al igual que 1 y 2 días, este otorga un engagement cercano al 100 por ciento, 
    # y ganancias anuales cercanas a los 200 mil dólares. Pero, a diferencia de los otros dos, disminuye el costo de producción anual a los 
    # 1450 dólares. Esto hace que, si analizamos la mejoría en estos 3 resultados, el intervalo entre subidas de 3 días sea el valor óptimo.
    # Para el análisis de este parámetro, no consideramos la variación en el porcentaje de propinas en los ingresos totales, ya que no es un 
    # resultado que se vea afectado significativamente por el mismo.
    print("1 hora")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=60, precioSuscripcion=5).imprimir()
    print("1 día")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(1), precioSuscripcion=5).imprimir() 
    print("2 días")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(2), precioSuscripcion=5).imprimir()
    print("3 días") # -> MEJOR VALOR
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=5).imprimir()
    print("4 días")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(4), precioSuscripcion=5).imprimir()
    print("7 días")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(7), precioSuscripcion=5).imprimir()
    print("15 días")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(15), precioSuscripcion=5).imprimir()

    #  --- Varío el precio de la suscripción, manteniendo el intervalo entre subidas fijo en 3 días ---
    # Para buscar el mejor valor posible de esta variable, vamos a intentar, principalmente, maximizar las ganancias anuales. Como objetivo 
    # secundario, también queremos disminuir al mínimo el porcentaje de propinas en los ingresos totales. Reducir este valor es positivo para
    # los creadores de contenido, porque los hace menos dependientes de las variaciones propias de este tipo de ingreso. Por otro lado, al 
    # parámetro del Engagement no le vamos a dar tanta importancia en este análisis, porque es natural que al aumentar el precio de la 
    # suscripción, ciertos clientes prefieran no contratar la misma. Sin embargo, si el precio elegido es el correcto, esta disminución en 
    # las ventas se ve compensada por un aumento en la ganancia correcta. Nuestro objetivo al ajustar esta variable es buscar el punto medio 
    # adecuado que aumenta nuestras ganancias por venta, sin afectar demasiado las ventas totales, manteniendo al máximo posible las ganancias. 
    # Por último, el resultado del costo de producción debe ser ingnorado en este análisis, ya que no es afectado por el precio que eligamos. 
    # Las variaciones en ese resultado, son en este caso propias de la aleatoriedad de la simulación realizada.
    # De los casos planteados, los que otorgan mayores ganancias son los que tienen precios de suscripción de 20 y 22 dólares. Estos dos son
    # muy similares en cuanto a ganancias. Lo que sí varía considerablemente, es el Engagement, que es mayor cuando el precio es de 20 dólares.
    # Es por eso que vamos a elegir como mejor el precio de 20 dólares, ya que mejora el Engagement manteniendo ganancias similares. Esto le 
    # permite al creador de contenido tener una mayor base de clientes, lo que aporta más estabilidad en sus ingresos.
    # Si se quisiera seguir analizando más en detalle, se podrían probar todos los valores cercanos a 20, hasta la precisión del centavo, con 
    # tiempos de ejecución de simulación mayores. Esto permitiría afinar aún más el valor, encontrando el precio ideal.
    print("5 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=5).imprimir() 
    print("10 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=10).imprimir()
    print("20 dólares") # -> MEJOR VALOR
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=20).imprimir()
    # No incluyo en el análisis por ser muy parecido a 22 dólares. Si se quisiera ver más en detalle cuál es el mejor, se podría ejecutar la simulación con un mayor tiempo final.
    # print("21 dólares")
    # simulacion(tiempoFinal=meses(90), intervaloEntreSubidas=dias(3), precioSuscripcion=21).imprimir() 
    print("22 dólares")
    simulacion(tiempoFinal=meses(90), intervaloEntreSubidas=dias(3), precioSuscripcion=22).imprimir()
    # print("23 dólares")
    # simulacion(tiempoFinal=meses(90), intervaloEntreSubidas=dias(3), precioSuscripcion=23).imprimir()
    # print("24 dólares")
    # simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=24).imprimir()
    print("25 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=25).imprimir()
    print("50 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=50).imprimir()

    # --- Estudio combinaciones de los valores ---
    # Debería ser el mejor
    print("3 días y 20 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=20).imprimir()
    # Cercanos al mejor resultado
    print("Cercanos al mejor resultado")
    print("Variando el precio de la suscripción")
    print("3 días y 22 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=22).imprimir()
    print("3 días y 10 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(3), precioSuscripcion=10).imprimir()
    print("Variando el intervalo entre subidas")
    print("4 días y 20 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(4), precioSuscripcion=20).imprimir()
    print("2 días y 20 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(2), precioSuscripcion=20).imprimir()
    print("Variando ambos")
    print("4 días y 22 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(4), precioSuscripcion=22).imprimir()
    print("2 días y 10 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(2), precioSuscripcion=10).imprimir()
    # Lejanos al mejor resultado, muy extremos para arriba y para abajo
    print("Lejanos al mejor resultado")
    print("30 días y 1 dólar")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=dias(30), precioSuscripcion=1).imprimir()
    print("1 hora y 50 dólares")
    simulacion(tiempoFinal=meses(30), intervaloEntreSubidas=60, precioSuscripcion=50).imprimir()