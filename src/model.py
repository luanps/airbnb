# -*- coding: utf-8 -*-

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error
from sklearn.metrics import make_scorer
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
import pdb

class Model:

    def __init__(self, model, model_name, cross_val):
        self.model = model
        self.model_name = model_name
        self.cross_val = cross_val
        self.scorer = make_scorer(mean_squared_error, greater_is_better = False) 


    def fit(self, X_train, y_train):
        self.model.fit(X_train, y_train)


    def predict(self, X_test, y_test):
        self.model.predict(X_test, y_test)

        
    def fit_cross_val(self, X_train, y_train):
        cv_score = cross_val_score(self.model, X_train, y_train,
                                   scoring = self.scorer, cv = self.cross_val)
        rmse_train = np.sqrt(-cv_score).mean()
        return rmse_train


    def predict_cross_val(self, X_test, y_test):
        cv_score = cross_val_score(self.model, X_test, y_test, 
                                   scoring = self.scorer, cv = self.cross_val)
        rmse_pred = np.sqrt(-cv_score).mean()
        return rmse_pred


    def fit_linear_model(self, X_train, y_train):
        self.fit(X_train, y_train)

        alpha = self.model.alpha_
        print(f'Best alpha: {alpha}')

        if self.model_name == 'ElasticNet':
            l1_ratio = self.model.l1_ratio_
            print(f'Best l1_ratio: {l1_ratio}')
        else:
            l1_ratio = 0

        return alpha, l1_ratio

    def plot_feature_importances(self, X_test):
        feat = pd.Series(self.model.feature_importances_, index = X_test.columns)
        '''keep_coefs = sum(coefs != 0)
        discarted_coefs = sum(coefs == 0)
        print(f"""The model {self.model_name} picked {keep_coefs} features 
                  and eliminated {discarted_coefs} features""")'''

        plt.figure(figsize=(8,6))
        importances = feat.sort_values(ascending = False).head(20)
        importances.plot(kind = 'barh')

        plt.title(f'{self.model_name} feature importances')
        plt.savefig(f'plots/coefficients/{self.model_name}.png', 
                    bbox_inches = "tight")
        plt.close()


    def plot_coefficients(self, X_test):
        coefs = pd.Series(self.model.coef_, index = X_test.columns)
        keep_coefs = sum(coefs != 0)
        discarted_coefs = sum(coefs == 0)
        print(f"""The model {self.model_name} picked {keep_coefs} features 
                  and eliminated {discarted_coefs} features""")

        plt.figure(figsize=(8,6))
        imp_coefs = pd.concat([coefs.sort_values().head(10),
                               coefs.sort_values().tail(10)])

        imp_coefs.plot(kind = 'barh')
        plt.title(f'{self.model_name} coefficients')
        plt.savefig(f'plots/coefficients/{self.model_name}.png', 
                    bbox_inches = "tight")
        plt.close()


    @staticmethod
    def encode_data(X):
        numerical_data = X.select_dtypes(exclude=['object'])
        numerical_labels = numerical_data.keys().tolist()

        categorical_data = X.select_dtypes(include=['object'])
        categorical_labels = categorical_data.keys().tolist()

        standard_X = StandardScaler()
        standard_X.fit(numerical_data)
        standard_encoded = standard_X.transform(numerical_data)

        onehot_X = OneHotEncoder()
        onehot_X.fit(categorical_data)
        onehot_encoded = onehot_X.transform(categorical_data).toarray()
        onehot_labels = onehot_X.get_feature_names(categorical_labels)

        standard_df = pd.DataFrame(standard_encoded, columns = numerical_labels)
        onehot_df = pd.DataFrame(onehot_encoded, columns = onehot_labels)
        X = pd.concat([standard_df, onehot_df],axis=1)

        return X


    @staticmethod
    def encode_split_data(data):
        X = data.drop(['logPrice', 'price'], axis=1)
        X = Model.encode_data(X)
        y = data[['logPrice']]

        return train_test_split(X, y, test_size = 0.3, random_state = 42)

