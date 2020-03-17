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


def calc_radius_growth(rho_prev, temperature, time_step):
    radius = mat_const.calc_gb_mobility(temperature) * calc_driving_force(rho_prev, temperature) * time_step
    return radius


def static_rx(rho_m, rho_def, n_rx_prev, r_g_prev, D_def, temperature, time_step, r_rx_prev):
#    print("inside function call of static")
    rx_critical = mat_const.calc_austenite_gb_energy(temperature) / (calc_driving_force(rho_m, temperature) + 1)
#    print("rx_critical: ", rx_critical)
#    print("rx_prev: ", r_rx_prev)
    '''check for nucleation possible or not'''
    if rx_critical > r_rx_prev:
        d_nrx_dt = 0.0
        d_nrx = 0
        # r_rx = rx_critical
    else:
        # n_rx = n_rx_prev + d_nrx
        pre_exp_factor = inputdata.C0 * calc_driving_force(rho_m, temperature) / (4 * math.pi * math.pow(rx_critical, 2)
                                                                                  * D_def)
        exp_factor = math.exp(-inputdata.activation_energy_static_rx / (inputdata.uni_gas_const * temperature))
        d_nrx_dt = pre_exp_factor * exp_factor
        d_nrx = d_nrx_dt * time_step
#    print(d_nrx_dt)

    n_rx = n_rx_prev + d_nrx
    r_rx = (r_g_prev * n_rx_prev + d_nrx * calc_critical_radius_rx_grain(rho_m, temperature)) / n_rx #\
#        if rx_critical < r_rx_prev else rx_critical
    r_g_curr = r_rx + calc_radius_growth(rho_m, temperature, time_step)
    x_curr = 4 / 3 * math.pi * math.pow(r_g_curr, 3) * n_rx
#    print('xcurr : ', x_curr)
#    print("driving force :", calc_driving_force(rho_m, temperature))
#    print('nrx_prev: ', n_rx_prev, 'n_Rx : ', n_rx)
#    print("r_g_curr : ", r_g_curr)

    return_dict = {'driving_force': calc_driving_force(rho_m, temperature),
                   'r_critical': rx_critical,
                   'r_rx_prev_critical': r_rx_prev - rx_critical,
                   'r_rx': r_rx,
                   'd_nrx_dt': d_nrx_dt,
                   'd_nrx': d_nrx,
                   'N_rx': n_rx,
                   'r_g_curr': r_g_curr,
                   'x_curr': x_curr,
                   'd_mean': r_g_curr*x_curr + (1 - x_curr) * (D_def / 2),
                   'rho_m': rho_def * (1-x_curr) + x_curr * rho_full_rx,
                   'D_def': D_def,
                   'rho_def': rho_def}
    return return_dict
