"""This module contains some integration tests."""
import pickle as pkl

import numpy as np

from trempy.shared.shared_auxiliary import dist_class_attributes
from trempy.shared.shared_auxiliary import criterion_function
from trempy.shared.shared_auxiliary import print_init_dict
from trempy.config_trempy import PACKAGE_DIR
from trempy.clsModel import ModelCls
from trempy import simulate


def run_regression_test(test):
    """Run a single regression test.

    It is repeatedly used by the testing infrastructure.
    Thus, manual modifications are only required here.
    """
    # Create and process initialization file
    init_dict, crit_val = test

    # TEMPORARY: for old regression vault, 'version' is missing. Delete for new batch.
    if 'VERSION' not in init_dict.keys():
        init_dict['VERSION'] = dict()
        init_dict['VERSION']['version'] = 'scaled_archimedean'
        init_dict['SCIPY-L-BFGS-B'] = dict()
        init_dict['SCIPY-L-BFGS-B']['gtol'] = 1e-5
        init_dict['SCIPY-L-BFGS-B']['ftol'] = 1e-5
        init_dict['SCIPY-L-BFGS-B']['eps'] = 1e-5

    print_init_dict(init_dict)
    model_obj = ModelCls('test.trempy.ini')
    df, fval = simulate('test.trempy.ini')

    # Distribute class attributes for further processing.
    args = [model_obj, 'paras_obj', 'questions', 'cutoffs', 'version']
    paras_obj, questions, cutoffs, version = dist_class_attributes(*args)

    if version in ['scaled_archimedean']:
        args = [model_obj, 'marginals', 'upper']
        marginals, upper = dist_class_attributes(*args)
        version_specific = {'marginals': marginals, 'upper': upper}
    else:
        version_specific = None

    # The number of actual economic parameters in paras_obj not counting questions.
    n_econ_params = paras_obj.attr['nparas_econ']

    # Standard deviations
    x_econ_all = paras_obj.get_values('econ', 'all')
    if version in ['scaled_archimedean']:
        stands = x_econ_all[5:]
    elif version in ['nonstationary']:
        stands = x_econ_all[n_econ_params:]

    stat = criterion_function(df=df, questions=questions, cutoffs=cutoffs,
                              paras_obj=paras_obj, version=version, sds=stands,
                              **version_specific)

    np.testing.assert_almost_equal(stat, crit_val)


def test_1():
    """Run a small sample of the regression test battery."""
    tests = pkl.load(open(PACKAGE_DIR + '/tests/regression_vault.trempy.pkl', 'rb'))
    i = 0
    for test in tests[:5]:
        i = i + 1

        print(i)
        print('\n')
        print(test)
        print('\n')

        run_regression_test(test)
