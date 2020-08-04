'''
    CluesML
    Machine Learning tools for the CLUES project

    (C) Edoardo Carlesi 2020
    https://github.com/EdoardoCarlesi/CluesML
'''

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

import read_files as rf
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import tools as t

sns.set_style('whitegrid')

data = rf.read_lg_fullbox_vweb(grids = [32, 64, 128])

print(data.info())

data['Mtot'] = data['M_M31'] + data['M_MW']
data['Mratio'] = data['M_M31'] / data['M_MW']

'''
data.drop(['sub_code', 'simu_code', 'Nsub_M31', 'Nsub_MW', 'Xc_LG', 'Yc_LG', 'Zc_LG'], axis=1, inplace=True)
data.drop(['cNFW_MW', 'c_NFW_M31', 'Vmax_MW', 'Vmax_M31'], axis=1, inplace=True)
data.drop(['Npart_MW', 'Npart_M31'], axis=1, inplace=True)
data.drop(['lambda_MW', 'lambda_M31'], axis=1, inplace=True)
print(data.info())
print(data.head())
'''

#grid = 128
grid = 32
#grid = 64
l1 = 'l1_' + str(grid); l2 = 'l2_' + str(grid); l3 = 'l3_' + str(grid)
dens = 'dens_' + str(grid)

n_estimators = 1000
max_depth = 3
min_samples_split = 10

#train_cols = ['R','Vrad', 'Mtot']; test_col = 'Mratio'; train_type = 'mass_ratio_lambda'
#train_cols = ['R','Vrad', 'Mtot']; test_col = 'Mratio'; train_type = 'mass_ratio'
train_cols = ['R','Vrad', 'Vtan', l1, l2, l3, dens]; test_col = 'Mtot'; train_type = 'mass_total_lambda' + str(grid)
#train_cols = ['R','Vrad', 'Vtan', dens]; test_col = 'Mtot'; train_type = 'mass_total'
#train_cols = ['R','Vrad', dens]; test_col = 'Mtot'; train_type = 'mass_total'
#train_cols = ['R','Vrad', 'Vtan', dens]; test_col = 'Mtot'; train_type = 'mass_total'
#train_cols = ['R','Vrad', 'Vtan']; test_col = 'Mtot'; train_type = 'mass_total'
#train_cols = ['Mtot','R', 'Vtan']; test_col = 'Vrad'; train_type = 'vel_rad'
#train_cols = ['R','Vrad', 'Vtan']; test_col = 'M_M31'; train_type = 'mass_m31'
#train_cols = ['R','Vrad', 'Vtan']; test_col = 'M_M31'; train_type = 'mass_mw'

#regressor = LinearRegression(); reg_name = 'linear_reg' + '_' + train_type
#regressor = RandomForestRegressor(n_estimators = n_estimators); reg_name = 'randomforest_reg' + '_' + train_type
regressor = GradientBoostingRegressor(n_estimators = n_estimators, max_depth = max_depth, min_samples_split = min_samples_split); reg_name = 'gradientboost_reg' + '_' + train_type

X = data[train_cols]
y = data[test_col]

print('Total size: ', X.count())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 40)

print('Train size: ', len(X_train))
print('Test size: ', len(X_test))

#scaler = MinMaxScaler()
scaler = StandardScaler()

# This only optimizes the parameters to perform the scaling later on
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

regressor.fit(X_train, y_train)
predictions = regressor.predict(X_test)

print(y_test.shape)

mae = metrics.mean_absolute_error(y_test, predictions)
msq = metrics.mean_squared_error(y_test, predictions)
mape = t.MAPE(y_test, predictions)


if train_type == 'mass_total' or train_type == 'mass_total_lambda' + str(grid): 
    print('MAE: ', mae/1.0e+12, ' MSQ: ', np.sqrt(msq)/1.0e+12, ' MAPE: ', np.mean(mape) )
    cols = ['M_tot_true', 'M_tot_pred']
    data = pd.DataFrame() 
    data[cols[0]] = np.log10(y_test)
    data[cols[1]] = np.log10(predictions)
    sns.lmplot(x=cols[0], y=cols[1], data=data)

    slope = np.polyfit(np.log10(y_test), np.log10(predictions), 1)
    print('Slope: ', slope)

elif train_type == 'mass_m31':
    print('MAE: ', mae/1.0e+12, ' MSQ: ', np.sqrt(msq)/1.0e+12, ' MAPE: ', np.mean(mape) )
    ax = sns.scatterplot(x=np.log10(y_test), y=np.log10(predictions))
    cols = ['M_M31_true', 'M_M31_pred']
    data = pd.DataFrame() 
    data[cols[0]] = np.log10(y_test)
    data[cols[1]] = np.log10(predictions)
    sns.lmplot(x=cols[0], y=cols[1], data=data)

    slope = np.polyfit(np.log10(y_test), np.log10(predictions), 1)
    print('Slope: ', slope)

elif train_type == 'mass_mw':
    print('MAE: ', mae/1.0e+12, ' MSQ: ', np.sqrt(msq)/1.0e+12, ' MAPE: ', np.mean(mape) )
    cols = ['M_MW_true', 'M_MW_pred']
    data = pd.DataFrame() 
    data[cols[0]] = np.log10(y_test)
    data[cols[1]] = np.log10(predictions)
    sns.lmplot(x=cols[0], y=cols[1], data=data)

    slope = np.polyfit(np.log10(y_test), np.log10(predictions), 1)
    print('Slope: ', slope)

elif train_type == 'mass_ratio':
    print('MAE: ', mae, ' MSQ: ', np.sqrt(msq), ' MAPE: ', np.mean(mape) )
    cols = ['M_ratio_true', 'M_ratio_pred']
    ax = sns.scatterplot(y_test, predictions)
    ax.set(xlabel='M_ratio (true)', ylabel='M_ratio (pred)')

elif train_type == 'vel_rad':
    print('MAE: ', mae/100.0, ' MSQ: ', np.sqrt(msq)/100.0, ' MAPE: ', np.mean(mape) )
    ax = sns.scatterplot(y_test, predictions)

    slope = np.polyfit(y_test, predictions, 1)
    print('Slope: ', slope)
    ax.set(xlabel='V_rad (true)', ylabel='V_rad (pred)')


if reg_name == 'randomforest_reg' + '_' + train_type:
    importances = regressor.feature_importances_
    print(X.columns)
    print(importances)

#plt.scatterplot(y_test, predictions)
plt.tight_layout()
print('savefig to output/' + reg_name + '.png')
plt.savefig('output/' + reg_name + '.png')


'''
print(classification_report(y_test, pred))
print(confusion_matrix(y_test, pred))

print('RANDOM FOREST')

rforest = RandomForestClassifier(n_estimators = 200)
rforest.fit(X_train, y_train)
pred2 = rforest.predict(X_test)

print(classification_report(y_test, pred2))
print(confusion_matrix(y_test, pred2))

scaler.fit(train.drop('TARGET CLASS', axis = 1))
scaled_feat = scaler.transform(train.drop('TARGET CLASS', axis = 1))
data_scaled = pd.DataFrame(scaled_feat, columns = train.columns[:-1])

print(scaled_feat)

print(data_scaled.head())

pred = knn.predict(X_test)
pred2 = logmod.predict(X_test)
print(classification_report(y_test, pred))
plt.show()
'''
