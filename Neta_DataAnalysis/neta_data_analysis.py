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
pkl_pth = 'temp_12_2018.pkl'
if path.exists(pkl_pth):
    data = load_from_pkl(pkl_pth)
    control = data['control']
    experiment = data['experiment']
else:
    control = pd.read_excel('control_2.xlsx').dropna(how='all')
                            # parse_dates=['maternal_birth_date', 'neonatal_birth_date']).dropna(how='all')
    # experiment = pd.read_excel('experiment_2.xlsx', sheet_name='experiment', parse_dates=['BirthDate']).dropna(how='all')
    experiment = pd.read_excel('experiment_2.xlsx').dropna(how='all')
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


def all_to_datetime(row, field):
    date_str = row[field]
    if isinstance(date_str, datetime):
        return date_str
    if isinstance(date_str, float) and str(date_str) == 'nan':
        return None
    if isinstance(date_str, pd.Timestamp):
        return datetime(date_str.year, date_str.month, date_str.day)
    year = int(date_str[0:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    return datetime(year, month, day)


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
    df['neonatal_birth_date'] = df.apply(all_to_datetime, axis=1, args=('neonatal_birth_date',))

    # TODO: calculate maternal age at birth? if columns are not timestamps - convert

    # remove from control any rows that exist in experiment
    df = remove_overlap(df, experiment_df, 'new_index')

    # remove rows with missing information
    df.dropna(subset=['neonatal_birth_date'], inplace=True)

    return df


def arrange_experiment(df):
    """
    Arranges experiment data - dropping rows without parity, creating index from case_id_parity, removing duplicates.
    :param df: Pandas frame, experiment
    :return: Pandas frame
    """

    # re-arrange column names
    column_mapping = {
        # u'שם מלא': 'full_name',
        u'name': 'full_name',
        # u'מספר ת_ז': 'id',
        u'ID': 'id',
        # u'גיל ': 'age_at_procedure',
        u'age': 'age_at_procedure',
        u'BirthDate': 'neonatal_birth_date',
        u'parity': 'parity',
        # u'P': 'parity',
        u'Is_twins?': 'num_fetuses',
        u'הוצא מהביקורת ': 'removed_from_control',
        u'ביקורת 1': 'control_1',
        u'ביקורת 2 ': 'control_2'
    }
    df.rename(columns=column_mapping, inplace=True)

    # create new index and remove duplicates
    df = create_new_index(df)
    df.drop_duplicates(inplace=True)

    # increase number of fetuses (0 for 1 fetus)
    df['num_fetuses'] += 1

    # convert dates, if needed
    df['neonatal_birth_date'] = df.apply(all_to_datetime, axis=1, args=('neonatal_birth_date',))

    # remove rows with missing information
    df.dropna(subset=['neonatal_birth_date'], inplace=True)

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
    return df1.iloc[list(df1[index_column].isin(indices_to_keep))]


def check_age(control, experiment):
    """
    Compares age - Age at neonatal birth > age at lapro + 1 (surgery followed by birth or rounding down)
    :param control: integer, age at control
    :param experiment: integer, age at experiment
    :return: True \ False if condition is filled
    """
    return experiment <= control <= experiment + 1


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
    now = datetime.now()
    age_at_lapro = row.age_at_procedure
    parity_at_lapro = row.parity
    num_fetuses_at_lapro = row.num_fetuses
    neonatal_birth_date_at_lapro = row.neonatal_birth_date

    args = (age_at_lapro, parity_at_lapro, num_fetuses_at_lapro, neonatal_birth_date_at_lapro)
    is_suitable = control_df.apply(check_control_row, axis=1, args=args)
    suitable_rows = control_df.iloc[list(is_suitable)][['case', 'full_name', 'id', 'calculated_maternal_age_at_birth_year',
                                                       'parity', 'num_fetuses', 'new_index']]
    column_mapping = {'case': 'ctrl_case', 'full_name': 'ctrl_full_name', 'id': 'ctrl_id', 'parity': 'ctrl_parity',
                      'new_index': 'ctrl_index',
                      'calculated_maternal_age_at_birth_year': 'ctrl_age', 'num_fetuses': 'ctrl_num_fetuses'}
    suitable_rows.rename(columns=column_mapping, inplace=True)
    suitable_rows['run_ix'] = range(len(suitable_rows))
    suitable_rows.set_index('run_ix', inplace=True)
    our_row = [row['full_name'], row['id'], row['age_at_procedure'], row['parity'], row['num_fetuses']]
    dup_df = pd.DataFrame([our_row] * len(suitable_rows),
                          columns=['exp_full_name', 'exp_id', 'exp_age', 'exp_parity', 'exp_num_fetuses'])
    dup_df['run_ix'] = range(len(dup_df))
    dup_df.set_index('run_ix', inplace=True)
    print('finished one experiment row - took {} seconds'.format(datetime.now() - now))
    return [dup_df.join(suitable_rows)]


def find_suitable_indices(experiment_df, control_df, num_samples_control=2, final_path='tmp.xlsx'):
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
    # experiment_df = experiment_df.iloc[:5]  # TODO: remove this for full data
    matching_controls = experiment_df.apply(check_experiment_row, axis=1, args=(control_df,)).id

    columns = sorted(matching_controls.iloc[0].columns)
    new_dataframe = pd.DataFrame(columns=columns)
    for exp_row_ix in range(len(matching_controls)):
        exp_row = matching_controls.iloc[exp_row_ix]

        if len(new_dataframe) and len(exp_row):
            exp_row = remove_overlap(exp_row, new_dataframe, 'ctrl_index')

        if len(exp_row) >= num_samples_control:
            sampled_controls = exp_row.sample(num_samples_control)
        else:
            sampled_controls = exp_row
        new_dataframe = pd.concat([new_dataframe, sampled_controls])

    new_dataframe.to_excel(final_path)


# arrange data - control and experiment
clean_pkl = 'clean_temp_2.pkl'
if path.exists(clean_pkl):
    data = load_from_pkl(clean_pkl)
    clean_experiment = data['clean_experiment']
    clean_control = data['clean_control']
else:
    clean_experiment = arrange_experiment(experiment.copy())
    clean_control = arrange_control(control.copy(), clean_experiment)
    save_to_pkl(clean_pkl, clean_experiment=clean_experiment, clean_control=clean_control)

# find matches in control for rows from experiment
find_suitable_indices(clean_experiment, clean_control,
                      num_samples_control=2, final_path='tmp_2.xlsx')


