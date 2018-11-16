"""This module contains all the required capabilities to read an initialization file."""
import shlex
import os

import numpy as np

from trempy.custom_exceptions import TrempyError
from trempy.config_trempy import DEFAULT_BOUNDS
from trempy.config_trempy import QUESTIONS_ALL
from trempy.config_trempy import HUGE_FLOAT

# Blocks that should be processed all the time.
BASIC_GROUPS = [
    'VERSION', 'SIMULATION', 'ESTIMATION', 'SCIPY-BFGS', 'SCIPY-POWELL', 'CUTOFFS', 'QUESTIONS',
]

# Blocks that are specific to the 'version' of the utility function.
ESTIMATION_GROUP = {
    'scaled_archimedean': ['UNIATTRIBUTE SELF', 'UNIATTRIBUTE OTHER', 'MULTIATTRIBUTE COPULA'],
    'nonstationary': ['ATEMPORAL PARAMETERS', 'TEMPORAL PARAMETERS'],
}


def read(fname):
    """Read the initialization file."""
    # Check input
    np.testing.assert_equal(os.path.exists(fname), True)

    # Initialization
    dict_, group = {}, None

    with open(fname) as in_file:

        for line in in_file.readlines():

            list_ = shlex.split(line)

            # Determine special cases
            is_empty, is_group, is_comment = process_cases(list_)

            # Applicability
            if is_empty or is_comment:
                continue

            # Prepare dictionary
            if is_group:
                group = ' '.join(list_)
                dict_[group] = dict()
                continue

            # Code below is only executed if the current line is not a group name
            flag, value = list_[:2]

            # Handle the VERSION block.
            if (group in ['VERSION']) and (flag in ['version']):
                version = value
                print('Version: {}.'.format(version))

            # Type conversions for the NON-CUTOFF block
            if group not in ['CUTOFFS']:
                value = type_conversions(version, flag, value)

            # We need to make sure questions and cutoffs are not duplicated.
            if flag in dict_[group].keys():
                raise TrempyError('duplicated information')

            # Handle the basic blocks
            if group in BASIC_GROUPS:
                if group in ['CUTOFFS']:
                    dict_[group][flag] = process_cutoff_line(list_)
                elif group in ['QUESTIONS']:
                    dict_[group][flag] = process_coefficient_line(group, list_, value)
                else:
                    dict_[group][flag] = value

            # Handle blocks specific to the 'version' of the utility function.
            if group in ESTIMATION_GROUP[version]:
                if version in ['scaled_archimedean']:
                    if flag not in ['max', 'marginal']:
                        dict_[group][flag] = process_coefficient_line(group, list_, value)
                    else:
                        dict_[group][flag] = value

                elif version in ['nonstationary']:
                    dict_[group][flag] = process_coefficient_line(group, list_, value)

                else:
                    raise TrempyError('version not implemented')

    # We allow for initialization files where no CUTOFFS are specified.
    if "CUTOFFS" not in dict_.keys():
        dict_['CUTOFFS'] = dict()

    # We want to ensure that the keys to the questions are integers
    for label in ['QUESTIONS', 'CUTOFFS']:
        dict_[label] = {int(x): dict_[label][x] for x in dict_[label].keys()}

    # We do some modifications on the cutoff values. Instead of None, we will simply use
    # HUGE_FLOAT and we fill up any missing cutoff values for any possible questions..
    for q in QUESTIONS_ALL:
        if q not in dict_['CUTOFFS'].keys():
            dict_['CUTOFFS'][q] = [-HUGE_FLOAT, HUGE_FLOAT]
        else:
            for i in range(2):
                if dict_['CUTOFFS'][q][i] is None:
                    dict_['CUTOFFS'][q][i] = (-1)**i * -HUGE_FLOAT

    # # Post-processing of the version parameters
    # if version in ['scaled_archimedean']:
    #     pass
    # elif version in ['nonstationary']:
    #     dict_['TEMPORAL PARAMETERS'] = postprocess_temporal_blocks(dict_['TEMPORAL PARAMETERS'])
    # else:
    #     raise TrempyError('version not implemented')

    return dict_


def process_cutoff_line(list_):
    """Process a cutoff line."""
    cutoffs = []
    for i in [1, 2]:
        if list_[i] == 'None':
            cutoffs += [None]
        else:
            cutoffs += [float(list_[i])]

    return cutoffs


def process_bounds(bounds, label):
    """Extract the proper bounds."""
    bounds = bounds.replace(')', '')
    bounds = bounds.replace('(', '')
    bounds = bounds.split(',')
    for i in range(2):
        if bounds[i] == 'None':
            bounds[i] = DEFAULT_BOUNDS[label][i]
        else:
            bounds[i] = float(bounds[i])

    return bounds


def process_coefficient_line(group, list_, value):
    """Process a coefficient line and extracts the relevant information.

    We also impose the default values for the bounds here.
    """
    try:
        label = int(list_[0])
    except ValueError:
        label = list_[0]

    # We need to adjust the labels
    label_internal = label
    if label in ['r'] and 'SELF' in group:
        label_internal = 'r_self'
    elif label in ['r'] and 'OTHER' in group:
        label_internal = 'r_other'

    if len(list_) == 2:
        is_fixed, bounds = False, DEFAULT_BOUNDS[label_internal]
    elif len(list_) == 4:
        is_fixed = True
        bounds = process_bounds(list_[3], label_internal)
    elif len(list_) == 3:
        is_fixed = (list_[2] == '!')

        if not is_fixed:
            bounds = process_bounds(list_[2], label_internal)
        else:
            bounds = DEFAULT_BOUNDS[label_internal]

    return value, is_fixed, bounds


def process_cases(list_):
    """Process cases and determine whether group flag or empty line."""
    # Get information
    is_empty = (len(list_) == 0)

    if not is_empty:
        is_group = list_[0].isupper()
        is_comment = list_[0][0] == '#'
    else:
        is_group = False
        is_comment = False

    # Finishing
    return is_empty, is_group, is_comment


def type_conversions(version, flag, value):
    """Type conversions by version."""
    if flag in ['seed', 'agents', 'maxfun', 'max', 'skip']:
        value = int(value)
    elif flag in ['version', 'file', 'optimizer', 'start', 'marginal']:
        value = str(value)
    elif flag in ['detailed']:
        assert (value.upper() in ['TRUE', 'FALSE'])
        value = (value.upper() == 'TRUE')
    elif flag in []:
        value = value.upper()
    else:
        # Currently both cases are handled identically. This is only future-proofing.
        if version in ['scaled_archimedean']:
            value = float(value)

        elif version in ['nonstationary']:
            # Optional argument needs handling of 'None' string.
            if flag.startswith('unrestricted_weights_') and value == 'None':
                value = None
            else:
                value = float(value)
        else:
            raise TrempyError('version not implemented')

    # Finishing
    return value


# def postprocess_temporal_blocks(block):
#     """Convert temporal block into dictionary."""
#     temporal_dict = dict()
#     for key, value in block.items():
#         # Split at the last occurence of '_' to get the period.
#         varname, period = key.rsplit('_', 1)

#         if varname in temporal_dict.keys():
#             temporal_dict[varname][period] = value
#         else:
#             temporal_dict[varname] = dict()
#             temporal_dict[varname][period] = value

#     return temporal_dict
