import pandas as pd

from os import path
from utils import save_to_pkl, load_from_pkl

"""
For each row in Laproscopy DB (experiment.xlsx), find 2 rows in Control DB (contron.xlsx).

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
    control, experiment = load_from_pkl(pkl_pth).values()
else:
    control = pd.read_excel('control.xlsx').dropna()
    experiment = pd.read_excel('experiment.xlsx', sheet_name='experiment').dropna()
    save_to_pkl(pkl_pth, control=control, experiment=experiment)


def create_new_index(df):
    # remove rows without parity
    df.dropna(subset=['parity'], inplace=True)

    # create a new index of case, id, parity
    def new_index(row):
        return row.case + '_' + row.id + '_' + str(row.parity)
    df['new_index'] = df.apply(new_index, axis=1)
    return df


def arrange_control(df):
    """
    Arranges the control file.
    :param df: Pandas frame
    :return: Pandas frame
    """

    df = create_new_index(df)

    # new column - count number of fetuses (= duplicate rows) - find duplicates and count
    duplicated = df.loc[df.duplicated(keep=False)]
    counted_multi_fetuses = duplicated.groupby('new_index').count()['id']

    def num_fetuses(row):
        return counted_multi_fetuses[row.new_index] if row.new_index in counted_multi_fetuses else 1
    df['num_fetuses'] = df.apply(num_fetuses, axis=1)

    # TODO: calculate maternal age at birth? if columns are not timestamps - convert

    return df


def arrange_experiment(df):
    """
    Arranges experiment data - dropping rows without parity,
    :param df: Pandas frame, experiment
    :return: Pandas frame
    """

    df = create_new_index(df)
    

# clean_control = arrange_control(control.copy())
clean_experiment = arrange_experiment(experiment.copy())



a = 5