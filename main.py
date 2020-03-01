# -*- coding: utf-8 -*-
from sklearn.linear_model import LogisticRegression
import pandas as pd
import pdb
from src.utils import load_dataset
from src.exploratory import ExploratoryAnalysis
from src.preproc import Preproc
from src.model import Model
pd.set_option('display.max_rows', 1000)

# TODO: group some numerical attributes into range of categories
# TODO: encode strings

def data_exploration(data):
    exploratory = ExploratoryAnalysis(data)
    
    data_length = exploratory.data_length()
    print("="*79)
    print(f"""This dataset contains {data_length[0]}
        samples with {data_length[1]} attributes.\n""")

    attributes = exploratory.list_attributes()
    print("="*79)
    print(f"""These attributes are:\n {attributes}""")
    
    description = exploratory.data_description()
    print("="*79)
    print(f"""Per attribute description :""")
    [print(f"""{value}\n""") for key, value in description.items()]

    null_data = exploratory.check_null()
    print("="*79)
    print(f"""Attributes with null data:\n {null_data}""")

    majority_null = exploratory.majority_nulls(0.66)
    print("="*79)
    print(f"""Attributes which more than 66% of data is null""")
    [print(key, value) for key, value in majority_null.items()]

    empty_spaces = exploratory.check_empty_spaces()
    print("="*79)
    print(f"""Textual attributes with empty data (value=' '):\n{empty_spaces}""")
    
    zeros = exploratory.check_zeros()
    print("="*79)
    print(f"""Numerical attributes with zeros:""")
    [print(key, value) for key, value in zeros.items()]

    unique_values = exploratory.check_unique_values(10)
    print("="*79)
    print(f"""Sample of each attribute:""")
    [print(key, value) for key, value in unique_values.items()]

    singlelabel = exploratory.check_singlelabel()
    print(f"""Attribute with only one label:""")
    [print(key, value) for key, value in singlelabel.items()]
   
    return majority_null, singlelabel


if __name__ == '__main__':
    print("============= Reading data from file  =============")
    filepath = 'data/listings_full.csv'
    data = load_dataset(filepath)

    unnecessary_columns = 'unnecessary_attributes.csv'
    unnecessary_columns = load_dataset(unnecessary_columns)
    unnecessary_columns = unnecessary_columns['attributes'].values.tolist()

    print("============= Data exploration  =============")
    majority_null, singlelabel = data_exploration(data)

    print("============= Applying Preprocessing step =============")
    empty_columns = [key for key, value in {**majority_null,
                                              **singlelabel}.items()]

    columns_to_drop = unnecessary_columns + empty_columns

    country = 'Brazil'
    obj_to_float = ['price', 'security_deposit', 'cleaning_fee',
    'extra_people', 'host_response_rate']
    num_to_categories = ['review_scores_rating', 'review_scores_accuracy',
    'review_scores_cleanliness', 'review_scores_checkin',
    'review_scores_communication', 'review_scores_location',
    'review_scores_value', 'reviews_per_month']

    preproc = Preproc(data, columns_to_drop, country , obj_to_float,
        num_to_categories)

    treated_data = preproc.apply_preproc()
    preproc.encode_numerical_to_categories()

    print("============= Plotting data  =============")
    prefix = 'before_outlier_removal'
    ExploratoryAnalysis.plot_data(treated_data, prefix)

    print("============= Removing outliers  =============")
    outlier_threshold = 3
    outliers_to_analize = ['price', 'accommodates', 'bathrooms', 'bedrooms',
    'beds', 'calculated_host_listings_count', 'cleaning_fee', 'extra_people',
    'guests_included', 'minimum_nights', 'security_deposit'] 
    cleaned_data = preproc.drop_outliers(outliers_to_analize, outlier_threshold)

    print("============= Plotting data  =============")
    prefix = 'after_outlier_removal'
    #ExploratoryAnalysis.plot_data(cleaned_data, prefix)

    print("============= Data exploration after preprocessing  =============")
    #data_exploration(cleaned_data)


    '''print("============= Encoding data  =============")
    encoded_data = preproc.encode_data(treated_data)

    print("=============  Running Logistic Regression  =============")
    lr_model = LogisticRegression()
    model_name = 'logistic_regression'
    model = Model(lr_model,model_name)
    model.run_model(encoded_data)'''
