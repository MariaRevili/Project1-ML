import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.preprocessing import StandardScaler


###Download the data
url = "https://raw.githubusercontent.com/MariaRevili/FYS-STK4155/master/Project3/eyeData.csv"
data = pd.read_csv(url)
data = data.iloc[:, 1:]
X = data.iloc[:, 0:14]
#print(X.head(3))
y = data.iloc[:, 14]
data = pd.DataFrame(data)
#print(y.head(3))
# print(data["eyeDetection"].mean())


##scale the data 

scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

### Obtain predictions from each weak tree and then use these predictions as covariates for neural networks
np.random.seed(20)
n = 1000
pred_mat = np.ones((y.size, 1))

rf=RandomForestClassifier(n_estimators=1000, bootstrap=True) ##Number of Trees to build
rf.fit(X, y)

for tree in rf.estimators_:
    per_tree_pred = tree.predict(X).reshape(-1,1)
    pred_mat = np.c_[pred_mat, per_tree_pred]

pred_mat = pd.DataFrame(pred_mat)
pred_mat = pred_mat.iloc[:, 1:]
print(pred_mat.head(5))

X_train, X_test, y_train, y_test = train_test_split(pred_mat, y, test_size=0.2, random_state=1)


####Feed these predicted values instead of original covariates into neural networks

from tensorflow.keras.layers import Input
from tensorflow.keras.models import Sequential      #This allows appending layers to existing models
from tensorflow.keras.layers import Dense           #This allows defining the characteristics of a particular layer
from tensorflow.keras import optimizers             #This allows using whichever optimiser we want (sgd,adam,RMSprop)
from tensorflow.keras import regularizers           #This allows using whichever regularizer we want (l1,l2,l1_l2)
from tensorflow.keras.utils import to_categorical   #This allows using categorical cross entropy as the cost function
from tensorflow.keras import initializers
from tensorflow.keras.layers.experimental import preprocessing


epochs = 100
batch_size = 100
n_neurons_layer1 = 100
n_neurons_layer2 = 100
n_categories = 10
eta_vals = np.logspace(-5, 0, 5)
lmbd_vals = np.logspace(-5, 0, 5)

def neural_network_keras(n_neurons_layer1, n_neurons_layer2, eta, lmbd):  ##Build the model
    model = Sequential()
    model.add(Dense(n_neurons_layer1, activation='sigmoid', kernel_regularizer=regularizers.l2(lmbd)))
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])  ##try adam also
    
    return model

DNN_keras = np.zeros((len(eta_vals), len(lmbd_vals)), dtype=object)
  
def train_dnn():    ##fit for different learning rate and decay (lambda)  
    for i, eta in enumerate(eta_vals):
        for j, lmbd in enumerate(lmbd_vals):
            DNN = neural_network_keras(n_neurons_layer1, n_neurons_layer2, 
                                            eta=eta, lmbd=lmbd)
            DNN.fit(X_train, y_train, validation_split=0.2, epochs=epochs, batch_size=batch_size, verbose=0) ##what is verbose?
            y_pred = DNN.predict_classes(X_test)
            scores = DNN.evaluate(X_test, y_test, verbose=1)
            
            DNN_keras[i][j] = DNN
            
            print("Learning rate = ", eta)
            print("Lambda = ", lmbd)
            print("Test MSE = ", scores)
            print()  
  
#train_dnn()  
DNN = neural_network_keras(n_neurons_layer1, n_neurons_layer2, 
                                 eta=1, lmbd=1)
DNN.fit(X_train, y_train, validation_split=0.2, epochs=epochs, batch_size=batch_size, verbose=0) ##what is verbose?
y_pred = DNN.predict_classes(X_test)
scores = DNN.evaluate(X_test, y_test, verbose=1)
print("Test MSE = ", scores)