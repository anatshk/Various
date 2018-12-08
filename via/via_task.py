"""
Column Description -
Attached is the data from a 2 week period in NY. Each row includes the following fields:
1. Request Id -  a unique identifier per request
2. ETA a - An estimated ETA calculated by the system (timestamp)
3. ETA b - A second estimated ETA calculated by the system with a different method (timestamp)
4. Load - the number of riders currently on board the van
5. Pickup bearing - The direction (heading) in degrees of the pickup
6. Pickup id - A unique identifier of the pickup location
7. Pickup latitude
8. Pickup longitude
9. Pickup ts - the actual timestamp of the pickup
10. Request type - A string that describes the type of the request as analyzed by the system.
11. Ride type - A string that describes the ride type - i.e. shared, private, express etc.
12. Timestamp - of the request
13. Van capacity -  maximal van capacity
14. Van id - unique van id
15. Van latitude - Van latitude at the moment of the request
16. Van longitude -Van longitude at the moment of the request

Guidelines :
> The analysis is intended to require 3-6 hours (so scale your efforts accordingly).
> Attach your code in a verbose readable and reproducible version - assessment will take your
methodology and approach into account as well as the final result.
> Training the model will require no more than 10 minutes.
> We have withheld 20% of the data for testing and it will be used to assess your model.
> Using additional resources for this assignment is encouraged, but please specify them in your
assignment. Feel free to contact amir.livne.bar.on@ridewithvia.com or
elad.berkman@ridewithvia.com if you have any questions.
"""

import numpy as np
import pandas as pd
import sklearn.model_selection
import sklearn.metrics

from datetime import datetime
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor

pth = r'C:\Users\Anat\Downloads\via\Data_science_assignment_train (3).csv'

df = pd.read_csv(pth)
df.rename(columns={u'Unnamed: 0': u'request_id'}, inplace=True)

# remove nan from target column and estimated eta columns
# (not mandatory to remove nan from estimated eta for modelling - only to keep consistency)
df.dropna(subset=['pickup_ts', 'external_eta', 'internal_eta'], inplace=True)

# NOTE: I've noticed rows where van_capacity < load.
# after a clarification email from Elad, both rows where capacity < load and rows where capacity - load = 0 remain in
# the dataset.


def calc_metric(y_true, y_pred):
    return np.sqrt(sklearn.metrics.mean_squared_error(y_true, y_pred))

########################################################################################################################
# Part A
# 1. Using the data provided, perform an exploratory analysis, focused on the relations between the
# Actual ETA and the the estimated ETAs calculated by each method. Provide the required graphs
# as you see fit.
########################################################################################################################

SHOW_PLOTS = False

# extract relevant columns
actual_eta = df.pickup_ts
internal_estimated_eta = df.internal_eta
external_estimated_eta = df.external_eta

# diff histogram calculations
internal_diff_seconds = actual_eta - internal_estimated_eta
external_diff_seconds = actual_eta - external_estimated_eta

# calculate RMSE
internal_rmse = calc_metric(df.pickup_ts, df.internal_eta)
external_rmse = calc_metric(df.pickup_ts, df.external_eta)

if SHOW_PLOTS:
    # initial plot
    plt.figure()
    plt.scatter(actual_eta, internal_estimated_eta, c='b', marker='x')
    plt.scatter(actual_eta, external_estimated_eta, c='k', marker='.')
    plt.xlabel('actual eta [timestamp]')
    plt.ylabel('estimated etas [timestamp]')
    plt.title('actual vs. estimated eta')
    plt.legend(['internal', 'external'])
    plt.show()

    # histograms of diffs
    bins = np.arange(-1e3, 1.1e3, 1e2)
    in_heights, in_bins = np.histogram(internal_diff_seconds, bins=bins)
    ex_heights, ex_bins = np.histogram(external_diff_seconds, bins=in_bins)
    width = (in_bins[1] - in_bins[0]) / 3

    plt.figure()
    plt.bar(in_bins[:-1], in_heights / in_heights.sum(), width=width, color='blue')
    plt.bar(in_bins[:-1] + width, ex_heights / ex_heights.sum(), width=width, color='red')
    plt.xlabel('Diff: Actual ETA - Estimated ETA [sec]')
    plt.ylabel('%')
    plt.title('Histogram of Difference between\nActual and Estimated ETAs')
    plt.legend(['Internal (RMSE={} [sec])'.format(round(internal_rmse, 3)),
                'External (RMSE={} [sec])'.format(round(external_rmse, 3))])
    plt.show()

########################################################################################################################
# Part B
# 1. Using the data in the first file build a simple model that will allow us to give an improved prediction
# for the time of pickup. Specify any input features you used.
# 2. What measure would you use for assessing your model? Explain your choice?
# 3. Based on the model results - Which features have the largest impact on the model? Can you
# explain why?
# 4. Given more time, what future analysis and modelling would you recommend (do not implement
# these)
########################################################################################################################

HYPER_PARAMETER_OPTIMIZATION = False

# select relevant features that may affect pickup time - in the future - engineer features
df_ordinal_features = df[['load', 'ts', 'van_capacity']]

# encode categorical features to one-hot vectors
df_categorical_features = pd.get_dummies(df[['ride_type', 'request_type']])
# In the future: engineer features from locations of request and van
df_location_features = df[['pickup_bearing', 'pickup_lat', 'pickup_lng', 'van_lat', 'van_lng']]

features = pd.concat([df_ordinal_features, df_location_features, df_categorical_features], axis=1)
labels = df.pickup_ts

# divide into train \ test
train, test, train_labels, test_labels = sklearn.model_selection.train_test_split(features, labels, test_size=0.2)

# run cross validation on train set to select hyper-parameters
kf = sklearn.model_selection.KFold(n_splits=5, shuffle=True)
splits = list(kf.split(train, train_labels))
n_splits = kf.get_n_splits(train)

# parameter sets
param_grid = sklearn.model_selection.ParameterGrid({
    # 'n_estimators': np.concatenate([np.array([1]), np.arange(5, 20, 5)]),
    # 'min_samples_split': [2, 5, 10, 15],
    # 'min_impurity_split': [1e-7, 1e-5, 1e-3, 1e-1],  # deprecated in later versions for min_impurity_decrease
    # 'max_features': ['auto', 'sqrt']
    'n_estimators': np.arange(20, 60, 5),
    'min_samples_split': [10, 15, 20, 25],
    'min_impurity_split': [1e-6, 1e-5, 1e-4, 1e-3, 1e-2],
    'max_features': ['auto']
})

if HYPER_PARAMETER_OPTIMIZATION:
    param_performance_dict = {}
    cv_now = datetime.now()
    for ix, param_set in enumerate(param_grid):
        print('Starting - Param Set {} out of {}'.format(ix, len(param_grid)))
        now = datetime.now()
        model = RandomForestRegressor(n_jobs=-1, **param_set)
        cv_results = []
        # train and test model in cross validation
        for ix_fold, (cv_train_ix, cv_test_ix) in enumerate(splits):
            print('Starting - Fold {} out of {}'.format(ix_fold, n_splits))
            now_fold = datetime.now()
            cv_train, cv_train_labels = train.iloc[cv_train_ix], train_labels.iloc[cv_train_ix]
            cv_test, cv_test_labels = train.iloc[cv_test_ix], train_labels.iloc[cv_test_ix]
            model.fit(cv_train, cv_train_labels)
            predictions = model.predict(cv_test)
            # calculate RMSE per fold
            rmse = calc_metric(cv_test_labels, predictions)
            cv_results.append(rmse)
            print('Finished - Fold {0} out of {1}, RMSE={3}, took {2}'.format(ix_fold, n_splits,
                                                                              datetime.now() - now_fold, rmse))
        # calculate mean RMSE for all folds and save with param set
        final_rmse = np.nanmean(cv_results)
        param_performance_dict[final_rmse] = param_set
        print('Finished - Param Set {0} out of {1}, RMSE={3}, took {2}'.format(ix, len(param_grid),
                                                                               datetime.now() - now, final_rmse))
    print('Finished CV, took {}'.format(datetime.now() - cv_now))

    # select optimal hyper-parameters
    best = min(param_performance_dict.keys())
    print('Best param set {} has RMSE = {}'.format(param_performance_dict[best], best))
    best_param_set = param_performance_dict[best]
else:
    # RMSE = 239.27158225904262
    best_param_set = {'max_features': 'auto', 'min_impurity_split': 0.001, 'min_samples_split': 20, 'n_estimators': 55}

# train final model with selected hyper-parameters
final_model = RandomForestRegressor(n_jobs=-1, **best_param_set)

now = datetime.now()
final_model.fit(train, train_labels)
print('Final Model Training took ~{}'.format((datetime.now() - now)))

predictions = final_model.predict(test)
metric = calc_metric(test_labels, predictions)
print('Final Model performance: RMSE of predicted time = {}'.format(metric))
print('Internal RMSE={}, External RMSE={}'.format(internal_rmse, external_rmse))

# find feature importance
feature_names = np.array(features.columns.tolist())
feature_importance = final_model.feature_importances_
sorted_by_importance = feature_names[feature_importance.argsort()][::-1]  # flip as argsort sorts in ascending order
print('The features in decreasing order of importance - {}'.format(sorted_by_importance))
table = list(zip(feature_names[feature_importance.argsort()], feature_importance[feature_importance.argsort()]))
