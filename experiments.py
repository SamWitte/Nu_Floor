"""

Define experimental parameters based on element

"""

import numpy as np
import os

path = os.getcwd()

mp = 0.931
year_to_sec = 3.154e7
joule_to_MeV = 6.242e12
miles_to_m = 1609.34
ft_to_m = 0.3048


def Element_Info(element, electronic=False):
    print element
    if element == 'Germanium':
        Qmin = 0.04
        Qmax = 10.
        #Qmin = 10.
        #Qmax = 300.
        #Qmax = 50.
        Z = 32.
        Atope = np.array([70., 72., 73., 74., 76.])
        mfrac = np.array([0.212, 0.277, 0.077, 0.359, 0.074])
    
    elif element == 'Xenon':
        #Nuclear
        if not electronic:
            Qmin = 0.1
            Qmax = 50.
            #Qmin = 10.
            #Qmax = 300.
        else:
            # Electronic
            Qmin = 10.
            Qmax = 2e3
        
        Z = 54.
        Atope = np.array([128., 129., 130., 131., 132., 134., 136.])
        mfrac = np.array([0.019, 0.264, 0.041, 0.212, 0.269, 0.104, 0.089])

    elif element == 'Argon':
        if not electronic:
            Qmin = 1.
            Qmax = 50.
            #Qmin = 10.
            #Qmax = 300.
        else:
            # Electronic
            Qmin = 600.
            Qmax = 2e3
        
        Z = 18.
        Atope = np.array([40.])
        mfrac = np.array([1.])

    elif element == 'Sodium':
        #Qmin = 1.
        #Qmax = 50.
        Qmin = 10.
        Qmax = 300.
        Z = 11.
        Atope = np.array([23.])
        mfrac = np.array([1.])

    elif element == 'Iodine':
        #Qmin = 1.
        #Qmax = 50.
        Qmin = 10.
        Qmax = 300.
        Z = 53.
        Atope = np.array([127.])
        mfrac = np.array([1.])

    elif element == 'Fluorine':
        Qmin = 1.
        Qmax = 50.
        Z = 9.
        Atope = np.array([19.])
        mfrac = np.array([1.])

    elif element == 'Silicon':
        Qmin = 0.1
        Qmax = 50.
        Z = 14.
        Atope = np.array([28, 29, 30])
        mfrac = np.array([0.922, 0.0468, 0.03119])

    elif element == 'FutureARGO':
        Qmin = 10.
        Qmax = 200.
        Z = 18.
        Atope = np.array([40.])
        mfrac = np.array([1.])
    elif element == 'FutureARGO_S2':
        Qmin = 0.6
        Qmax = 10.
        Z = 18.
        Atope = np.array([40.])
        mfrac = np.array([1.])
    elif element == 'FutureF':
        Qmin = 6. # check
        Qmax = 150.
        Z = 9.
        Atope = np.array([19.])
        mfrac = np.array([1.])
    elif element == 'FutureXe':
        Qmin = 1.
        Qmax = 150.
        Z = 54.
        Atope = np.array([128., 129., 130., 131., 132., 134., 136.])
        mfrac = np.array([0.019, 0.264, 0.041, 0.212, 0.269, 0.104, 0.089])
    elif element == 'FutureGe':
        Qmin = 0.04
        Qmax = 50.
        Z = 32.
        Atope = np.array([70., 72., 73., 74., 76.])
        mfrac = np.array([0.212, 0.277, 0.077, 0.359, 0.074])
    elif element == 'FutureNEWS_G':
        Qmin = 0.1
        Qmax = 10.
        Z = 2
        Atope = np.array([4.])
        mfrac = np.array([1.])
    else:
        raise ValueError

    isotope = np.zeros((len(Atope), 4))
    for i in range(len(Atope)):
        isotope[i] = np.array([mp * Atope[i], Z, Atope[i], mfrac[i]])
    return isotope, Qmin, Qmax


def laboratory(elem, xen='LZ', geo_analysis=False):
    if elem == 'Germanium' or elem == 'Fluorine':
        lab = 'Snolab'
    elif elem == 'Xenon':
        if xen == 'LZ':
            lab = 'SURF'
        elif xen == 'X':
            lab = 'GS'
        else:
            raise ValueError
    elif elem == 'Argon':
        lab = 'GS'
    elif elem == 'Sodium' or elem == 'Iodine':
        lab = 'GS'
    else:
        lab = 'GS'
    if geo_analysis:
        lab = 'JP'
    return lab

# Name of reactor, Surface distance in km, Power output MWe
reactors_SURF = [['Cooper Nuclear Station', 801., 2419.],
                 ['Monticello Nuclear Generating Plant', 788., 2004.],
                 ['Prarie Island Nuclear Generating Plant', 835., 3334.]]

reactors_SNOLAB = [['Nine Mile Point Nuclear Station U2', 498., 1850.],
                   ['Nine Mile Point Nuclear Station U1', 498., 3988.],
                   ['R.E. Ginna Nuclear Power Plant', 468., 1775.],
                   ['James A. Fitzpatrick Nuclear Power Plant', 500., 2536.],
                   ['Point Beach Nuclear Power Plant U1', 552., 1800.],
                   ['Point Beach Nuclear Power Plant U2', 552., 1800.],
                   ['Fermi Unit II', 527., 3486.],
                   ['Davis-Besse Nuclear Power Station', 563., 2817.],
                   ['Perry Nuclear Power Plant U1', 519., 3758.],
                   ['Bruce Nuclear Generating Station', 240., 21384.],
                   ['Darlington Nuclear Generating Station', 343., 11104.]]

reactors_GS = [['Tricastin 1-4', 744., 11140.],
               ['Cruas 1-4', 750., 11140.],
               ['St. Alban 1-2', 778., 7634.],
               ['Bugey 2-5', 760., 13094.]]

reactors_JP = [['Fangchengang', 998.16, 12110.],
                ['Changjiang', 1206., 3806.],
                ['Yangjiang', 1239., 17430.],
                ['Taishan', 1318., 9180.],
                ['Ling Ao', 1422., 11620.],
                ['Fuqing', 1763., 17740.],
                ['Hanbit', 2463., 16874.]]

Nfiss = 6.
reac_runtime = 0.75
rntime_err = 0.06
Efiss = 205.3  # MeV


def reactor_flux(loc='Snolab'):
    if loc == 'Snolab':
        depth = 6000. * ft_to_m
        reactor_list = reactors_SNOLAB
    elif loc == 'SURF':
        depth = 8000. * ft_to_m
        reactor_list = reactors_SURF
    elif loc == 'GS':
        depth = 1.
        reactor_list = reactors_GS
    elif loc == 'JP':
        depth = 2400.
        reactor_list = reactors_JP
    else:
        depth = 0.
        reactor_list = []

    flux = 0.
    err = 0.
    for reactor in reactor_list:
        flux += Nfiss * reactor[2] * joule_to_MeV * 1e6/Efiss * reac_runtime / \
                (4. * np.pi * (reactor[1]*1e5 + depth*1e2)**2.)
#        err += Nfiss * reactor[2] * joule_to_MeV * 1e6/Efiss * reac_runtime / \
#            (4. * np.pi * (reactor[1]*1e5 + depth*1e2)**2.)*np.sqrt((0.6/Efiss)**2. + (rntime_err/reac_runtime)**2. + (10./reactor[1])**2.)
    err = 0.1 * flux
    return flux, err

def geo_flux(loc='Snolab', el='U'):
    #print loc, el
    # element is either 'U' or 'Th' or 'K'
    extrafactor = 1.
    if loc == 'Snolab':
        if el == 'U':
            flux = 4.9 * 10 ** 6.
            flx_err = 0.98 * 10 ** 6.
        elif el == 'Th':
            flux = 4.55 * 10 ** 6.
            flx_err = 1.17 * 10 ** 6.
        elif el == 'K':
            flux = 21.88 * 10 ** 6.
            flx_err = 3.67 * 10 ** 6.
    elif loc == 'SURF':
        if el == 'U':
            flux = 5.26 * 10**6.
            flx_err = 1.17 * 10**6.
        elif el == 'Th':
            flux = 4.90 * 10**6.
            flx_err = 1.34 * 10**6.
        elif el == 'K':
            flux = 22.68 * 10 ** 6.
            flx_err = 4.37 * 10 ** 6.
    elif loc == 'GS':
        if el == 'U':
            flux = 4.34 * 10**6.
            flx_err = 0.96 * 10 **6.
        elif el == 'Th':
            flux = 4.23 * 10**6.
            flx_err = 1.26 * 10 **6.
        elif el == 'K':
            flux = 20.54 * 10 ** 6.
            flx_err = 3.99 * 10 ** 6.

    if loc == 'JP':
        extrafactor = 2.5
        if el == 'U':
            flux = extrafactor * 4.9 * 10 ** 6.
            flx_err = 0.98 * 10 ** 6.
        elif el == 'Th':
            flux = extrafactor * 4.55 * 10 ** 6.
            flx_err = 1.17 * 10 ** 6.
        elif el == 'K':
            flux = extrafactor * 21.88 * 10 ** 6.
            flx_err = 3.67 * 10 ** 6.
    return flux, flx_err


def bkg_electron_specs(elem='Xenon'):
    if elem == 'Xenon':
        file_list = ["Xe_Kr", "Xe_2N2B", "Xe_Rn"]
    elif elem == 'Argon':
        file_list = ["Ar_Cos", "Ar_P", "Ar_Rn"]

    return file_list

def geo_uncertainty():
    
    geo_flux = {}
    geo_flux['GS_U'] = 4.34e6
    geo_flux['GS_U_high'] = 0.96e6
    geo_flux['GS_U_low'] = 0.75e6
    geo_flux['GS_Th'] = 4.23e6
    geo_flux['GS_Th_high'] = 1.26e6
    geo_flux['GS_Th_low'] = 0.8e6
    geo_flux['GS_K'] = 20.54e6
    geo_flux['GS_K_high'] = 3.99e6
    geo_flux['GS_K_low'] = 2.96e6
    
    geo_flux['SURF_U'] = 5.26e6
    geo_flux['SURF_U_high'] = 1.17e6
    geo_flux['SURF_U_low'] = 0.97e6
    geo_flux['SURF_Th'] = 4.9e6
    geo_flux['SURF_Th_high'] = 1.34e6
    geo_flux['SURF_Th_low'] = 0.87e6
    geo_flux['SURF_K'] = 22.68e6
    geo_flux['SURF_K_high'] = 4.37e6
    geo_flux['SURF_K_low'] = 3.13e6
    
    geo_flux['Snolab_U'] = 4.9e6
    geo_flux['Snolab_U_high'] = 0.98e6
    geo_flux['Snolab_U_low'] = 0.78e6
    geo_flux['Snolab_Th'] = 4.55e6
    geo_flux['Snolab_Th_high'] = 1.17e6
    geo_flux['Snolab_Th_low'] = 0.73e6
    geo_flux['Snolab_K'] = 21.88e6
    geo_flux['Snolab_K_high'] = 3.67e6
    geo_flux['Snolab_K_low'] = 2.76e6
    
    extrafactor = 2.5
    geo_flux['JP_U'] = extrafactor*4.9e6
    geo_flux['JP_U_high'] = 0.98e6
    geo_flux['JP_U_low'] = 0.78e6
    geo_flux['JP_Th'] = extrafactor*4.55e6
    geo_flux['JP_Th_high'] = 1.17e6
    geo_flux['JP_Th_low'] = 0.73e6
    geo_flux['JP_K'] = extrafactor*21.88e6
    geo_flux['JP_K_high'] = 3.67e6
    geo_flux['JP_K_low'] = 2.76e6
    
    return geo_flux
