import math
import material_constants as material_constants
import inputdata as inputdata
# import numpy
from inputdata import fitting_params as fp


def strain_calc(strain_init, time_step, strain_rate):
    strain_current = strain_init + strain_rate * time_step

    return strain_current


def calc_deformation_dislocation(rho_prev, time_step, temperature,
                                 strain_rate_initial, D_def, n_rx_prev, r_g_prev, x_prev, x_c_prev,
                                 r_rx_prev, d_mean_prev):

    ''' calculation of all the A values using the constants c1, c2, c3, c4 ... to be further used for'
        'the dislocation density calculation after deformation '''
    # D_def = d_mean_prev * math.exp(-2 * 0 / math.sqrt(3))
    a0 = inputdata.M * strain_rate_initial / material_constants.calc_burgers_vector(temperature)
    a1 = fp['C_4'] * fp['C_5'] * inputdata.M * inputdata.alpha * math.pow(material_constants.calc_burgers_vector(temperature), 4) * material_constants.calc_shear_modulus(temperature) \
         / (inputdata.K_b * temperature)
    a2 = fp['C_4'] * fp['C_5'] * material_constants.calc_burgers_vector(temperature) * inputdata.M / fp['C_9']
    a3 = a0 / (fp['C_7'] * inputdata.nu_a)
    a4 = math.exp(fp['C_8'] * (
            material_constants.calc_shear_modulus(temperature) / (2 * inputdata.K_b * temperature)) \
                   * math.pow(material_constants.calc_burgers_vector(temperature), 3))
    a5 = a3 * a4
    subpart1 = a0 * fp['C_1'] / (3 * D_def)
    subpart2 = a0 * fp['C_2'] * math.sqrt(rho_prev)
    subpart3 = -3 * fp['C_3'] * a0 * material_constants.calc_burgers_vector(temperature) * rho_prev
    subpart4 = -5 * a1 * material_constants.calc_effective_diffusivity(temperature, rho_prev) * math.pow(rho_prev, 2.5)
    subpart5 = material_constants.calc_effective_diffusivity(temperature, rho_prev) * math.pow(rho_prev, 2.5) * a2 * math.asinh(a5 / math.sqrt(rho_prev))
    rho_def = (subpart1 + subpart2 + subpart3 + subpart4 + subpart5) * time_step + rho_prev

    'calculation of rho_critical'
    n_z = 0.1 if strain_rate_initial > 1 else 1
    gb_energy = material_constants.calc_austenite_gb_energy(temperature)
    M_g = material_constants.calc_gb_mobility2_drx(temperature)
    part1 = (16 * material_constants.calc_austenite_gb_energy(temperature) *
             math.pow(strain_rate_initial, n_z) * inputdata.M) \
            / (3 * material_constants.calc_burgers_vector(temperature) *
               material_constants.calc_gb_mobility2_drx(temperature) *
               math.pow(material_constants.calc_dislocation_line_energy(temperature), 2))

    part2 = (inputdata.fitting_params['C_1'] / D_def) + (
            inputdata.fitting_params['C_2'] * math.sqrt(inputdata.rho_const))

    # storage_dict['rho_critical'].append(math.pow(part1 * part2, 1 / 3))
    rho_critical = math.pow(part1*part2, (1/3))
    deformation_dict = {'D_def': D_def,
                        'rho_critical': rho_critical,
                        'rho_def': rho_def,
                        'r_xc': 0.0,
                        'n_d': 0.0,
                        'x_curr': x_prev,
                        'd_nrx_dt': 0.0,
                        'n_rx': n_rx_prev,
                        'r_rx': r_rx_prev,
                        'drg_dt': 0.0,
                        'r_g_curr': r_g_prev,
                        'rho_rxed': 0.0,
                        # 'd_mean': D_def/math.exp(-2 * 0 / math.sqrt(3)),
                        'd_mean': d_mean_prev,
                        'rho_m': rho_def,
                        'd_nrx': 0.0,
                        'x_c_curr': x_c_prev
                        }
    'going inside dynamic recrystallisation'
    if rho_def > rho_critical:
        mean_free_path_dis_cr = 1 / ((fp['C_1'] / D_def) + fp['C_2'] * math.sqrt(rho_critical))
        mean_free_path_dis = 1 / ((fp['C_1'] / D_def) + fp['C_2'] * math.sqrt(rho_def))

        'Calculation of R_xc'
        subpart1 = (3 * material_constants.calc_burgers_vector(temperature) * material_constants.calc_gb_mobility2_drx(
            temperature) *
                    material_constants.calc_dislocation_line_energy(temperature)) / (4 * inputdata.M * fp['C_10'])

        r_xc = subpart1 * math.pow(rho_critical, 2) * mean_free_path_dis_cr

        'calculation of nd'
        n_d = math.pi * math.pow(r_xc, 2) / mean_free_path_dis_cr ** 2

        'calculation of nucleation rate and total number of grains'
        p_r = math.exp(-281000 / (inputdata.uni_gas_const * temperature))
        kf = 0.4e6
        nucleation_rate = kf * strain_rate_initial * p_r * (1 - x_prev) / (
                n_d * D_def * material_constants.calc_burgers_vector(temperature) *
                mean_free_path_dis)
        d_nrx = nucleation_rate * time_step
        n_rx = n_rx_prev + d_nrx

        'calculate radius of recrystallised grains depending on whether number of recrystallised grains >=0 or not'
        r_rx = (n_rx_prev * r_g_prev + d_nrx * r_xc) / n_rx if n_rx != 0 else 0

        'calculation of recrystallisation fraction'
        x_curr = (4 / 3) * math.pi * math.pow(r_rx, 3) * n_rx

        'radius growth of the newly rxed grains'
        x_c_curr = x_c_prev
        if round(x_c_curr, 7) == 0:
            s = 0
            x_c_curr = x_curr
        else:
            s = 1
        psi = 1 - s * math.pow((x_curr - x_c_curr) / (1 - x_c_curr), inputdata.n_x)

        'rate of growth of the newly formed grains, i.e. dr_g'
        drg_dt = rho_def * psi * material_constants.calc_dislocation_line_energy(
            temperature) * material_constants.calc_gb_mobility2_drx(
            temperature)
        dr_g = drg_dt * time_step if round(n_rx, 7) != 0 else 0
        r_g_curr = r_rx + dr_g

        'calculation of rxed dislocation density'
        fragment1 = (fp['C_1'] / D_def) + (fp['C_2'] * math.sqrt(rho_def))
        fragment2 = r_rx / (
                material_constants.calc_burgers_vector(temperature) * material_constants.calc_dislocation_line_energy(
            temperature) * rho_def)
        if strain_rate_initial > 1:
            rho_rxed = 0.005 * math.pow(strain_rate_initial, 0.176) * inputdata.M * fragment1 * \
                       (fragment2 / math.pow(material_constants.calc_gb_mobility2_drx(temperature), 0.98))
        else:
            rho_rxed = 0.85 * math.pow(strain_rate_initial, 0.2) * inputdata.M * fragment1 * \
                       (fragment2 / math.pow(material_constants.calc_gb_mobility2_drx(temperature), 0.97))

        'calculation of mean grain size'
        d_mean = 2 * r_g_curr * x_curr + (1 - x_curr) * inputdata.d0

        'calculation of mean dislocation density'
        # rho_m = rho_curr*(1-x_curr) + rho_rxed*x_curr if not first_from_interpass else rho_curr
        rho_m = rho_def * (1 - x_curr) + rho_rxed * x_curr
        'where rho_def has the same value as rho_m when coming from an interpass'

        return_dict = {'r_xc': r_xc,
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
        for key, value in return_dict.items():
            if key in deformation_dict:
                deformation_dict[key] = value

    return deformation_dict