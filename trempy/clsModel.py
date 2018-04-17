"""This module includes the specification of the model."""
import numpy as np

from trempy.shared.shared_auxiliary import dist_class_attributes
from trempy.shared.shared_auxiliary import print_init_dict
from trempy.paras.clsParas import ParasCls
from trempy.shared.clsBase import BaseCls
from trempy.read.read import read


class ModelCls(BaseCls):
    """This class manages all issues about the model specification."""
    def __init__(self, fname):

        init_dict = read(fname)

        # We first tackle the more complex issue of parameter management.
        paras_obj = ParasCls(init_dict)

        self.attr = dict()

        # Parameters
        self.attr['paras_obj'] = paras_obj

        # Cutoffs
        self.attr['cutoffs'] = init_dict['CUTOFFS']

        # Simulation
        self.attr['sim_agents'] = init_dict['SIMULATION']['agents']
        self.attr['sim_seed'] = init_dict['SIMULATION']['seed']
        self.attr['sim_file'] = init_dict['SIMULATION']['file']

        # Estimation
        self.attr['est_detailed'] = init_dict['ESTIMATION']['detailed']
        self.attr['optimizer'] = init_dict['ESTIMATION']['optimizer']

        self.attr['est_agents'] = init_dict['ESTIMATION']['agents']
        self.attr['est_file'] = init_dict['ESTIMATION']['file']
        self.attr['maxfun'] = init_dict['ESTIMATION']['maxfun']
        self.attr['start'] = init_dict['ESTIMATION']['start']

        # Optimizer options
        self.attr['opt_options'] = dict()

        self.attr['opt_options']['SCIPY-BFGS'] = dict()
        self.attr['opt_options']['SCIPY-BFGS']['gtol'] = init_dict['SCIPY-BFGS']['gtol']
        self.attr['opt_options']['SCIPY-BFGS']['eps'] = init_dict['SCIPY-BFGS']['eps']

        self.attr['opt_options']['SCIPY-POWELL'] = dict()
        self.attr['opt_options']['SCIPY-POWELL']['xtol'] = init_dict['SCIPY-POWELL']['xtol']
        self.attr['opt_options']['SCIPY-POWELL']['ftol'] = init_dict['SCIPY-POWELL']['ftol']

        para_objs = paras_obj.get_attr('para_objs')

        questions = []
        for para_obj in para_objs:
            label = para_obj.get_attr('label')
            if label in ['alpha', 'eta', 'beta']:
                continue

            questions += [label]

        self.attr['questions'] = sorted(questions)
        self.attr['num_questions'] = len(questions)

        # We now need to check the integrity of the class instance.
        self._check_integrity()

    def update(self, perspective, which, values):
        """This method updates the estimation parameters."""
        # Distribute class attributes
        paras_obj = self.attr['paras_obj']

        paras_obj.set_values(perspective, which, values)

    def write_out(self, fname):
        """This method creates a initialization dictionary of the current class instance."""
        init_dict = dict()

        for label in ['PREFERENCES', 'QUESTIONS', 'CUTOFFS',  'ESTIMATION', 'SIMULATION']:
            init_dict[label] = dict()

        paras_obj = self.attr['paras_obj']
        questions = self.attr['questions']

        # Preferences
        for label in ['alpha', 'beta', 'eta']:
            init_dict['PREFERENCES'][label] = paras_obj.get_para(label)

        # Questions
        for q in questions:
            init_dict['QUESTIONS'][q] = paras_obj.get_para(q)

        # Cutoffs
        init_dict['CUTOFFS'] = self.attr['cutoffs']

        # Estimation
        init_dict['ESTIMATION']['detailed'] = self.attr['est_detailed']
        init_dict['ESTIMATION']['optimizer'] = self.attr['optimizer']
        init_dict['ESTIMATION']['agents'] = self.attr['est_agents']
        init_dict['ESTIMATION']['file'] = self.attr['est_file']
        init_dict['ESTIMATION']['maxfun'] = self.attr['maxfun']
        init_dict['ESTIMATION']['start'] = self.attr['start']

        # Simulation
        init_dict['SIMULATION']['agents'] = self.attr['sim_agents']
        init_dict['SIMULATION']['seed'] = self.attr['sim_seed']
        init_dict['SIMULATION']['file'] = self.attr['sim_file']

        # Optimizer options
        init_dict['SCIPY-BFGS'] = dict()
        init_dict['SCIPY-BFGS']['gtol'] = self.attr['opt_options']['SCIPY-BFGS']['gtol']
        init_dict['SCIPY-BFGS']['eps'] = self.attr['opt_options']['SCIPY-BFGS']['eps']

        init_dict['SCIPY-POWELL'] = dict()
        init_dict['SCIPY-POWELL']['xtol'] = self.attr['opt_options']['SCIPY-POWELL']['xtol']
        init_dict['SCIPY-POWELL']['ftol'] = self.attr['opt_options']['SCIPY-POWELL']['ftol']

        print_init_dict(init_dict, fname)

    def _check_integrity(self):
        """This method checks the integrity of the class instance."""
        # Distribute class attributes for further processing.
        args = []
        args += ['paras_obj', 'sim_seed', 'sim_agents', 'sim_file', 'est_agents', 'maxfun']
        args += ['est_file', 'questions', 'start']

        paras_obj, sim_seed, sim_agents, sim_file, est_agents, maxfun, est_file, questions, \
            start = dist_class_attributes(self, *args)

        # We restrict the identifiers for the questions between 1 and 16
        np.testing.assert_equal(0 < min(questions) <= max(questions) < 16, True)

        # We have to alternative how to start the estimation.
        np.testing.assert_equal(start in ['init', 'auto'], True)
