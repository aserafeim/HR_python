# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:46:48 2020

@author: sroy
"""
import material_constants as mat_const
import inputdata
import math


def dynamic_rx(rho_critical, rho_curr, n_rx_prev,
               r_g_prev, x_prev, x_c_prev, time_step, temp_curr,
               temp_strain_rate, D_def, c1, c2, c10, m):

    mean_free_path_dis_cr = 1/((c1 / D_def) + c2 * math.sqrt(rho_critical))
    mean_free_path_dis = 1/((c1 / D_def) + c2 * math.sqrt(rho_curr))
    
    'Calculation of R_xc'
    subpart1 = (3 * mat_const.calc_burgers_vector(temp_curr)*mat_const.calc_gb_mobility2_drx(temp_curr)*
                mat_const.calc_dislocation_line_energy(temp_curr)) / (4 * m * c10)

    r_xc = subpart1 * math.pow(rho_critical, 2) * mean_free_path_dis_cr

    'calculation of nd'
    n_d = math.pi * math.pow(r_xc, 2) / mean_free_path_dis_cr ** 2
    
    'calculation of nucleation rate and total number of grains'
    p_r = math.exp(-281000/(inputdata.uni_gas_const * temp_curr))
    kf = 0.4e6
    nucleation_rate = kf * temp_strain_rate* p_r * (1 - x_prev)/(n_d * D_def * mat_const.calc_burgers_vector(temp_curr) *
                                                                 mean_free_path_dis)
    d_nrx = nucleation_rate * time_step
    n_rx = n_rx_prev + d_nrx
    
    'calculate radius of recrystallised grains depending on whether number of recrystallised grains >=0 or not'
    r_rx = (n_rx_prev * r_g_prev + d_nrx*r_xc) / n_rx if n_rx != 0 else 0
    
    'calculation of recrystallisation fraction'
    x_curr = (4/3) * math.pi * math.pow(r_rx,3) * n_rx
    
    'radius growth of the newly rxed grains'
    x_c_curr = x_c_prev
    if round(x_c_curr, 7) == 0:
        s = 0
        x_c_curr = x_curr
    else:
        s = 1
    psi = 1 - s * math.pow((x_curr - x_c_curr)/(1 - x_c_curr), inputdata.n_x)

    'rate of growth of the newly formed grains, i.e. dr_g'
    drg_dt = rho_curr * psi * mat_const.calc_dislocation_line_energy(temp_curr) * mat_const.calc_gb_mobility2_drx(temp_curr)
    dr_g = drg_dt * time_step if round(n_rx, 7) != 0 else 0
    r_g_curr = r_rx + dr_g
    
    'calculation of rxed dislocation density'
    fragment1 = (c1 / D_def) + (c2 * math.sqrt(rho_curr))
    fragment2 = r_rx/(mat_const.calc_burgers_vector(temp_curr)*mat_const.calc_dislocation_line_energy(temp_curr)*rho_curr)
    if temp_strain_rate > 1:
        rho_rxed = 0.005 * math.pow(temp_strain_rate, 0.176) * inputdata.M * fragment1 * \
                   (fragment2/math.pow(mat_const.calc_gb_mobility2_drx(temp_curr), 0.98))
    else:
        rho_rxed = 0.85 * math.pow(temp_strain_rate, 0.2) * inputdata.M * fragment1 * \
                   (fragment2/math.pow(mat_const.calc_gb_mobility2_drx(temp_curr), 0.97))
    
    'calculation of mean grain size'
    d_mean = 2 * r_g_curr * x_curr + (1-x_curr)*inputdata.grain_size_init
    
    'calculation of mean dislocation density'
    # rho_m = rho_curr*(1-x_curr) + rho_rxed*x_curr if not first_from_interpass else rho_curr
    rho_m = rho_curr * (1 - x_curr) + rho_rxed * x_curr
    'where rho_curr has the same value as rho_m when coming from an interpass'
    
    return_dict = {'r_xc':  r_xc,
                   'n_d': n_d,
                   'x_curr': x_curr,
                   'd_nrx_dt': nucleation_rate,
                   'n_rx': n_rx,
                   'r_rx': r_rx,
                   'drg_dt': drg_dt,
                   'r_g_curr': r_g_curr,
                   'rho_rxed': rho_rxed,
                   'd_mean': d_mean,
                   'rho_m': rho_m,
                   'd_nrx': d_nrx,
                   'x_c_curr': x_c_curr,
                   'D_def': D_def}

    return return_dict
