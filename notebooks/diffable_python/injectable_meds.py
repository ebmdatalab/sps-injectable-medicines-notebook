# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# The [Specialist Pharmacy Service](https://www.sps.nhs.uk/) is preparing guidance for CCGs, practices and others around delaying delaying administration of injectable medicines in primary care during the pandemic. This notebook sets out the prescribing of these medicines over the last decade.
#
# Readers may find the ["What is a BNF code blog"](https://ebmdatalab.net/prescribing-data-bnf-codes/) useful reading for shortlisting some injections.

#import libraries required for analysis
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from ebmdatalab import bq, charts, maps
import os

## ensuring the format is consistent for pounds and pence
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# +
sql = '''
SELECT
    pct,
    CAST(month AS DATE) AS month,
    bnf.presentation,
    bnf_code,
    SUM(items) AS items,
    SUM(actual_cost) AS cost
FROM hscic.normalised_prescribing_standard presc
INNER JOIN hscic.practices pract ON presc.practice = pract.code
INNER JOIN
  hscic.ccgs AS ccg
ON
  presc.pct=ccg.code
INNER JOIN
  hscic.bnf as bnf
ON
  presc.bnf_code = bnf.presentation_code
WHERE
    ccg.org_type='CCG' AND
    pract.setting = 4 AND
    presc.bnf_code IN (
        SELECT DISTINCT(bnf_code)
        FROM ebmdatalab.measures.dmd_objs_with_form_route
        WHERE 
        (form_route LIKE '%intravenous%' OR
        form_route LIKE'%injection%' OR
        form_route LIKE'%subcutaneous')      
        AND 
        bnf_code NOT LIKE "060101%"  #insulin out of scope
        AND
        bnf_code NOT LIKE "0304030C0%" #adrenaline out of scope
        AND
        bnf_code NOT LIKE "140%" #vaccines out of scope
        )
GROUP BY pct, month, presentation, bnf_code
ORDER BY pct, month
'''

df_inj = bq.cached_read(sql, csv_path=os.path.join('..','data', 'df_inj.zip'))
df_inj['month'] = df_inj['month'].astype('datetime64[ns]')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
df_inj.head()
# -

df_inj.groupby("month")['items'].sum().plot(kind='line', title="Total items of injectable preparations in English primary care")
plt.ylim(0, )

df_inj.nunique()

df_inj["presentation"].unique()

##groupby bnf name  to see largest volume in terms of items
df_products = df_inj.groupby(['bnf_code', 'presentation']).sum().reset_index().sort_values(by = 'items', ascending = False)
df_products.head(100)
