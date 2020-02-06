# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 23:33:54 2020

@author: aserafeim
"""
import inputdata as id
import dislo_amir as dis
t=0
eps=0
rho_cm=id.rho_cm_0*id.rho_0
rho_wi=id.rho_wi_0*id.rho_0
rho_ci=id.rho_ci_0*id.rho_0

strain_l=[0]
cm_l=[rho_cm]
wi_l=[rho_wi]
ci_l=[rho_ci]
sigma_l=[]
time_l=[0]
cm_gn=[0]
cm_an=[0]
ci_an=[0]
wi_an=[0]
ci_ac=[0]
wi_ac=[0]
cm_tr=[0]
wi_nc=[0]
ci_rm=[0]
wi_rm=[0]
dci=[0]

for i in range(500):
    dt=0.1
    eps_dot=0.01
    t+=dt
    eps+=eps_dot*dt
    deps=dt*eps_dot
    T=(550+273.15)/id.T0
    
    r_d=dis.dislo2(dt,T,deps,eps_dot,rho_cm,rho_wi,rho_ci)

    if i==0:
        sigma_l.append(r_d['s_v']) 
    else:
        sigma_l.append(r_d['s'])
    
    time_l.append(t)
    strain_l.append(eps)
    cm_l.append(r_d['r_cm_c'])
    wi_l.append(r_d['r_wi_c'])
    ci_l.append(r_d['r_ci_c'])
    dci.append(r_d['drho_ci'])
    cm_gn.append(r_d['drho_cm_gn'])
    cm_an.append(r_d['drho_cm_an'])
    ci_an.append(r_d['drho_ci_an'])
    wi_an.append(r_d['drho_wi_an'])
    ci_ac.append(r_d['drho_ci_ac'])
    wi_ac.append(r_d['drho_wi_ac'])
    cm_tr.append(r_d['drho_cm_tr'])
    wi_nc.append(r_d['drho_wi_nc'])
    ci_rm.append(r_d['drho_ci_rm'])
    wi_rm.append(r_d['drho_wi_rm'])
    
    
#     r_d['s_v']=sigma_v
#    r_d['r_wi_c']=rho_wi_curr
#    r_d['r_ci_c']=rho_ci_curr
#    r_d['r_cm_c']=rho_cm_curr
#    r_d['s']=sigma
#    r_d['drho_cm_gn']=drho_cm_gn
#    r_d['drho_cm_an']=drho_cm_an
#    r_d['drho_ci_an']=drho_ci_an
#    r_d['drho_wi_an']=drho_wi_an
#    r_d['drho_ci_ac']=drho_ci_ac
#    r_d['drho_wi_ac']=drho_wi_ac
#    r_d['drho_cm_tr']=drho_cm_tr
#    r_d['drho_wi_nc']=drho_wi_nc
#    r_d['drho_ci_rm']=drho_ci_rm
#    r_d['drho_wi_rm']=drho_wi_rm
    rho_cm=cm_l[-1]
    rho_wi=wi_l[-1]
    rho_ci=ci_l[-1]
    print (eps)