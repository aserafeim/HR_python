import material_constants as mat_const
import math
import numpy
import inputdata

rho_full_rx = 1e11

def calc_driving_force(rho_prev, temperature):
    '''for austenite dislocation density of a fully recrystallised grain is 1e11'''
    driving_force = mat_const.calc_dislocation_line_energy(temperature) * (rho_prev - rho_full_rx)
    return driving_force

def calc_critical_radius_rx_grain(rho_prev, temperature):
    'this is the critical radius of the RX-ed grain, i.e. the radius with which the rx_ed nucleus becomes stable as a grain'
    return mat_const.calc_austenite_gb_energy(temperature) / (calc_driving_force(rho_prev, temperature) + 1)

def calc_no_of_nucleated_grains(rho_prev, temperature, time_step, number_grain_prev):
    ans_dict = {}
    crit_radius = calc_critical_radius_rx_grain(rho_prev, temperature)
    '''taking radius of the deformed grain as initial grain radius as of now, To be later implemented as the radius 
    of the grain of the previous time_step'''
    pre_exp_factor = inputdata.C0 * calc_driving_force(rho_prev, temperature) / (4 * 3.1416 * math.pow(crit_radius, 2) *inputdata.grain_size_init)
    exp_factor = math.exp(-inputdata.activation_energy_static_rx / (inputdata.uni_gas_const * (temperature)))
    number_rxed_grains = pre_exp_factor * exp_factor * time_step
    ans_dict['N'] = number_grain_prev + number_rxed_grains
    ans_dict['dN'] = number_rxed_grains
    return ans_dict


def calc_radius_growth(rho_prev, temperature, time_step):
    radius = mat_const.calc_gb_mobility(temperature) * calc_driving_force(rho_prev, temperature) * time_step
    #print('mat_const.calc_gb_mobility(temperature)', mat_const.calc_gb_mobility(temperature))
    return radius


def static_rx(rho_prev, rho_def, number_grain_prev, radius_grain_prev, d0, temperature, time_step,r_rx_prev):
    
    return_dict = {}
    return_dict['driving_force'] = calc_driving_force(rho_prev, temperature)
    
    return_dict['critical_nuclei_radius'] = critical_radius = calc_critical_radius_rx_grain(rho_prev, temperature)
    
    #no_grains_rx_curr = calc_no_of_nucleated_grains(rho_prev, temperature, time_step, number_grain_prev)
    '''return_dict['newly_nucleated_grains']=no_grains_rx_curr['dN']'''
    #newly_nucleated_grains = calc_no_of_nucleated_grains(rho_prev, temperature, time_step, number_grain_prev)['']
    #return_dict['N_rx'] = no_grains_rx_curr['N']
    '''check for nucleation possible or not'''

    return_dict['r_rx_prev-critical'] = r_rx_prev - critical_radius
    if critical_radius > r_rx_prev:
        number_rxed_grains = 0
        mean_rxed_grain_size = critical_radius
    else:
        pre_exp_factor = inputdata.C0 * calc_driving_force(rho_prev, temperature) / (4 * 3.1416 * math.pow(critical_radius, 2) *inputdata.grain_size_init)
        exp_factor = math.exp(-inputdata.activation_energy_static_rx / (inputdata.uni_gas_const * (temperature)))
        number_rxed_grains = pre_exp_factor * exp_factor * time_step
    
    return_dict['newly_nucleated_grains']= number_rxed_grains
    #n_rx = number_grain_prev + number_rxed_grains
    return_dict['N_rx'] = n_rx_i = number_grain_prev + number_rxed_grains
    
    mean_rxed_grain_size = (radius_grain_prev * number_grain_prev + number_rxed_grains * calc_critical_radius_rx_grain(rho_prev, temperature))/n_rx_i
    
    return_dict['mean_rxed_grain_size'] = mean_rxed_grain_size
    return_dict['new_rxed_grain_size']=new_rxed_grain_size = mean_rxed_grain_size + calc_radius_growth(rho_prev, temperature, time_step)
    return_dict['recrystallised_fraction']=recrystallised_fraction = 4/3 * (22/7) * math.pow(new_rxed_grain_size, 3) * n_rx_i
    return_dict['mean_grain_size']=new_rxed_grain_size*recrystallised_fraction + (1- recrystallised_fraction)* (d0/2)
    return_dict['mean_rho_new']= rho_def * (1-recrystallised_fraction) + recrystallised_fraction * rho_full_rx

    return return_dict