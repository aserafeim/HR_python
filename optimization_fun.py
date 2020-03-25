from deformation import *
import dynamic_recrystallisation as drx
import material_constants as mat_const
import numpy as np
#
#
# def optimize(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, temperature, stress_exp, strain_list, rho_def_list, strain_rate, time_step, D_def, m):
#    'strain list has the strains at which the subroutine runs for the deformation and dynamic recrystallisation'
#    for i in len(0, strain_list):
#         'call to the deformation module'
#         rho_def = calc_deformation_dislocation(rho_def_list[i], time_step, temperature, strain_rate, D_def, c1, c2,c3, c4, c5, c6, c7,c8, c9, c10, m)
#
#         "calculation of rho critical = critical dislocation density which decides if DRX occurs"
#         n_z = 0.1 if strain_rate > 1 else 1
#         part1 = (16 * mat_const.calc_austenite_gb_energy(temperature) *
#                      math.pow(strain_rate, n_z) * m) \
#                      /(3 * mat_const.calc_burgers_vector(temperature) *
#                        mat_const.calc_gb_mobility2_drx(temperature) *
#                        math.pow(mat_const.calc_dislocation_line_energy(temperature), 2))
#
#         part2 = (inputdata.fitting_params['C_1'] / D_def) + (
#                         inputdata.fitting_params['C_2'] * math.sqrt(inputdata.rho_const))
#         rho_critical = math.pow(part1 * part2, 1 / 3)
def error_fun(x_exp,x_sim):
      error=0
      for i in range(len(x_exp)):
                error += (x_exp[i] - x_sim[i]) / x_exp[i]    
      error_final = error/len(x_exp)
      return error_final

def optimize_second(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, temperature, stress_list_exp, strain_list_exp, rho, strain_rate, time_step, D_def, m, rho_curr, n_rx_prev,
                    r_rx_prev, r_g_prev, x_prev, x_c_prev):
    'r_rx_prev, r_g_prev and the rest of the variables should not be used in this function, only the c values will be input'
    temp_list=[900]
    strain_rate_list=[0.1]
    de=0.001
    final_strain=0.8
    i,j,k=0
    inc=0.05
    stress_list_model = []
    target_strains=[]
    for k in range(0,10):
        target_strains.append(k*inc)
    for temperature in temp_list:
        i=+i
        for strain_rate in strain_rate_list:
            j=+j
            for strain in range(0,final_strain/de):
                rho_def = calc_deformation_dislocation(rho, time_step, temperature, strain_rate, D_def, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, m)
                'calculation of critical dislocation density'
                n_z = 0.1 if strain_rate > 1 else 1
                part1 = (16 * mat_const.calc_austenite_gb_energy(temperature) *
                         math.pow(strain_rate, n_z) * m) \
                        / (3 * mat_const.calc_burgers_vector(temperature) *
                           mat_const.calc_gb_mobility2_drx(temperature) *
                           math.pow(mat_const.calc_dislocation_line_energy(temperature), 2))
        
                part2 = (c1 / D_def) + (c2 * math.sqrt(inputdata.rho_const))
                rho_critical = math.pow(part1 * part2, 1 / 3)
                rho_m = rho_def
        
                if rho_def > rho_critical:
                    temp_variable = drx.dynamic_rx(rho_critical, rho_curr, n_rx_prev,
                       r_rx_prev, r_g_prev, x_prev, x_c_prev, time_step, temperature,
                       strain_rate, strain, D_def, c1, c2, c10, m)
                    rho_m = temp_variable['rho_m']
        
                stress_curr = mat_const.calculate_stress(temperature, strain_rate, rho_m, c7, c8, c9, m)
                stress_list_model.append(stress_curr)
                'separate stress on a separate list (stress_target) when target strain is reached'
                
            'fetch experimental data for target strains based on temperature and strain rate from dictionary'    
            'to do and will give stress_list_exp'
            'error function calculation'
            loc_error=error_fun(stress_list_exp,stress_target)
            error_array[i,j]=loc_error
            
    error_final=np.sum(error_array)/np.size(error_array)
    return error_final


