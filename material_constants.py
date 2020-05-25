import inputdata as inputdata
import math
import numpy
import deformation
from inputdata import fitting_params as fp


def calc_unit_cell_length(temperature):
    return (0.35519 + 8.1593e-6 * temperature + 1.7341e-3 * inputdata.chem_comp['w_C']) * 1.0e-9


def calc_burgers_vector(temperature):
    'Burgers vector in m'
    return calc_unit_cell_length(temperature) / math.sqrt(2.0)


def calc_shear_modulus(temperature):
    g_t = inputdata.shear_mod_G0 * (1.0 - 0.91 * (temperature - 300.0) / inputdata.melting_temp_TmG)
    return g_t


def calc_dislocation_line_energy(temperature):
    return (calc_shear_modulus(temperature) * math.pow(calc_burgers_vector(temperature), 2)) / 2


def calc_melting_temp_for_diffusion(temperature):
    t_mD = 1804.44 - 134.15 * inputdata.chem_comp['w_C'] - 1.85 * inputdata.chem_comp['w_Mn'] - \
           24.08 * inputdata.chem_comp['w_Si']
    return t_mD


def calc_self_diffusivity(temperature):
    d_self = 6.89e-6 * numpy.exp(- 17.0 * calc_melting_temp_for_diffusion(temperature) / temperature)
    return d_self


def calc_gb_diffusivity(temperature):
    d_gb = 1.0e-3 * numpy.exp(- 11.0 * calc_melting_temp_for_diffusion(temperature) / temperature)
    return d_gb


def calc_vol_dislocation(temperature, rho_last):
    vol_d = 3.1416 * calc_burgers_vector(temperature) ** 2 * rho_last
    return vol_d


def calc_effective_diffusivity(temperature, rho_last):
    d_eff = (1.0 - calc_vol_dislocation(temperature, rho_last)) * calc_self_diffusivity(temperature) + \
            calc_vol_dislocation(temperature, rho_last) * calc_gb_diffusivity(temperature)
    return d_eff


def calc_gb_mobility(temperature):
    M_g = 1.05e-4 * numpy.exp(-160000 / (8.314 * temperature))
    return M_g


def calc_gb_mobility2_drx(temperature):
    M_g = 355e-6 * numpy.exp(-29410 * 4.25 / (8.314 * temperature))
    return M_g


def calc_austenite_gb_energy(temperature):
    Gam_gb = 1.3115 - 0.0005 * temperature
    return Gam_gb


def calc_pinning_pressure(temperature, fraction_p, radius_p):
    pinning_press = 3 * calc_austenite_gb_energy(temperature) * fraction_p / 2 / radius_p
    return pinning_press


# def calc_stress(temp_curr, temp_strain_rate, rho_m):
#      'calculation of stress'
#      a5 = deformation.calc_const_A5(temp_curr, temp_strain_rate) / math.sqrt(rho_m)
#      const_sigma0 = (58.7 - 0.0425*(temp_curr - 273)) * math.pow(10, 6)
#      stress_part1 = inputdata.M * inputdata.alpha * calc_shear_modulus(temp_curr) * calc_burgers_vector(temp_curr) * math.sqrt(rho_m)
#      stress_part2 = (inputdata.M * temp_curr * inputdata.K_b * math.sqrt(rho_m) * numpy.arcsinh(a5))/ (math.pow(calc_burgers_vector(temp_curr), 2) * inputdata.fitting_params['C_9'])
#      stress = stress_part1 + stress_part2 + const_sigma0
#      return stress


def calculate_stress(temp_curr, strain_rate_initial, rho_m):
    a0 = inputdata.M * strain_rate_initial / calc_burgers_vector(temp_curr)
    a3 = a0 / (fp['C_7'] * inputdata.nu_a)
    a4 = numpy.exp(fp['C_8'] * (calc_shear_modulus(temp_curr) / (2 * inputdata.K_b * temp_curr)) \
                   * math.pow(calc_burgers_vector(temp_curr), 3))
    a5 = a3 * a4
    modified_a5 = a5 / math.sqrt(rho_m)
    const_sigma0 = (58.7 - 0.0425 * (temp_curr - 273)) * math.pow(10, 6)
    stress_part1 = inputdata.M * inputdata.alpha * calc_shear_modulus(temp_curr) * calc_burgers_vector(
        temp_curr) * math.sqrt(rho_m)
    stress_part2 = (inputdata.M * temp_curr * inputdata.K_b * math.sqrt(rho_m) * numpy.arcsinh(modified_a5)) / (
                math.pow(calc_burgers_vector(temp_curr), 2) * fp['C_9'])
    stress = stress_part1 + stress_part2 + const_sigma0
    return stress
