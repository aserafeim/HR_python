import material_constants as mat_const
import math
import inputdata

rho_full_rx = 1e11


def calc_driving_force(rho_prev, temperature):
    '''for austenite dislocation density of a fully recrystallised grain is 1e11'''
    driving_force = mat_const.calc_dislocation_line_energy(temperature) * (rho_prev - rho_full_rx)
    return driving_force


def calc_critical_radius_rx_grain(rho_prev, temperature):
    '''this is the critical radius of the RX-ed grain, i.e.
     the radius with which the rx_ed nucleus becomes stable as a grain'''
    return mat_const.calc_austenite_gb_energy(temperature) / (calc_driving_force(rho_prev, temperature) + 1)


def calc_radius_growth(rho_prev, temperature):
    drgdt = mat_const.calc_gb_mobility(temperature) * calc_driving_force(rho_prev, temperature)
    return drgdt


def static_rx(rho_m, rho_def, n_rx_prev, r_g_prev, D_def, temperature, dt, r_rx_prev):

    if rho_def > rho_full_rx:
        driving_force = calc_driving_force(rho_m, temperature)
    else:
        driving_force = 0.0
    'calculation of critical radius'
    r_xc = mat_const.calc_austenite_gb_energy(temperature) / (driving_force + 1)
    '''check for nucleation possible or not'''
    if r_xc > r_rx_prev:
        d_nrx_dt = 0.0
        # d_nrx = 0
        # r_rx = r_xc
    else:
        pre_exp_factor = inputdata.C0 * driving_force / (4 * math.pi * math.pow(r_xc, 2) * D_def)
        exp_factor = math.exp(-inputdata.activation_energy_static_rx / (inputdata.uni_gas_const * temperature))
        d_nrx_dt = pre_exp_factor * exp_factor
    d_nrx = d_nrx_dt * dt
    n_rx = n_rx_prev + d_nrx_dt * dt
    'mean rxed grain size'
    r_rx = (r_g_prev * n_rx_prev + d_nrx * r_xc) / n_rx
    'growth contribution'
    drg_dt = mat_const.calc_gb_mobility(temperature) * driving_force
    r_g_curr = r_rx + drg_dt * dt
    x_curr = (4/3) * math.pi * math.pow(r_g_curr, 3) * n_rx

    return_dict = {'driving_force': driving_force,
                   'r_critical': r_xc,
                   'r_rx_prev_critical': r_rx_prev - r_xc,
                   'r_rx': r_rx,
                   'd_nrx_dt': d_nrx_dt,
                   'd_nrx': d_nrx,
                   'n_rx': n_rx,
                   'drg_dt': drg_dt,
                   'r_g_curr': r_g_curr,
                   'x_curr': x_curr,
                   'd_mean': (r_g_curr * x_curr + (1 - x_curr) * (D_def / 2))*2,
                   'rho_m': rho_def * (1-x_curr) + x_curr * rho_full_rx,
                   'D_def': D_def,
                   'rho_def': rho_def}
    return return_dict
