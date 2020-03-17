import math
import material_constants as material_constants
import inputdata as inputdata
import numpy


def strain_calc(strain_init, time_step, strain_rate):
    
    strain_current = strain_init + strain_rate * time_step

    return strain_current


def calc_const_A0(temperature, strain_rate_initial):
    return inputdata.M * strain_rate_initial / \
           material_constants.calc_burgers_vector(temperature)


def calc_const_A2 (temperature):
    return inputdata.fitting_params['C_4'] * inputdata.fitting_params['C_5'] * \
           material_constants.calc_burgers_vector(temperature) * inputdata.M / inputdata.fitting_params['C_9']


def calc_const_A1(temperature):
    part1 = inputdata.M * inputdata.alpha * material_constants.calc_shear_modulus(temperature)\
            / (inputdata.K_b * temperature)
    part2 = math.pow(material_constants.calc_burgers_vector(temperature), 4)
    return inputdata.fitting_params['C_4'] * inputdata.fitting_params['C_5'] * part1 * part2


def calc_const_A4(temperature):
    step1 = (material_constants.calc_shear_modulus(temperature) / (2 * inputdata.K_b * temperature)) \
            * math.pow(material_constants.calc_burgers_vector(temperature), 3)
    
    step2 = inputdata.fitting_params['C_8'] * step1
    return numpy.exp(step2)


def calc_const_A3(temperature, strain_rate_initial):
    return calc_const_A0(temperature, strain_rate_initial)/(inputdata.fitting_params['C_7'] * inputdata.nu_a)


def calc_const_A5(temperature, strain_rate_initial):
    return calc_const_A3(temperature, strain_rate_initial) * calc_const_A4(temperature)


def dislocation_density_calc(rho_prev, time_step, temperature, strain_rate_initial, D_def):
#    D_t = inputdata.grain_size_init * math.exp(-2*temp_strain/math.sqrt(3))
    subpart1 = (calc_const_A0(temperature, strain_rate_initial) * inputdata.fitting_params['C_1'])\
               / (3 * D_def)
    
    subpart2 = calc_const_A0(temperature, strain_rate_initial) * inputdata.fitting_params['C_2'] * math.sqrt(rho_prev)
    
    subpart3 = -3 * inputdata.fitting_params['C_3'] * calc_const_A0(temperature, strain_rate_initial) * \
                    material_constants.calc_burgers_vector(temperature) * rho_prev
   
    subpart4 = -5 * calc_const_A1(temperature) * material_constants.calc_effective_diffusivity(temperature, rho_prev)\
               * math.pow(rho_prev, 2.5)
    
    subpart5 = (subpart4 / (5 * calc_const_A1(temperature))) * calc_const_A2(temperature) * math.asinh(calc_const_A5(temperature, strain_rate_initial) / math.pow(rho_prev, 0.5))
    
    rho_current = (subpart1 + subpart2 + subpart3 + subpart4 + subpart5) * time_step + rho_prev
    return rho_current
