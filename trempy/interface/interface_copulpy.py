"""Manage everything related to interfacing the copulpy package."""
import numpy as np

from copulpy import UtilityCopulaCls


def get_copula_scaled_archimedean(upper, marginals, r_self, r_other, delta, self, other):
    """Access a multiattribute utility copula."""
    copula_spec = dict()

    version = 'scaled_archimedean'
    copula_spec['version'] = version
    copula_spec[version] = dict()

    copula_spec[version]['r'] = [r_self, r_other]
    copula_spec[version]['marginals'] = marginals
    copula_spec[version]['u'] = self, other
    copula_spec[version]['bounds'] = upper
    copula_spec[version]['delta'] = delta

    copula_spec[version]['generating_function'] = 1
    copula_spec[version]['version'] = 'scaled_archimedean'
    copula_spec[version]['a'] = 1.0
    copula_spec[version]['b'] = 0.0

    copula = UtilityCopulaCls(copula_spec)

    return copula


def get_copula_nonstationary(alpha, beta, gamma, y_scale,
                             discount_factors_0, discount_factors_1, discount_factors_3,
                             discount_factors_6, discount_factors_12, discount_factors_24,
                             unrestricted_weights_0, unrestricted_weights_1,
                             unrestricted_weights_3, unrestricted_weights_6,
                             unrestricted_weights_12, unrestricted_weights_24,
                             # Quick and dirty implementation of other discounting functions.
                             exp_discounting=False,
                             beta_delta_discounting=False,
                             stationary_model=False
                             ):
    """Access the nonstationary utility copula."""
    version = 'nonstationary'
    copula_spec = {'version': version}
    copula_spec[version] = {
        'version': version,
        'y_scale': y_scale,
        'alpha': alpha,
        'gamma': gamma,
        'beta': beta,
    }
    # Anti-bugging.
    np.testing.assert_equal(exp_discounting and beta_delta_discounting, False)

    if exp_discounting is True:
        # Use discount_factors_0 for delta. Here, one "period" has length 1 month.
        dict_discount_f = {
            0: 1,
            1: discount_factors_0,
            3: discount_factors_0 ** 3,
            6: discount_factors_0 ** 6,
            12: discount_factors_0 ** 12,
            24: discount_factors_0 ** 24,
        }
    elif beta_delta_discounting is True:
        # Use discount_factors_0 and _1 for beta and delta.
        dict_discount_f = {
            0: 1,
            1: discount_factors_0 * discount_factors_1,
            3: discount_factors_0 * discount_factors_1 ** 3,
            6: discount_factors_0 * discount_factors_1 ** 6,
            12: discount_factors_0 * discount_factors_1 ** 12,
            24: discount_factors_0 * discount_factors_1 ** 24,
        }
    else:
        # "Nonparametric" discount factors D_t for t in 0,1,3,6,12,24.
        dict_discount_f = {
            0: discount_factors_0,
            1: discount_factors_1,
            3: discount_factors_3,
            6: discount_factors_6,
            12: discount_factors_12,
            24: discount_factors_24,
        }
    copula_spec[version]['discount_factors'] = dict_discount_f

    # Optional argument: unrestricted weights
    dict_unrestriced = {
        0: unrestricted_weights_0,
        1: unrestricted_weights_1,
        3: unrestricted_weights_3,
        6: unrestricted_weights_6,
        12: unrestricted_weights_12,
        24: unrestricted_weights_24,
    }

    if None in dict_unrestriced.values():
        dict_unrestriced = None

    # The model becomes stationary.
    if stationary_model is True:
        dict_unrestriced = {key: y_scale for key in [0, 1, 3, 6, 12, 24]}

    copula_spec[version]['unrestricted_weights'] = dict_unrestriced

    # Build copula
    copula = UtilityCopulaCls(copula_spec)

    return copula
