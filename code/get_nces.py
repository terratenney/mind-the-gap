#!/usr/bin/env python2.7 
"""pull pertinent data from NCES tab delimited files""" 

import pandas as pd
import numpy as np


def NCES_boolean(x):
    if x == 1:
        return True
    elif x == 2:
        return False
    else:
        return np.nan


def schools(_schoolids=None, columns=None):
    """
    INPUT: pandas series of NCES school ids
           specific column names (optional)
    OUTPUT: pandas dataframe 

    step through NCES CCD school data and grab school stats for given Donors Choose NCES school id
    """

    # hard-code boolean columns
#     boolcolumns = ["BIES", "RECONSTF", "ISMEMPUP", "ISFTEPUP", "ISFTEPUP", "ISPFEMALE", "ISPWHITE", "ISPELM",
#                    "PKOFFRD", "KGOFFRD", "G01OFFRD", "G02OFFRD", "G03OFFRD", "G04OFFRD", "G05OFFRD", "G06OFFRD", 
#                    "G07OFFRD", "G08OFFRD", "G09OFFRD", "G10OFFRD", "G11OFFRD", "G12OFFRD", "UGOFFRD",
#                    "CHARTR", "MAGNET", "TITLEI", "STITLI"]

    # load-in NCES school data 
    schooldf = pd.read_csv("../data/school/sc111a_supp.txt", sep='\t', 
                           low_memory=False,
#                            na_values=[-1, -2, -9, 'M', 'N'])
                           na_values=['M', 'N', 'R'])

    schooldf.index = schooldf.pop("NCESSCH")

    # student-teacher ratio
    schooldf["ST_ratio"] = schooldf.MEMBER/schooldf.FTE

#     for column in boolcolumns:
#         schooldf[column] = schooldf[column].apply(NCES_boolean)

    if _schoolids:
        if columns:
            outdf = schooldf[columns].loc[_schoolids].copy()
        else:
            outdf = schooldf.loc[_schoolids].copy()
    else:
        outdf = schooldf.copy()

    return outdf


def districts(lea_ids=None, columns=[], state="", dropna=False):
    """
    INPUT: pandas series of local education agency ids indexed by NCES school ids (optional)
           specific column names to include (optional)
    OUTPUT: pandas dataframe

    step through NCES CCD district data and grab school stats for every DonorsChoose NCES local education agency id
    """

    # load-in NCES school data
    districtdf = pd.read_csv("../data/district/sdf11_1a.txt", index_col=0, sep='\t',
                             low_memory=False, na_values=[-1, -2, -9, 'M', 'N', 'R'])
#                              low_memory=False, na_values=['M', 'N'])

    # binarize GSLO and GSHI with pd.get_dummies
#     districtdf = pd.concat([districtdf, pd.get_dummies(districtdf.GSLO, prefix="GSLO")], axis=1)
#     districtdf = pd.concat([districtdf, pd.get_dummies(districtdf.GSHI, prefix="GSHI")], axis=1)

    # make sure LEAIDs are integer values
    districtdf.index = districtdf.index.astype(np.int)

    if state:
        districtdf = districtdf[districtdf.STABBR == state] 

    if lea_ids:
        if columns:
            outdf = districtdf[columns].loc[lea_ids].copy()
        else:
            outdf = districtdf.loc[lea_ids].copy()

        # index by school_ids instead of lea_ids
        outdf.index = lea_ids.index
    else:
        if columns:
            outdf = districtdf[columns].copy()
        else:
            outdf = districtdf.copy()

    # binarize GSLO and GSHI with pd.get_dummies
    # (add even if not specified on columns kwarg)
    if lea_ids:
        outdf = pd.concat([outdf, pd.get_dummies(districtdf.loc[lea_ids].GSLO, prefix="GSLO")], axis=1)
        outdf = pd.concat([outdf, pd.get_dummies(districtdf.loc[lea_ids].GSHI, prefix="GSHI")], axis=1)
    else:
        outdf = pd.concat([outdf, pd.get_dummies(districtdf.GSLO, prefix="GSLO")], axis=1)
        outdf = pd.concat([outdf, pd.get_dummies(districtdf.GSHI, prefix="GSHI")], axis=1)

    if dropna:
        outdf = outdf.dropna()

    return outdf


def schools_and_districts(school_ids):
    """
    INPUT: pandas series of NCES school ids
    OUTPUT: pandas dataframe with index as the given series of school ids

    grab both NCES school demographics and NCES district finance data
    """
    print "[grab NCES data...]"

    columns = ["SCHNAM", "SURVYEAR", "LEAID", "FTE", "TOTFRL", "MEMBER", "ST_ratio"]
    NCES_schools = schools(school_ids, columns=columns)

    columns = ["TOTALREV", "TFEDREV", "TSTREV", "TLOCREV", "TOTALEXP", "TCURSSVC", "TCAPOUT", "HR1", "HE1", "HE2"]
    NCES_districts = districts(NCES_schools.LEAID, columns=columns)

    NCESdf = pd.concat([NCES_schools, NCES_districts], axis=1)

    return NCESdf
