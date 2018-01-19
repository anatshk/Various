import pandas as pd

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
3. In experiment (Lapro) table - a single patient can undergo several procedures. 
If all procedures are within scope of same pregnancy - treat them as single row and only find matches from control once.


Data Validation:
1. Rows in experiment should be removed from control.
2. Rows in experiment without parity - should be removed.

Other:
* rows colored purple - manually created couplings. Can be used to test final flow. 
  Comparison should be contains and not exact. 
  In 'experiment' sheet in experiment.xlsx, there is a list of the selected rows.
"""