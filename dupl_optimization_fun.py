from deformation import *
import dynamic_recrystallisation as drx
import material_constants as mat_const
import numpy as np
from main_opt import find_target_stress, read_parameters_file
# from main import read_parameters_file
import inputdata
from inputdata import fitting_params as fp


def error_fun(x_exp, x_sim):
    error = 0
    for i in range(len(x_exp)):
        error += (x_exp[i] - (x_sim[i]/math.pow(10, 6))) / x_exp[i]
    error_final = error / len(x_exp)
    return error_final


def optimize_second(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10):
    '''r_rx_prev, r_g_prev and the rest of the variables should not be used in this function,
    only the c values will be input'''
    temp_list = [950]
    strain_rate_list = [0.1]
    de = 0.001
    final_strain = 0.8
    i, j, k = 0, 0, 0
    inc = 0.05
    stress_list_model = []
    target_strains = []
    stress_target = []
    error_arr = []
    imported_dict = read_parameters_file()
    working_dict = imported_dict[5]
    upper_limit = int(final_strain / de)
    for k in range(0, 10):
        target_strains.append(k * inc)
    for temperature in temp_list:
        i += i
        # i += 1

        for strain_rate in strain_rate_list:
            j += j
            # j += 1
            rho = working_dict['rho_0']
            time_step = working_dict['time_increment']
            D_def = inputdata.grain_size_init
            r_rx_prev = 0.0
            r_g_prev = 0.0
            n_rx_prev = 0.0
            x_prev = 0.0
            x_c_prev = 0.0
            m = inputdata.M
            strain = 0.0
            'to initialise with a non-zero value for running the simulation'
            rho = 1E+11
            # for strain in range(0.0, final_strain, 0.001):
            while strain <= final_strain:
                rho_def = calc_deformation_dislocation(rho, time_step, temperature, strain_rate, D_def, c1, c2, c3, c4,
                                                       c5, c6, c7, c8, c9, c10, m)
                'calculation of critical dislocation density'
                flag = False
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
                    temp_variable = drx.dynamic_rx(rho_critical, rho_def, n_rx_prev,
                                                   r_rx_prev, r_g_prev, x_prev, x_c_prev, time_step, temperature,
                                                   strain_rate, strain, D_def, c1, c2, c10, m)
                    rho_m = temp_variable['rho_m']
                    flag = True

                stress_curr = mat_const.calculate_stress(temperature, strain_rate, rho_m, c7, c8, c9, m)
                # print("stress curr: ", stress_curr, " and strain curr:", strain)
                stress_list_model.append(stress_curr)
                'separate stress on a separate list (stress_target) when target strain is reached'
                for x in target_strains:
                    if round(strain, 2) == round(x, 2):
                        stress_target.append(stress_curr)
                'Updating values at the end of each subroutine'
                if flag:
                    n_rx_prev = temp_variable['n_rx']
                    r_rx_prev = temp_variable['r_rx']
                    x_prev = temp_variable['x_curr']
                    x_c_prev = temp_variable['x_c_curr']
                    r_g_prev = temp_variable['r_g_curr']
                rho = rho_m

                strain += 0.001
            'fetch experimental data for target strains based on temperature and strain rate from dictionary'
            'to do and will give stress_list_exp'
            'error function calculation'
            stress_list_exp = find_target_stress(target_strains, temperature, strain_rate)
            loc_error = error_fun(stress_list_exp, stress_target)
            # error_array[i, j] = loc_error
            error_arr.append(loc_error)
    # error_final = np.sum(error_array) / np.size(error_array)
    error_final = np.sum(error_arr) / np.size(error_arr)
    return error_final


error_return = optimize_second(fp['C_1'], fp['C_2'], fp['C_3'], fp['C_4'], fp['C_5'], fp['C_6'], fp['C_7'], fp['C_8'],
                            fp['C_9'], fp['C_10'])
print(error_return)
