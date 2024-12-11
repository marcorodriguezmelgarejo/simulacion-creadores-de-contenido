import json
from fitter import Fitter

# Step 1: Read the data from the file
with open('C:\\Users\\Marco\\OneDrive - UTN.BA\\UTN\\Simulación\\TP-final\\Datasets\\orders-dataset.json', 'r') as file:
    data = json.load(file)

# Step 2: Filter the items whose type is "performer_subscription"
filtered_items = [item['item'] for item in data if item['item']['type'] == 'performer_subscription']

# Step 3: Extract the prices of the filtered items
prices = [item['price'] for item in filtered_items]

# Step 4: Use the fitter library to find the best-fitting probability distribution
f = Fitter(prices)
f.fit()
f.summary()

# # Print the best-fitting distribution
print(f.get_best())
# Resultado: {'gengamma': {'a': 1.3744527645148987, 'c': 0.21986643848319853, 'loc': 9.999999999999998, 'scale': 0.4219069229308876}}