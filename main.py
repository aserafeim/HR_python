from deformation import dislocation_density_calc, strain_calc
import matplotlib.pyplot as plt
import copy
import openpyxl
import sys
import static_recrystallisation
import inputdata
import material_constants as mat_const
import dynamic_recrystallisation as drx
import math
import time
from plotting import plot_func

print('sys.path=', sys.path)
location = r'\\juno\homes\user\aserafeim\Desktop\DL\HR_python-changed_structure\HR_python-changed_structure\Test_srx.xlsx'
wb = openpyxl.load_workbook(location)
sheet_curr = wb['Static_RX']
max_col = sheet_curr.max_column
max_row = sheet_curr.max_row
main_dict = {}

'''reading excel file'''
for i in range(3, max_row + 1):
    temp_dict = {}
    temp_dict['time_increment'] = sheet_curr.cell(i, 2).value
    temp_dict['initial_strain'] = sheet_curr.cell(i, 3).value
    temp_dict['final_strain'] = sheet_curr.cell(i, 4).value
    temp_dict['initial_strain_rate'] = sheet_curr.cell(i, 5).value
    temp_dict['final_strain_rate'] = sheet_curr.cell(i, 6).value
    temp_dict['initial_temp'] = sheet_curr.cell(i, 7).value + 273.15
    temp_dict['final_temp'] = sheet_curr.cell(i, 8).value + 273.15
    temp_dict['rho_0'] = sheet_curr.cell(i, 9).value if (isinstance(sheet_curr.cell(i, 9).value, int) or
                                                         isinstance(sheet_curr.cell(i, 9).value, float)) else 0.0
    temp_dict['pass_interval'] = sheet_curr.cell(i, 10).value
    temp_dict['temp_rate_of_change'] = (temp_dict['final_temp'] - temp_dict['initial_temp'])/temp_dict['pass_interval']
    ''
    if temp_dict['initial_strain_rate'] != 0.0:
        temp_dict['reference'] = 'deformation'
    else:
        temp_dict['reference'] = 'interpass'
    main_dict[i - 2] = temp_dict
for key, items in main_dict.items():
    print(key, ':', items, '\n')

print('"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')

'start of processing of each pass'
counter = 0
start = time.time()

'storage dictionary for storing values of the working dictionary which will be ' \
'updated at the end to the variable pass dictionary'

storage_dict = {'strain': [],
                'temperature': [],
                'time': [],
                'rho_def': [],
                'global_time' : [],
                'r_rx_prev_critical': [],
                'r_xc': [],
                'r_rx': [],
                'r_g_curr': [],
                'n_rx': [],
                'd_nrx_dt': [],
                'x_curr': [],
                'stress': [],
                'driving_force': [],
                'x_c_curr': [],
                'd_mean': [],
                'drg_dt': [],
                'n_d': [],
                'rho_m': [],
                'rho_critical': [],
                'd_nrx': [],
                'rho_rxed': [],
                'r_critical': [],
                'D_def': []
}
'''running of loops for passes'''

for i in range(1, max_row - 1):
    ''' initialisation of variables '''
    variable_pass = main_dict[i]
    print(i)

    time_step = variable_pass['time_increment']
    strain_initial = variable_pass['initial_strain']
    pass_interval = variable_pass['pass_interval']
    time_curr = time_step
    strain_rate_initial = variable_pass['initial_strain_rate']
    strain_rate_temp = strain_rate_initial

    '''1st step and if deformation'''
    if i == 1:
        storage_dict['rho_def'].append(variable_pass['rho_0'])
        storage_dict['n_rx'].append(0.0)
        storage_dict['r_g_curr'].append(0.0)
        storage_dict['x_curr'].append(0.0)
        storage_dict['x_c_curr'].append(0.0)
        storage_dict['r_rx'].append(0.0)
        storage_dict['d_mean'].append(inputdata.grain_size_init)
        storage_dict['D_def'].append(inputdata.grain_size_init)
        storage_dict['global_time'].append(time_curr)

    ''' last_time used for real time calculation and global time calculation'''
    if i > 1:
        last_time = main_dict[i - 1]['global_time'][-1]

    storage_dict['temperature'].append(variable_pass['initial_temp'])
    storage_dict['strain'].append(strain_initial)

    '''checks if strain rate is 0 or not, i.e deformation or static RX'''
    if strain_rate_initial > 0:
        'sub-routine counter variable'
        j = 0
        # k = 0
        while time_curr <= pass_interval:
#            print(j)
            storage_dict['strain'].append(strain_calc(storage_dict['strain'][j], time_step, strain_rate_initial))
            storage_dict['temperature'].append(storage_dict['temperature'][j] +
                                               variable_pass['temp_rate_of_change'] * time_step)

            'calculation of rho critical'
            n_z = 0.1 if strain_rate_temp > 1 else 1
            gb_energy = mat_const.calc_austenite_gb_energy(storage_dict['temperature'][j])
            M_g = mat_const.calc_gb_mobility2_drx(storage_dict['temperature'][j])
            '''check if dmean of something else'''
            D_def = storage_dict['d_mean'][0] * math.exp(-2 *0 / math.sqrt(3)) #storage_dict['strain'][j] 

            'Call to the deformation module'
            storage_dict['rho_def'].append(dislocation_density_calc(storage_dict['rho_def'][j], time_step,
                                                                    storage_dict['temperature'][j], strain_rate_initial,
                                                                    D_def))
            'Adding values to the lists of temp, strain and dislocation_density'
            storage_dict['time'].append(time_curr)
            if i == 1:
                storage_dict['global_time'].append(time_curr)
            else:
                storage_dict['global_time'].append(last_time + time_curr)

            "calculation of rho critical = dislocation density which decides if DRX occurs"
            part1 = (16 * mat_const.calc_austenite_gb_energy(storage_dict['temperature'][j]) *
                     math.pow(strain_rate_temp, n_z) * inputdata.M) \
                     /(3 * mat_const.calc_burgers_vector(storage_dict['temperature'][j]) *
                       mat_const.calc_gb_mobility2_drx(storage_dict['temperature'][j]) *
                       math.pow(mat_const.calc_dislocation_line_energy(storage_dict['temperature'][j]), 2))

            part2 = (inputdata.fitting_params['C_1'] / D_def) + (
                        inputdata.fitting_params['C_2'] * math.sqrt(inputdata.rho_const))

            storage_dict['rho_critical'].append(math.pow(part1 * part2, 1 / 3))
            rho_temp_var = 0.0
            dyn_rx_dict = {'r_xc':  0.0,
                           'n_d': 0.0,
                           'x_curr': 0.0,
                           'd_nrx_dt': 0.0,
                           'n_rx': 0.0,
                           'r_rx': 0.0,
                           'drg_dt': 0.0,
                           'r_g_curr': 0.0,
                           'rho_rxed': 0.0,
                           'd_mean': 0.0,
                           'rho_m': 0.0,
                           'd_nrx': 0.0,
                           'x_c_curr': 0.0}
            'checking for dynamic recrystallisation'
            if storage_dict['rho_def'][j] > storage_dict['rho_critical'][j]:
#                print("inside drx")
                # k = 0
#                print(len(storage_dict['n_rx']), len(storage_dict['r_rx']), " and ", j)
                dyn_rx_dict = drx.dynamic_rx(storage_dict['rho_critical'][j], storage_dict['rho_def'][j],
                                             storage_dict['n_rx'][j], storage_dict['r_rx'][j],
                                             storage_dict['r_g_curr'][j],
                                             storage_dict['x_curr'][j], storage_dict['x_c_curr'][j], time_step,
                                             storage_dict['temperature'][j], strain_rate_temp,
                                             storage_dict['strain'][j], D_def)

            'appending values to the lists'
            storage_dict['r_xc'].append(dyn_rx_dict['r_xc'])
            storage_dict['x_curr'].append(dyn_rx_dict['x_curr'])
            storage_dict['rho_m'].append(dyn_rx_dict['rho_m'])
            storage_dict['r_rx'].append(dyn_rx_dict['r_rx'])
            storage_dict['r_g_curr'].append(dyn_rx_dict['r_g_curr'])
            storage_dict['d_nrx_dt'].append(dyn_rx_dict['d_nrx_dt'])
            storage_dict['n_rx'].append(dyn_rx_dict['n_rx'])
            storage_dict['d_mean'].append(dyn_rx_dict['d_mean'])
            storage_dict['x_c_curr'].append((dyn_rx_dict['x_c_curr']))
            storage_dict['drg_dt'].append(dyn_rx_dict['drg_dt'])
            storage_dict['rho_rxed'].append(dyn_rx_dict['rho_rxed'])
            storage_dict['n_d'].append(dyn_rx_dict['n_d'])
            storage_dict['D_def'].append(D_def)
            rho_temp_var = dyn_rx_dict['rho_m']

            if dyn_rx_dict['x_curr'] > 0.99:
                plot_func(storage_dict['time'], storage_dict['x_curr'], 'Time', 'drx_xcurr', True, False,
                              variable_pass)
                break

            'calculation of stress'
            storage_dict['stress'].append(mat_const.calc_stress(storage_dict['temperature'][j], strain_rate_temp,
                                                                rho_temp_var))

            'Updating variables for next iteration of the sub-routine'
            time_curr += time_step
            j += 1
    else:
#        print('inside static rx')
        j = 0
        'Static recrystallisation module'
        while time_curr <= pass_interval:
            'calculation of strain and temperature'
            storage_dict['strain'].append(strain_calc(storage_dict['strain'][j], time_step, strain_rate_initial))
            storage_dict['temperature'].append(storage_dict['temperature'][j] +
                                               variable_pass['temp_rate_of_change'] * time_step)
            'call to static module'
#            print('j : ', j)
            # print(len(storage_dict['strain']))
#            print(storage_dict['d_mean'])
            D_def = storage_dict['d_mean'][0] * math.exp(-2 *0/ math.sqrt(3))# storage_dict['strain'][j] 

            temp_srx_dict = static_recrystallisation.static_rx(storage_dict['rho_m'][j], storage_dict['rho_def'][j],
                                                               storage_dict['n_rx'][j], storage_dict['r_g_curr'][j],
                                                               D_def, storage_dict['temperature'][j], time_step,
                                                               storage_dict['r_rx'][j])

            'adding values to the list, later used for plotting the graphs'
            storage_dict['time'].append(time_curr)
            storage_dict['d_mean'].append(temp_srx_dict['d_mean'])
            storage_dict['rho_m'].append(temp_srx_dict['rho_m'])
            storage_dict['n_rx'].append(temp_srx_dict['N_rx'])
            storage_dict['x_curr'].append(temp_srx_dict['x_curr'])
            storage_dict['d_nrx_dt'].append(temp_srx_dict['d_nrx_dt'])
            storage_dict['d_nrx'].append(temp_srx_dict['d_nrx'])
            storage_dict['r_g_curr'].append(temp_srx_dict['r_g_curr'])
            storage_dict['driving_force'].append(temp_srx_dict['driving_force'])
            storage_dict['r_rx'].append(temp_srx_dict['r_rx'])
            storage_dict['r_critical'].append(temp_srx_dict['r_critical'])
            storage_dict['r_rx_prev_critical'].append(temp_srx_dict['r_rx_prev_critical'])
            storage_dict['rho_def'].append(temp_srx_dict['rho_def'])
            storage_dict['D_def'].append(temp_srx_dict['D_def'])
            'Stress calculation'
#            print('rho_m:', temp_srx_dict['rho_m'])
            storage_dict['stress'].append(mat_const.calc_stress(storage_dict['temperature'][j], strain_rate_temp,
                                                                temp_srx_dict['rho_m']))
            'tracking real time'
            if i == 1:
                storage_dict['global_time'].append(time_curr)
            else:
                storage_dict['global_time'].append(last_time + time_curr)

            'updating values after every iteration'
            time_curr += time_step
            j += 1
    'keys and values of storage dict for each iteration is added to the variable pass, which contains the '
    for key in storage_dict:
        variable_pass[key] = storage_dict[key].copy()

    for value in storage_dict.values():
        del value[:]
#    print(storage_dict)

#    print(" ----------------- variable pass ----------------------")
#    for key, val in main_dict[i].items():
#        print(key, ':', val) if type(val) != list else print(key, ':', len(val))
#    print("---------------------------------------------------------")

    if i < max_row - 2:
        storage_dict['d_mean'].append(variable_pass['d_mean'][-1])
        'special conditions if deformation -> interpass and is the first step'
        if variable_pass['reference'] == 'deformation' and main_dict[i+1]['reference'] == 'interpass':

            storage_dict['rho_m'].append(variable_pass['rho_m'][-1])
            storage_dict['rho_def'].append(variable_pass['rho_def'][-1])
            storage_dict['r_rx'].append(0.5 * variable_pass['d_mean'][-1])
            storage_dict['n_rx'].append(variable_pass['n_rx'][-1])
            storage_dict['D_def'].append(variable_pass['D_def'][-1])
            storage_dict['r_critical'].append(0.0)
            storage_dict['x_curr'].append(0.0)
            storage_dict['r_g_curr'].append(variable_pass['r_g_curr'][-1])
#            print(storage_dict)
            print("******************************************")

        'interpass to interpass'
        if variable_pass['reference'] == 'interpass' and main_dict[i+1]['reference'] == 'interpass':
            storage_dict['rho_m'].append(main_dict[i]['rho_m'][-1])
            storage_dict['rho_def'].append(main_dict[i]['rho_def'][-1])
            storage_dict['r_rx'].append(0.5 * main_dict[i]['d_mean'][-1])
            storage_dict['n_rx'].append(main_dict[i]['n_rx'][-1])
            storage_dict['D_def'].append(main_dict[i]['D_def'][-1])
            storage_dict['r_critical'].append(0.0)
            storage_dict['r_g_curr'].append(main_dict[i]['r_g_curr'][-1])
#            print(storage_dict)

        'interpass to deformation'
        if variable_pass['reference'] == 'interpass' and main_dict[i+1]['reference'] == 'deformation':
            storage_dict['n_rx'].append(0.0)
            storage_dict['r_rx'].append(0.0)
            storage_dict['r_g_curr'].append(0.0)
            storage_dict['x_curr'].append(0.0)
            storage_dict['x_c_curr'].append(0.0)
            storage_dict['rho_def'].append(main_dict[i]['rho_def'][-1])
            storage_dict['rho_m'].append(main_dict[i]['rho_m'][-1])
            storage_dict['D_def'].append(0.0)
#            print(storage_dict)


# print(nuclei)
# plt.xlim(0,100)
# plt.ylim(0,1)
# print(max(stress_list))
# =============================================================================
# plt.plot(d_timelist, drx_xcurr_list, 'r')
# #plt.plot(d_timelist, dislocation_list, 'b')
# plt.xscale('log')
# plt.grid(True,which="both", linestyle='--')
# plt.xlabel('time')
# plt.ylabel('rho')
# plt.title('rho vs time')
#
# plt.show()
# =============================================================================
# plot_func(d_timelist, dislocation_list, 'Time', 'rho_list', True, False, main_dict)
end = time.time()
print('Time elapsed', end - start)
