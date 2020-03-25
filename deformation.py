import math
import material_constants as material_constants
import inputdata as inputdata
import numpy


def strain_calc(strain_init, time_step, strain_rate):
    
    strain_current = strain_init + strain_rate * time_step

    return strain_current


def calc_deformation_dislocation(rho_prev, time_step, temperature,
                                 strain_rate_initial, D_def, c1, c2, c3,
                                 c4, c5, c6, c7, c8, c9, c10, m):
    ''' calculation of all the A values using the constants c1, c2, c3, c4 ... to be further used for'
        'the dislocation density calculation after deformation '''
    a0 = m * strain_rate_initial / material_constants.calc_burgers_vector(temperature)
    a1 = c4 * c5 * m * inputdata.alpha * material_constants.calc_shear_modulus(temperature) \
         / (inputdata.K_b * temperature) * math.pow(material_constants.calc_burgers_vector(temperature), 4)
    a2 = c4 * c5 * material_constants.calc_burgers_vector(temperature) * m / c9
    a3 = a0 / (c7 * inputdata.nu_a)
    a4 = numpy.exp(c8 * (
                material_constants.calc_shear_modulus(temperature) / (2 * inputdata.K_b * temperature)) \
                   * math.pow(material_constants.calc_burgers_vector(temperature), 3))
    a5 = a3 * a4
    subpart1 = a0 * c1 / (3 * D_def)
    subpart2 = a0 * c2 * math.sqrt(rho_prev)
    subpart3 = -3 * c3 * a0 * material_constants.calc_burgers_vector(temperature) * rho_prev
    subpart4 = -5 * a1 * material_constants.calc_effective_diffusivity(temperature, rho_prev) * math.pow(rho_prev, 2.5)
    subpart5 = (subpart4 / (5 * a1)) * a2 * math.asinh(a5 / math.sqrt(rho_prev))
    rho_current = (subpart1 + subpart2 + subpart3 + subpart4 + subpart5) * time_step + rho_prev
    return rho_current
