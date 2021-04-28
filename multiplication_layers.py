import seaborn as sns
import matplotlib.pyplot as plt
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Multiply
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
from keras.metrics import RootMeanSquaredError as rmse
from keras.activations import relu
from keras.optimizers import Adam
from tensorflow.python.keras.engine.training import Model


'''
This file created to show how to use merge layers. (like multiplication layer all of them used with samemethod)
We will multiply 2 numbers and then we are going to use 2 different models to predict result of the multiplication.
First model is gonna use Multiply layer and second is going to consist from dense layers.
Since we have multiplied two numbers we used Multiply layer.
You can use other merge layers like Add or Subtract to use in your own projects.

We will discover success of two methods will be different.
Because it is is much more usefull to use Multiply layer when multiply numbers (no surprise).

We also used multiple input layers at the model which contains multiply layer.
'''
def create_multiplication_file(filename, start, stop):
    with open(filename, "w") as f:
        f.writelines("first,second,result\n")
        for i in range(-start, stop+1):
            for j in range(start, stop+1):
                f.writelines(str(i)+ "," + str(j) + "," + str(i*j) + "\n")


create_multiplication_file(filename="f.csv", start=10, stop=100)
d = pd.read_csv("f.csv", index_col=None)
x = d.iloc[:,:2]
y = d.iloc[:,2]

X_train, X_test, y_train, y_test = train_test_split(x,y, test_size=0.2, shuffle=True)
print(X_train)
xt1 = X_train["first"]
xt2 = X_train["second"]


inp1 = Input((1,))
inp2 = Input((1,))
m = Multiply()([inp1, inp2])
d1 = Dense(32, activation=relu)(m)
d2 = Dense(32, activation=relu)(d1)
out = Dense(1)(d2)
model = Model([inp1, inp2], out)


model2 = Sequential([
    Dense(32, activation="relu"),
    Dense(32, activation="relu"),
    Dense(1)
])

es1 = EarlyStopping(monitor='val_rmse', mode='min', verbose=1, patience=2)
es2 = EarlyStopping(monitor='val_rmse', mode='min', verbose=1, patience=2)


epochs = 500

model.compile(optimizer=Adam(), loss="mse", metrics=[rmse(name="rmse")])
history = model.fit(x=[xt1, xt2], y=y_train, epochs=epochs, validation_data=([X_test["first"],X_test["second"]], y_test), callbacks=[es1])

model2.compile(optimizer=Adam(), loss="mse", metrics=[rmse(name="rmse")])
history2 = model2.fit(x=X_train, y=y_train, epochs=epochs, validation_data=(X_test, y_test), callbacks=[es2])

y_preds = model.predict([X_test["first"],X_test["second"]])
y_preds2 = model2.predict(X_test)


sns.set_style("darkgrid")
#MODEL1 RESULTS
plt.subplot(221)
sns.lineplot(range(0, es1.stopped_epoch+1) if es1.stopped_epoch != 0 else range(0, epochs), 
             history.history["rmse"],
             label="train rmse 1")
sns.lineplot(range(0, es1.stopped_epoch+1) if es1.stopped_epoch != 0 else range(0,epochs), 
             history.history["val_rmse"], 
             label="val rmse 1")
plt.title("Errors")
plt.legend()
plt.subplot(222)
sns.lineplot(range(0, y_test.shape[0]), y_test,
             label="test actual 1")
sns.lineplot(range(0, y_test.shape[0]), y_preds[:,0],
             label="test preds 1")
plt.legend()
plt.title("Predictions")


#MODEL2 RESULTS
plt.subplot(223)
sns.lineplot(range(0, es2.stopped_epoch+1) if es2.stopped_epoch != 0 else range(0, epochs), 
             history2.history["rmse"],
             label="train rmse 2")
sns.lineplot(range(0, es2.stopped_epoch+1) if es2.stopped_epoch != 0 else range(0,epochs), 
             history2.history["val_rmse"], 
             label="val rmse 2")
plt.legend()
plt.subplot(224)
sns.lineplot(range(0, y_test.shape[0]), y_test,
             label="test actual 2")
sns.lineplot(range(0, y_test.shape[0]), y_preds2[:,0],
             label="test preds 2")
plt.legend()

#SHOW PLOT
plt.suptitle(f"RESULTS\nRMSE when Multiplication layer used: {history.history['val_rmse'][-1]}\nRMSE when Multiplication layer not used: {history2.history['val_rmse'][-1]}")
plt.show()

results = pd.DataFrame([y_preds[:,0], y_preds2, y_test, X_test.iloc[:,0], X_test.iloc[:,1]]).T
results.columns = ["Model with Multiplication", "Model without Multiplication", "Actual Result", "First Value", "Second Value"]
results["Model without Multiplication"] = results["Model without Multiplication"].astype(float)
print(results)
