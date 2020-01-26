# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 13:46:48 2020

@author: sroy
"""
import material_constants as mat_const
import inputdata
import math
import deformation

def dynamic_rx(rho_critical, rho_curr, n_rx_prev, r_rx_prev, r_g_prev,x_prev, x_c_prev, time_step, temp_curr, temp_strain_rate, temp_strain):
    return_dict = {}
    D_t = inputdata.grain_size_init * math.exp(-2*temp_strain/math.sqrt(3))
    mean_free_path_dis_cr = 1/((inputdata.fitting_params['C_1']/D_t) + inputdata.fitting_params['C_2']*math.sqrt(rho_critical))
    mean_free_path_dis = 1/((inputdata.fitting_params['C_1']/D_t) + inputdata.fitting_params['C_2']*math.sqrt(rho_curr))
    
    'Calculation of R_xc'
    subpart1 = (3*mat_const.calc_burgers_vector(temp_curr)*mat_const.calc_gb_mobility2_drx(temp_curr)*mat_const.calc_dislocation_line_energy(temp_curr)) / (4 * inputdata.M * inputdata.fitting_params['C_10'])
# =============================================================================
#     #part2 = (inputdata.fitting_params['C_1'] / D_t) + (inputdata.fitting_params['C_2'] * math.sqrt(inputdata.rho_const))
#     #part = (inputdata.fitting_params['C_1'] / D_t) + (inputdata.fitting_params['C_2'] * math.sqrt(rho_critical))
#     #subpart2 = math.pow(rho_critical,2) * mean_free_path_dis
#     #r_xc = subpart1*subpart2
# =============================================================================
    r_xc = subpart1 * math.pow(rho_critical, 2) * mean_free_path_dis_cr
    # r_xc = critical radius of newly formed nuclei
    'calculation of nd'
   
    # =c1/K(t)+c2* root of rho_cr
    n_d = math.pi*math.pow(r_xc, 2)/ mean_free_path_dis_cr ** 2
    
    'calculation of nucleation rate and total number of grains'
    p_r = math.exp(-281000/(inputdata.uni_gas_const * temp_curr))
    kf = 0.4e6
    nucleation_rate = kf * temp_strain_rate* p_r * (1 - x_prev)/(n_d * D_t * mat_const.calc_burgers_vector(temp_curr) * mean_free_path_dis)
    dn_rx = nucleation_rate * time_step
    n_rx = n_rx_prev + dn_rx
    
    'calculate radius of recrystallised grains depending on whether number of recrystallised grains >=0 or not'
    r_rx = (n_rx_prev*r_g_prev + dn_rx*r_xc)/ n_rx if n_rx != 0 else 0
    r_rx_method2 = math.pow((n_rx_prev* r_g_prev**3 + dn_rx* r_xc**3)/ n_rx, 1/3) if n_rx != 0 else 0
    
    'calculation of recrystallisation fraction'
    x_curr = (4/3) * math.pi * math.pow(r_rx,3) * n_rx
    
    'radius growth of the newly rxed grains'
    x_c_curr = x_c_prev
    #s = 0 if x_c_curr==0 else 1
    if round(x_c_curr, 7) == 0:
        s = 0
        x_c_curr = x_curr
    else:
        s = 1 
   #print('x_c_curr',x_c_curr, 'and x_curr is ', x_curr)
    #temp_var_1 = 0 if x_c_curr > x_curr else (x_curr - x_c_curr)
    psi = 1 - s* math.pow((x_curr - x_c_curr)/(1 - x_c_curr),inputdata.n_x)

    # growth rate of the radius
    
    drg_dt = rho_curr * psi * mat_const.calc_dislocation_line_energy(temp_curr) * mat_const.calc_gb_mobility2_drx(temp_curr)
    dr_g = drg_dt * time_step if round(n_rx,7) != 0 else 0#rate of growt of the newly formed grain
    r_g_curr = r_rx + dr_g
    
    'calculation of rxed dislocation density'
    #math.pow(mat_const.calc_gb_mobility(temp_curr), 0.98)
    fragment1 = (inputdata.fitting_params['C_1'] / D_t) + (inputdata.fitting_params['C_2'] * math.sqrt(rho_curr))
    fragment2 = r_rx/(mat_const.calc_burgers_vector(temp_curr)*mat_const.calc_dislocation_line_energy(temp_curr)*rho_curr)
    if temp_strain_rate > 1:
        rho_rxed = 0.005 * math.pow(temp_strain_rate, 0.176) * inputdata.M * fragment1 * (fragment2/math.pow(mat_const.calc_gb_mobility2_drx(temp_curr), 0.98))
    else:
        rho_rxed = 0.85 * math.pow(temp_strain_rate, 0.2) * inputdata.M * fragment1 * (fragment2/math.pow(mat_const.calc_gb_mobility2_drx(temp_curr), 0.97))
    
    'calculation of mean grain size'
    d_mean = 2*r_g_curr * x_curr + (1-x_curr)*inputdata.grain_size_init
    
    'calculation of mean dislocation density'
    rho_m = rho_curr*(1-x_curr) + rho_rxed*x_curr
#    print('rho_m:', rho_m, 'for x_curr:', x_curr)
    
    return_dict['r_xc'] = r_xc
    return_dict['n_d']=n_d
    return_dict['x_curr'] = x_curr
    return_dict['nucleation_rate'] = nucleation_rate
    return_dict['n_rx']=n_rx
    return_dict['r_rx']=r_rx
    return_dict['drgdt'] = drg_dt
    return_dict['r_g_curr']=r_g_curr
    return_dict['rho_rxed']=rho_rxed
    return_dict['d_mean']=d_mean
    return_dict['rho_m']=rho_m
    return_dict['dnrx'] = dn_rx
    return_dict['x_c_curr']=x_c_curr
    return return_dict
    
    