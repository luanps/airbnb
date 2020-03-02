# -*- coding: utf-8 -*-
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import LassoCV
import numpy as np
import pandas as pd
import pdb
from src.utils import load_dataset
from src.utils import load_serialized
from src.utils import save_serialized
from src.exploratory import ExploratoryAnalysis
from src.preproc import Preproc
from src.model import Model

pd.set_option('display.max_rows', 1000)


def data_exploration(data):
    exploratory = ExploratoryAnalysis(data)
    
    data_length = exploratory.data_length()
    print("="*79)
    print(f"""This dataset contains {data_length[0]}
        samples with {data_length[1]} attributes.\n""")
    print("="*79)

    attributes = exploratory.list_attributes()
    print(f"""These attributes are:\n {attributes}""")
    print("="*79)
    
    description = exploratory.data_description()
    print(f"""Per attribute description :""")
    [print(f"""{value}\n""") for key, value in description.items()]
    print("="*79)

    null_data = exploratory.check_null()
    print(f"""Attributes with null data:\n {null_data}""")
    print("="*79)

    majority_null = exploratory.majority_nulls(0.66)
    print(f"""Attributes which more than 66% of data is null""")
    [print(key, value) for key, value in majority_null.items()]
    print("="*79)

    empty_spaces = exploratory.check_empty_spaces()
    print(f"""Textual attributes with empty data (value=' '):\n{empty_spaces}""")
    print("="*79)
    
    zeros = exploratory.check_zeros()
    print(f"""Numerical attributes with zeros:""")
    [print(key, value) for key, value in zeros.items()]
    print("="*79)

    unique_values = exploratory.check_unique_values(10)
    print(f"""Sample of each attribute:""")
    [print(key, value) for key, value in unique_values.items()]
    print("="*79)

    singlelabel = exploratory.check_singlelabel()
    print(f"""Attributes with only one label:""")
    [print(key, value) for key, value in singlelabel.items()]
    print("="*79)
   
    return majority_null, singlelabel


def preproc_routines():

    print("="*79)
    print("============= Reading data from file  =============")
    filepath = 'data/listings_full.csv'
    data = load_dataset(filepath)
    print("="*79)

    unnecessary_columns = 'unnecessary_attributes.csv'
    unnecessary_columns = load_dataset(unnecessary_columns)
    unnecessary_columns = unnecessary_columns['attributes'].values.tolist()

    print("============= Data exploration  =============")
    majority_null, singlelabel = data_exploration(data)
    print("="*79)

    print("============= Applying Preprocessing step =============")
    empty_columns = [key for key, value in {**majority_null,
                                              **singlelabel}.items()]
    print("="*79)

    columns_to_drop = unnecessary_columns + empty_columns

    country = 'Brazil'
    obj_to_float = ['price', 'security_deposit', 'cleaning_fee',
    'extra_people', 'host_response_rate']
    print(f"""Data that will be transformed into float:\n{obj_to_float}""")
    print("="*79)

    num_to_categories = ['host_response_rate', 'review_scores_rating', 
        'review_scores_accuracy', 'review_scores_cleanliness',
        'review_scores_checkin', 'review_scores_communication',
        'review_scores_location', 'review_scores_value', 'reviews_per_month']
    print(f"""Numerical data that will be transformed into categories 
        [No Data, Low, Medium, High, Excellent]
        based on their own quantiles: \n{num_to_categories}""")
    print("="*79)

    text_to_counter = ['amenities', 'name', 'summary', 'space', 'description', 'access', 
    'neighborhood_overview', 'interaction', 'house_rules']
    print(f"""Textual data that will be transformed into an integer
          by counting its words:\n{text_to_counter}""")
    print("="*79)

    preproc = Preproc(data, columns_to_drop, country , obj_to_float,
        num_to_categories, text_to_counter)
    preproc.apply_general_preproc()

    print("============= Plotting data  =============")
    prefix = 'before_outlier_removal'
    ExploratoryAnalysis.plot_data(preproc.data, prefix)
    print("="*79)

    print("============= Removing outliers  =============")
    outlier_threshold = 3
    outliers_to_analize = ['price', 'accommodates', 'bathrooms', 'bedrooms',
    'beds', 'calculated_host_listings_count', 'cleaning_fee', 'extra_people',
    'guests_included', 'minimum_nights', 'security_deposit'] 
    print(f"""Numerical data which their outliers will be removed 
        (computed by z-score): \n{outliers_to_analize}""")
    preproc.drop_outliers(outliers_to_analize, outlier_threshold)
    print("="*79)

    print("========= Transforming target variable 'price' into log ========")
    preproc.log_price()
    print("="*79)

    print("============= Plotting data  =============")
    prefix = 'after_outlier_removal'
    ExploratoryAnalysis.plot_data(preproc.data, prefix)
    print("="*79)

    print("============= Data exploration after preprocessing  =============")
    data_exploration(preproc.data)
    print("="*79)

    return preproc.data


def run_linear_model(generic_model, model_name,  model_configs):

    X_train, X_test, y_train, y_test = model_configs['splitted_data']
    y_train = y_train.to_numpy().ravel()
    y_test = y_test.to_numpy().ravel()

    if model_name == 'Ridge':
        model = generic_model(alphas = model_configs['initial_alphas'],
                              cv = model_configs['cross_val'])

    elif model_name == 'Lasso':
        model = generic_model(alphas = model_configs['initial_alphas'] * 0.001,
                              cv = model_configs['cross_val'],
                              max_iter = model_configs['max_iter'])

    model = Model(model, model_name, cross_val = model_configs['cross_val'])
    model.fit(X_train, y_train)
    alpha = model.model.alpha_
    print(f'Best initial alpha: {alpha}')

    refined_alphas = model_configs['update_alphas'] * alpha
    model = generic_model(alphas = refined_alphas)
    model = Model(model, model_name, cross_val = model_configs['cross_val'])
    model.fit(X_train, y_train)
    alpha = model.model.alpha_
    print(f'Best refined alpha: {alpha}')

    rmse_train = model.fit_cross_val(X_train, y_train)
    rmse_test = model.predict_cross_val(X_test, y_test)
    print(f'RMSE on training data: {rmse_train}')
    print(f'RMSE on validation data: {rmse_test}')

    model.plot_coefficients(X_test)

    filepath = f'models/{model_name}' 
    save_serialized(filepath, model)


if __name__ == '__main__':

    preproc_filepath = 'data/preprocessed_data'
    try:
        data = load_serialized(preproc_filepath)
    except:
        data = preproc_routines()
        save_serialized(preproc_filepath, data)


    #X_train, X_test, y_train, y_test = 
    general_configs = {
        'splitted_data' : Model.encode_split_data(data),
        'cross_val' : 2,
        'max_iter' : 50000,
        'initial_alphas' : np.array([0.01, 0.03, 0.06, 0.1, 0.3, 0.6, 1, 3, 6,
                                     10, 30, 60]),
        'update_alphas' : np.array([.6, .65, .7, .75, .8, .85, .9, .95, 1.05, 
                                    1.1, 1.15, 1.25, 1.3, 1.35, 1.4])
    }

    print("=============  Running Ridge Regression  =============")
    model = RidgeCV
    model_name = 'Ridge'
    run_linear_model(model, model_name, general_configs)


    print("=============  Running Lasso Regression  =============")
    model = LassoCV
    model_name = 'Lasso'
    run_linear_model(model, model_name, general_configs)
