"""
Github: xichuanhit
https://github.com/xichuanhit/PerCode/edit/main/01-Electricity-Pre/BP-2.py

environment: python=3.9.7, tensorflow=2.7
"""

import OpenSSL.crypto
import pandas as pd
import numpy as np
from sklearn import metrics
import tensorflow as tf
import os

df=pd.read_excel("data211010.xlsx")
df_test=df[df["month"]>="2021/1/1"].shape[0]
df["Y"] = df["month"].dt.year
df["M"] = df["month"].dt.month
del df["month"]
arr = ["ele", "v1", "v2", "v3", "Y", "M", "tem", "GDP"]
df = df[arr]
df=df.fillna(method="pad") 

for i in df.columns:
    df[i]=(df[i]-df[i].mean())/df[i].std()

tmp=df.values 

traindata=[]
label=[]
for i in range(3, tmp.shape[0]):
    traindata.append(tmp[i-3:i,:])
    label.append(tmp[i,0])

train_data=np.array(traindata)
label=np.array(label)
X_train=train_data[:-df_test]
y_train=label[:-df_test]
X_test=train_data[-df_test:]
y_test=label[-df_test:]
X_train=X_train.reshape(X_train.shape[0], X_train.shape[1]*X_train.shape[2])
X_test=X_test.reshape(X_test.shape[0], X_test.shape[1]*X_test.shape[2])

callbacks = [tf.keras.callbacks.EarlyStopping(monitor='val_loss', verbose=1, patience=1000),
             tf.keras.callbacks.ModelCheckpoint("model_bp_02.hdf5", monitor='val_loss',
                             mode='min', verbose=0, save_best_only=True)]
                             
inputs = tf.keras.layers.Input(shape=(X_train.shape[1], ))
input2 = tf.keras.layers.Dense(256, activation="relu")(inputs)
input2 = tf.keras.layers.Dense(256, activation="relu")(input2)
input2 = tf.keras.layers.Dense(256, activation="relu")(input2)
output = tf.keras.layers.Dense(1, activation=None)(input2)
model = tf.keras.models.Model(inputs=[inputs], outputs=output)

model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(lr=0.0002), metrics =["mse"])
model.summary()
history = model.fit(X_train, y_train, epochs=300, batch_size=16, callbacks=callbacks, validation_data=(X_test, y_test), verbose=1)

model_new = tf.keras.models.load_model("model_bp_02.hdf5") 
pred_train = model_new.predict(X_train)
pred_train = np.squeeze(pred_train)
pred_test = model_new.predict(X_test)
pred_test= np.squeeze(pred_test)

pred_train=pd.DataFrame(pred_train)
pred_test=pd.DataFrame(pred_test)
y_train=pd.DataFrame(y_train)

pred_train.to_csv("BP_2_train.csv",index=False)
pred_test.to_csv("BP_2_test.csv",index=False)
y_train.to_csv("BP_2_ytrain.csv",index=False)
