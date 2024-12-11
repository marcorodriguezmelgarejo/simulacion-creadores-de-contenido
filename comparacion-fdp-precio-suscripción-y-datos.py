import json
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.stats import gengamma

# Cargar los datos
with open('C:\\Users\\Marco\\OneDrive - UTN.BA\\UTN\\Simulación\\TP-final\\Datasets\\orders-dataset.json', 'r') as file:
    data = json.load(file)

# Extraer los precios de suscripción
suscripciones = [item['item'] for item in data if item['item']['type'] == 'performer_subscription']
prices = [item['price'] for item in suscripciones]

# Generar valores aleatorios de la distribución ajustada
random_values = []
while len(random_values) < 10000:
    a = 1.3744527645148987
    c = 0.21986643848319853
    loc = 9.999999999999998
    scale = 0.4219069229308876
    random_values.append(int(stats.gengamma.rvs(a, c, loc, scale, random_state=None)))

# Graficar histogramas de los datos originales y de la distribución a la que ajustamos
plt.hist(prices, bins=30, density=True, alpha=0.6, color='g', label='Datos originales')
plt.hist(random_values, bins=30, density=True, alpha=0.6, color='b', label='Valores aleatorios generados')

# Graficar la distribución ajustada
x = np.linspace(min(prices), max(prices), 100)
pdf_fitted = gengamma.pdf(x, a, c, loc, scale)
plt.plot(x, pdf_fitted, 'r-', label='Distribución ajustada (gengamma)')

# Configurar el gráfico
plt.xlabel('Precio de suscripción')
plt.ylabel('Densidad de probabilidad')
plt.legend()
plt.title('Comparación entre datos originales y distribución ajustada')
plt.show()

# TODO: Arreglar esto con mi compañero, no sé qué onda