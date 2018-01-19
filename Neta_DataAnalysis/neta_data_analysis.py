# -*- coding: utf-8 -*-
import pandas as pd

from datetime import datetime
from os import path
from utils import save_to_pkl, load_from_pkl

"""
For each row in Laproscopy DB (experiment.xlsx), find 2 rows in Control DB (contron.xlsx).

Assumptions:
1. using case_id_parity provides a unique index in both tables.

Control sample is suitable if:
1. Age at neonatal birth > age at lapro + 1 (surgery followed by birth or rounding down)
2. Same parity (1st, 2nd, 3rd etc birth).
3. Same number of fetuses (single, twins, triplets, etc.)
4. Similar neonatal birth date. For births between 2011-2016 we can find exact match, for earlier births, 
   find closest year and date within +/- 7 days. (20/10/2009 --> 13-27/10/2011).
   
Add Columns in Control:
1. Calculate maternal age during birth.
2. Number of fetuses per birth (duplicate row = more than one fetus).

Remove duplicates in Experiments: 
1. In experiment (Lapro) table - a single patient can undergo several procedures. 
   If all procedures are within scope of same pregnancy - treat them as single row and find matches from control once.

Data Validation:
1. Rows in experiment should be removed from control.
2. Rows in experiment without parity - should be removed.

Other:
* rows colored purple - manually created couplings. Can be used to test final flow. 
  Comparison should be contains and not exact. 
  In 'experiment' sheet in experiment.xlsx, there is a list of the selected rows.
"""

# load files
pkl_pth = 'temp.pkl'
if path.exists(pkl_pth):
    data = load_from_pkl(pkl_pth)
    control = data['control']
    experiment = data['experiment']
else:
    control = pd.read_excel('control.xlsx',
                            parse_dates=['maternal_birth_date', 'neonatal_birth_date']).dropna(how='all')
    experiment = pd.read_excel('experiment.xlsx', sheet_name='experiment', parse_dates=['BirthDate']).dropna(how='all')
    save_to_pkl(pkl_pth, control=control, experiment=experiment)


def create_new_index(df):
    """
    Removes rows without parity, and creates full name_id_parity index as 'new_index' column
    :param df:
    :return:
    """
    # remove rows without parity
    df.dropna(subset=['parity'], inplace=True)

    if 'full_name' not in df.columns:
        def create_full_name(row):
            return row.last_name + ' ' + row.first_name
        df['full_name'] = df.apply(create_full_name, axis=1)

    # create a new index of full name, id, parity
    def new_index(row):
        return row.full_name + '_' + row.id + '_' + str(int(row.parity))
    df['new_index'] = df.apply(new_index, axis=1)
    # df.set_index('new_index', drop=False, inplace=True)
    return df


def arrange_control(df, experiment_df):
    """
    Arranges the control file.
    :param df: Pandas frame
    :param experiment_df: Pandas frame
    :return: Pandas frame
    """
    # remove redundant rows
    if 'IRON NUM' in df.index:
        df = df.drop('IRON NUM')

    # create new index
    df = create_new_index(df)

    # new column - count number of fetuses (= duplicate rows) - find duplicates and count
    duplicated = df.loc[df.duplicated(keep=False)]
    counted_multi_fetuses = duplicated.groupby('new_index').count()['id']

    def num_fetuses(row):
        return counted_multi_fetuses[row.new_index] if row.new_index in counted_multi_fetuses else 1
    df['num_fetuses'] = df.apply(num_fetuses, axis=1)
    df.drop_duplicates(inplace=True)

    # convert dates, if needed
    a = 5

    # TODO: calculate maternal age at birth? if columns are not timestamps - convert

    # remove from control any rows that exist in experiment
    df = remove_overlap(df, experiment_df, 'new_index')

    return df


def arrange_experiment(df):
    """
    Arranges experiment data - dropping rows without parity, creating index from case_id_parity, removing duplicates.
    :param df: Pandas frame, experiment
    :return: Pandas frame
    """

    # re-arrange column names
    column_mapping = {
        u'שם מלא': 'full_name',
        u'מספר ת_ז': 'id',
        u'גיל ': 'age_at_procedure',
        u'BirthDate': 'neonatal_birth_date',
        u'P': 'parity',
        u'Is_twins?': 'num_fetuses',
        u'הוצא מהביקורת ': 'removed_from_control',
        u'ביקורת 1': 'control_1',
        u'ביקורת 2 ': 'control_2'
    }
    df.rename(column_mapping, axis='columns', inplace=True)

    # create new index and remove duplicates
    df = create_new_index(df)
    df.drop_duplicates(inplace=True)

    # increase number of fetuses (0 for 1 fetus)
    df['num_fetuses'] += 1

    return df


def remove_overlap(df1, df2, index_column):
    """
    Remove from df1 indices that appear in df2
    :param df1: Pandas dataframe
    :param df2: Pandas dataframe
    :param index_column: string
    :return: pandas dataframe
    """
    indices_to_keep = list(set(df1[index_column]) - set(df2[index_column]))
    return df1.iloc[list(df1['new_index'].isin(indices_to_keep))]


def check_age(control, experiment):
    """
    Compares age - Age at neonatal birth > age at lapro + 1 (surgery followed by birth or rounding down)
    :param control: integer, age at control
    :param experiment: integer, age at experiment
    :return: True \ False if condition is filled
    """
    return control > experiment + 1


def check_parity(control, experiment):
    """
    Compares parity - Same parity (1st, 2nd, 3rd etc birth).
    :param control: parity at control
    :param experiment: parity at experiment
    :return: True \ False if condition is filled
    """
    return control == experiment


def check_num_fetuses(control, experiment):
    """
    Compares number of fetuses - Same number of fetuses (single, twins, triplets, etc.)
    :param control: number of fetuses at control
    :param experiment: number of fetuses at experiment
    :return: True \ False if condition is filled
    """
    return control == experiment


def check_birth_date(control, experiment):
    """
    Compares neonatal birth dates - Similar neonatal birth date. For births between 2011-2016 we can find exact match, for earlier births,
    find closest year and date within +/- 7 days. (20/10/2009 --> 13-27/10/2011).

    :param control: neonatal birth date at control
    :param experiment: neonatal birth date at experiment
    :return: True \ False if condition is filled
    """
    day_diff = pd.Timedelta('7 days')
    if not 2011 < experiment.year < 2016:
        experiment = datetime(control.year, experiment.month, experiment.day)
    return experiment - day_diff < control < experiment + day_diff


def check_control_row(row, age_at_lapro, parity_at_lapro, num_fetuses_at_lapro, neonatal_birth_date_at_lapro):
    """
    Will be applied to Pandas DataFrame.
    For each row in control will check the following conditions:
    1. Age at neonatal birth > age at lapro + 1 (surgery followed by birth or rounding down)
    2. Same parity (1st, 2nd, 3rd etc birth).
    3. Same number of fetuses (single, twins, triplets, etc.)
    4. Similar neonatal birth date. For births between 2011-2016 we can find exact match, for earlier births,
       find closest year and date within +/- 7 days. (20/10/2009 --> 13-27/10/2011).

    :param row:
    :param age_at_lapro:
    :param parity_at_lapro:
    :param num_fetuses_at_lapro:
    :param neonatal_birth_date_at_lapro:
    :return: True \ False for if conditions are filled
    """
    all_conditions = [
        check_age(row.calculated_maternal_age_at_birth_year, age_at_lapro),
        check_parity(row.parity, parity_at_lapro),
        check_num_fetuses(row.num_fetuses, num_fetuses_at_lapro),
        check_birth_date(row.neonatal_birth_date, neonatal_birth_date_at_lapro)
    ]
    return all(all_conditions)


def check_experiment_row(row, control_df):
    """
    Will be applied to Pandas DataFrame.
    For each row in experiment will check all control rows.
    :param row:
    :return: list of suitable indices from control
    """

    age_at_lapro = row.age_at_procedure
    parity_at_lapro = row.parity
    num_fetuses_at_lapro = row.num_fetuses
    neonatal_birth_date_at_lapro = row.neonatal_birth_date

    args = (age_at_lapro, parity_at_lapro, num_fetuses_at_lapro, neonatal_birth_date_at_lapro)
    is_suitable = control_df.apply(check_control_row, axis=1, args=args)
    a = 5


def find_suitable_indices(experiment_df, control_df, num_samples_control=2):
    """
    Goes over each row in experiment and finds matches in control.
    This will provide us with a list of suitable indices from control.
    Then, for each list of indices, randomly select N samples and make sure the are not selected for any other row.
    :param experiment_df: Pandas dataframe
    :param control_df: Pandas dataframe
    :param num_samples_control: integer
    :return: pandas dataframe
    """

    # get list of controls per experiment row
    matching_controls = experiment_df.apply(check_experiment_row, axis=1, args=(control_df,))

    # arrange data in new dataframe - experiment row (duplicated) concatenated with each control row

    return new_dataframe

    a = 5


# arrange data - control and experiment
clean_pkl = 'clean_temp.pkl'
if path.exists(clean_pkl):
    data = load_from_pkl(clean_pkl)
    clean_experiment = data['clean_experiment']
    clean_control = data['clean_control']
else:
    clean_experiment = arrange_experiment(experiment.copy())
    clean_control = arrange_control(control.copy(), clean_experiment)
    save_to_pkl(clean_pkl, clean_experiment=clean_experiment, clean_control=clean_control)

# find matches in control for rows from experiment
res = find_suitable_indices(clean_experiment, clean_control, num_samples_control=2)

a = 5