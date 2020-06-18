import material_constants as mat_const
import inputdata
from inputdata import fitting_params as fp
import math


def strain_calc(strain_init, time_step, strain_rate):
    strain_current = strain_init + strain_rate * time_step

    return strain_current


def deformation_and_drx(temperature, strain_rate_curr, dt, D_def, rho_prev, x_prev, r_g_prev, n_rx_prev, x_c_prev):
    b = mat_const.calc_burgers_vector(temperature)
    G = mat_const.calc_shear_modulus(temperature)
    D_eff = mat_const.calc_effective_diffusivity(temperature, rho_prev)
    Gam_gb = mat_const.calc_austenite_gb_energy(temperature)
    tau = mat_const.calc_dislocation_line_energy(temperature)
    M_g = mat_const.calc_gb_mobility2_drx(temperature)
    a0 = inputdata.M * strain_rate_curr / b
    a1 = fp['C_4'] * fp['C_5'] * math.pow(b, 4) * inputdata.M * inputdata.alpha * G / (inputdata.K_b * temperature)
    a2 = fp['C_4'] * fp['C_5'] * b * inputdata.M / fp['C_9']
    a3 = a0 / (fp['C_7'] * inputdata.nu_a)
    a4 = math.exp(fp['C_8'] * G * math.pow(b, 3)/ (2 * inputdata.K_b * temperature))
    a5 = a3 * a4
    drho_dt0 = a0 * ((fp['C_1']/3) / D_def)
    drho_dt1 = a0 * fp['C_2'] * math.sqrt(rho_prev)
    drho_dt3 = a0 * fp['C_3'] * 3 * b * rho_prev
    drho_dt4 = a1 * 5 * D_eff * math.pow(rho_prev, 2.5)
    drho_dt5 = a2 * D_eff * math.pow(rho_prev, 2.5)
    drho_dt6 = math.asinh(a5 / math.sqrt(rho_prev))

    drho_dt = drho_dt0 + drho_dt1 - drho_dt3 - drho_dt4 - drho_dt5 * drho_dt6
    rho_curr = rho_prev + drho_dt * dt

    l_d = 1 / ((fp['C_1'] / D_def) + fp['C_2'] * math.sqrt(rho_curr))
    'critical rho calculation'
    if strain_rate_curr >= 1:
        n_z = 0.1
    else:
        n_z = 1

    'rho critical'
    rho_c = math.pow((16 * Gam_gb * inputdata.M * math.pow(strain_rate_curr, n_z) / (3 * b * M_g * math.pow(tau, 2)))*((fp['C_1'] / D_def) + fp['C_2'] * math.sqrt(inputdata.rho_const)), (1/3))
    l_d_cr = 1 / ((fp['C_1'] / D_def) + fp['C_2'] * math.sqrt(rho_c))

    if rho_curr > rho_c and round(strain_rate_curr, 7) != 0.0:
        r_xc = (3 * b * M_g * tau / (4 * inputdata.M * fp['C_10'])) * (math.pow(rho_c, 2) /(fp['C_1'] / D_def + fp['C_2'] * math.sqrt(rho_c)))
        n_d = math.pi * math.pow(r_xc, 2) / math.pow(l_d_cr, 2)
        p_r = math.exp(-281000 / (inputdata.uni_gas_const * temperature))
        kf = 0.4e6
        dn_rx_dt = kf * strain_rate_curr * p_r * (1 - x_prev)/(n_d * D_def * b * l_d)
    else:
        dn_rx_dt = 0.0
        r_xc = 0.0
        n_d = math.pi * math.pow(r_xc, 2) / math.pow(l_d_cr, 2)

    d_nrx = dn_rx_dt * dt
    n_rx_curr = n_rx_prev + dn_rx_dt * dt

    if round(n_rx_curr, 7) != 0:
        'calculate r_rx'
        r_rx = (n_rx_prev * r_g_prev + d_nrx * r_xc) / n_rx_curr
    else:
        r_rx = 0.0

    x_curr = (4/3) * math.pi * n_rx_curr * math.pow(r_rx, 3)
    x_c_curr = x_c_prev
    if round(x_c_curr, 7) == 0.0:
        x_c_curr = x_curr
        psi_x = 1.0
    else:
        psi_x = 1 - math.pow(((x_curr - x_c_curr)/(1 - x_c_curr)), inputdata.n_x)

    if round(n_rx_curr, 7) != 0.0:
        d_rg_dt = psi_x * M_g * tau * rho_curr
    else:
        d_rg_dt = 0.0

    r_g_curr = r_rx + d_rg_dt * dt
    fragment1 = (fp['C_1'] / D_def + fp['C_2'] * math.sqrt(rho_curr))
    if strain_rate_curr <= 1:
        rho_rx = 0.85 * math.pow(strain_rate_curr, 0.2) * inputdata.M / (b * math.pow(M_g, 0.97) * tau * rho_curr) * fragment1 * r_rx
    else:
        rho_rx = 0.005 * math.pow(strain_rate_curr, 0.176) * inputdata.M / (
                    b * math.pow(M_g, 0.98) * tau * rho_curr) * fragment1 * r_rx

    rho_m = rho_curr * (1 - x_curr) + rho_rx * x_curr

    d_mean = x_curr * 2 * r_g_curr + (1-x_curr) * D_def

    deformation_dict = {'D_def': D_def,
                        'rho_critical': rho_c,
                        'rho_def': rho_curr,
                        'r_xc': r_xc,
                        'n_d': n_d,
                        'x_curr': x_curr,
                        'd_nrx_dt': dn_rx_dt,
                        'n_rx': n_rx_curr,
                        'r_rx': r_rx,
                        'drg_dt': d_rg_dt,
                        'r_g_curr': r_g_curr,
                        'rho_rxed': rho_rx,
                        'd_mean': d_mean,
                        'rho_m': rho_m,
                        'd_nrx': d_nrx,
                        'x_c_curr': x_c_curr
                        }

    return deformation_dict
