import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import matplotlib.pyplot as plt
import os
from scipy.interpolate import interp1d
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib as mpl
from experiments import *
from likelihood import *
from helpers import *
from rate_UV import *
from constants import *

import matplotlib.patheffects as PathEffects
import matplotlib.gridspec as gridspec
import glob
from matplotlib import rc
rc('font',**{'family':'serif','serif':['Times','Palatino']})
rc('text', usetex=True)


mpl.rcParams['xtick.major.size']=8
mpl.rcParams['ytick.major.size']=8
mpl.rcParams['xtick.labelsize']=18
mpl.rcParams['ytick.labelsize']=18


path = os.getcwd()
test_plots = os.getcwd() + '/Test_Plots/'

#solar nu flux taken from SSM 1104.1639


def neutrino_spectrum(lab='Snolab', Emin=0.1, Emax=1000., fs=18, save=True, sve_data=False):
    filename = test_plots + 'NeutrinoFlux_' + lab + '.pdf'
    ylims = [10**-4., 10**13.]

    nu_comp = ['b8', 'b7l1', 'b7l2', 'pepl1', 'hep', 'pp', 'o15', 'n13', 'f17', 'atmnue',
               'atmnuebar', 'atmnumu', 'atmnumubar', 'dsnb3mev', 'dsnb5mev', 'dsnb8mev',
               'reactor', 'geoU', 'geoTh','geoK']
    color_list = ['#800080', '#000080', '#000080', '#8A2BE2', '#A52A2A', '#A0522D', '#DC143C', '#B8860B',
                  '#8B008B', '#556B2F', '#FF8C00', '#9932CC', '#E9967A', '#FF1493', '#696969', '#228B22',
                  '#40E0D0', '#CD5C5C', '#90EE90', '#90EE90']
    nu_labels = ['8B', '7B [384.3 keV]', '7B [861.3 keV]', 'pep', 'hep', 'pp', '15O', '13N', '17F',
                 r'atm $\nu_e$', r'atm $\nu_{\bar e}$', r'atm $\nu_\mu$',
                 r'atm $\nu_{\bar \mu}$', 'DSN 3 MeV',
                 'DSN 5 MeV', 'DSN 8 MeV', 'Reactor', 'Geo U', 'Geo Th','Geo K']

    pl.figure()
    ax = pl.gca()
    
    if sve_data:
        dat_name = test_plots + 'NeuSpectrum_' + lab + '_'

    for i,nu in enumerate(nu_comp):
        er, spec = Nu_spec(lab).nu_spectrum_enu(nu, emin=Emin)
        pl.plot(er, spec, color_list[i], lw=1, label=nu_labels[i])
        if sve_data:
            fle = dat_name + nu + '.dat'
            np.savetxt(fle, np.column_stack((er, spec)))

    ax.set_xlabel(r'$E_\nu$  [MeV]', fontsize=fs)
    ax.set_ylabel(r'Neutrino Flux  [$cm^{-2} s^{-1} MeV^{-1}$]', fontsize=fs)


    plt.tight_layout()

    plt.xlim(xmin=Emin, xmax=Emax)
    plt.ylim(ymin=ylims[0],ymax=ylims[1])
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.legend(loc=1, frameon=True, framealpha=0.5, fontsize=9, ncol=1, fancybox=True)


    if save:
        plt.savefig(filename)
    return


def neutrino_recoils(Emin=0.001, Emax=100., element='Germanium', fs=18, save=True,
                     mass=6., sigmap=4.*10**-45., model='sigma_si', fnfp=1.,
                     delta=0., GF=False, time_info=False, xenlab='LZ', sve_data=False, geo_analysis=False):
    coupling = "fnfp" + model[5:]

    filename = test_plots + 'Recoils_in_' + element + '_'
    filename += model + '_' + coupling + '_{:.2f}'.format(fnfp)
    filename += '_DM_mass_{:.2f}_CSec_{:.2e}_Delta_{:.2f}'.format(mass, sigmap, delta)
    if element == 'xenon':
        filename += xenlab + '_'
    filename += '.pdf'

    er_list = np.logspace(np.log10(Emin), np.log10(Emax), 500)

    experiment_info, Qmin, Qmax = Element_Info(element)

    lab = laboratory(element, xen=xenlab, geo_analysis=geo_analysis)

    nu_comp = ['b8', 'b7l1', 'b7l2', 'pepl1', 'hep', 'pp', 'o15', 'n13', 'f17', 'atmnue',
               'atmnuebar', 'atmnumu', 'atmnumubar', 'dsnb3mev', 'dsnb5mev', 'dsnb8mev',
               'reactor', 'geoU', 'geoTh','geoK']

    nu_labels = ['8B', '7B [384.3 keV]', '7B [861.3 keV]', 'pep', 'hep', 'pp', '15O', '13N', '17F',
                 r'atm $\nu_e$', r'atm $\nu_{\bar e}$', r'atm $\nu_\mu$',
                 r'atm $\nu_{\bar \mu}$', 'DSN 3 MeV',
                 'DSN 5 MeV', 'DSN 8 MeV', 'Reactor', 'Geo U', 'Geo Th','Geo K']

    nu_lines = ['b7l1', 'b7l2', 'pepl1']
    line_flux = [(0.1) * 5.00 * 10. ** 9., (0.9) * 5.00 * 10. ** 9., 1.44 * 10. ** 8.]
    e_lines = [0.380, 0.860, 1.440]

    color_list = ['#800080', '#000080', '#000080', '#8A2BE2', '#A52A2A', '#A0522D', '#DC143C', '#B8860B',
                  '#8B008B', '#556B2F', '#FF8C00', '#9932CC', '#E9967A', '#FF1493', '#696969', '#228B22',
                  '#40E0D0', '#CD5C5C', '#90EE90','#90EE90']
    line_list = ['-', '--', '--', '-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-']


    nu_contrib = len(nu_comp)
    nuspec = np.zeros(nu_contrib, dtype=object)

    for i in range(nu_contrib):
        nuspec[i] = np.zeros_like(er_list)

    for iso in experiment_info:
        for i in range(nu_contrib):
            nuspec[i] += Nu_spec(lab).nu_rate(nu_comp[i], er_list, iso)

    if element != 'Silicon':
        coupling = "fnfp" + model[5:]
        drdq_params = default_rate_parameters.copy()
        drdq_params['element'] = element
        drdq_params['mass'] = mass
        drdq_params[model] = sigmap
        drdq_params[coupling] = fnfp
        drdq_params['delta'] = delta
        drdq_params['GF'] = GF
        drdq_params['time_info'] = time_info
        time_list = np.zeros_like(er_list)
        dm_spec = dRdQ(er_list, time_list, **drdq_params) * 10. ** 3. * s_to_yr

    pl.figure()
    ax = pl.gca()

    ax.set_xlabel(r'Recoil Energy  [keV]', fontsize=fs)
    ax.set_ylabel(r'Event Rate  [${\rm ton}^{-1} {\rm yr}^{-1} {\rm keV}^{-1}$]', fontsize=fs)

    for i in range(nu_contrib):
        pl.plot(er_list, nuspec[i], color_list[i], ls=line_list[i], lw=1, label=nu_labels[i])
        if sve_data:
            fileN = test_plots + 'Recoils_in_' + element + '_' + nu_comp[i] + '_.dat'
            np.savetxt(fileN, np.column_stack((er_list, nuspec[i])))

    if element != 'Silicon':
        pl.plot(er_list, dm_spec, 'b', lw=1, label='Dark Matter')
        print 'Number of dark matter events: ', np.trapz(dm_spec, er_list)
    plt.tight_layout()

    plt.xlim(xmin=Emin, xmax=Emax)
    plt.ylim(ymin=10.**-5., ymax=10.**8.)
    ax.set_xscale("log")
    ax.set_yscale("log")

    plt.legend(loc=1, frameon=True, framealpha=0.5, fontsize=9, ncol=1, fancybox=True)

    if save:
        plt.savefig(filename)
    return

def geo_recoil_rate(Emin=1., Emax=2000., fs=18, type='K', electronic=False, sve_data=False, geo_analysis=False):
    filename = test_plots + 'GeoRecoils_'
    if electronic:
        filename += 'Electronic_'
        er_list = np.logspace(np.log10(Emin), np.log10(Emax), 2000)
    else:
        filename += 'Nuclear_'
        Emin = 1e-2
        Emax = 1.
        er_list = np.logspace(np.log10(Emin), np.log10(Emax), 2000)
    if sve_data:
        fileSve = filename + '_'
    filename += type + '_all_Targets.pdf'

    colorL = ['red', 'blue', 'purple', 'green' ,'yellow', 'black', 'orange', 'cyan']
    
    nu_s = 'geo' + type
    targets = ['Xenon', 'Germanium', 'Argon', 'Fluorine', 'Sodium', 'Iodine', 'Silicon']
    pl.figure()
    ax = pl.gca()
    
    for i,tar in enumerate(targets):
        experiment_info, Qmin, Qmax = Element_Info(tar)
        lab = laboratory(tar, geo_analysis=geo_analysis)
        nuspec = np.zeros_like(er_list)
        for iso in experiment_info:
            if electronic:
                nuspec += Nu_spec('SURF').nu_rate_electronic(nu_s, er_list, iso, tar)
            else:
                nuspec += Nu_spec('SURF').nu_rate(nu_s, er_list, iso)

        pl.plot(er_list, nuspec, colorL[i], lw=1, label=tar)
        if sve_data:
            np.savetxt(fileSve + tar + '_' + nu_s + '.dat', np.column_stack((er_list, nuspec)))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r'Recoil Energy  [keV]', fontsize=fs)
    ax.set_ylabel(r'Event Rate  [${\rm ton}^{-1} {\rm yr}^{-1} {\rm keV}^{-1}$]', fontsize=fs)
    plt.xlim(xmin=Emin, xmax=Emax)
    #plt.ylim(ymin=10.**-4., ymax=2*10.**-2.)
    plt.legend(loc=1, frameon=True, framealpha=0.5, fontsize=9, ncol=1, fancybox=True)
    plt.savefig(filename)
    
    return

def neutrino_electronic_recoils(Emin=10., Emax=3000., element='Xenon', fs=18, save=True, xenlab='LZ', sve_data=False, geo_analysis=False):
    #coupling = "fnfp" + model[5:]

    filename = test_plots + 'ELECTRONIC_Recoils_in_' + element + '_'
    #filename += model + '_' + coupling + '_{:.2f}'.format(fnfp)
    #filename += '_DM_mass_{:.2f}_CSec_{:.2e}_Delta_{:.2f}'.format(mass, sigmap, delta)
    if element == 'xenon':
        filename += xenlab + '_'
    filename += '.pdf'

    er_list = np.logspace(np.log10(Emin), np.log10(Emax), 2000)

    experiment_info, Qmin, Qmax = Element_Info(element)
    lab = laboratory(element, xen=xenlab, geo_analysis=geo_analysis)

    nu_comp = ['b8', 'b7l1', 'b7l2', 'pepl1', 'hep', 'pp', 'o15', 'n13', 'f17',
               'reactor']

    nu_labels = ['8B', '7B [384.3 keV]', '7B [861.3 keV]', 'pep', 'hep', 'pp', '15O', '13N', '17F',
                'Reactor']

    nu_comp2 = ['geoU', 'geoTh','geoK']
    nu_labels2 = ['Geo U', 'Geo Th','Geo K']
    labsL = ['Snolab', 'SURF', 'GS']
    tagFluxL = ['_U', '_U_high', '_U_low', '_Th', '_Th_high', '_Th_low', '_K', '_K_high', '_K_low']

    nu_lines = ['b7l1', 'b7l2', 'pepl1']
    line_flux = [(0.1) * 5.00 * 10. ** 9., (0.9) * 5.00 * 10. ** 9., 1.44 * 10. ** 8.]
    e_lines = [0.380, 0.860, 1.440]

    color_list = ['#61E786', '#5A5766', '#9792E3', '#F98948', '#9B8816', '#F9EA9A', '#558B6E', '#B88C9E', '#66C3FF', 'red']
    line_list = ['-', '--', '--', '-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-']

    color_list_2 = ['k', 'k', 'k']

    nu_contrib = len(nu_comp)
    nuspec = np.zeros(nu_contrib, dtype=object)
    
    nu_contribGEO = len(nu_comp2)
    nu_contrib2 = len(nu_comp2*3*3)
    nuspecGEO = np.zeros(nu_contribGEO, dtype=object)
    nuspec2 = np.zeros(nu_contrib2, dtype=object)
    geo_clr = ['#F49F0A', '#00A6A6', '#D95D39']

    for i in range(nu_contrib):
        nuspec[i] = np.zeros_like(er_list)

    for iso in experiment_info:
        for i in range(nu_contrib):
            nuspec[i] += Nu_spec(lab).nu_rate_electronic(nu_comp[i], er_list, iso, element)

    pl.figure()
    ax = pl.gca()
    # Geo neutrino. Run over labs and range of fluxes.
    geo_flux = geo_uncertainty()
    Sigma_U = [geo_flux['GS_U'] - geo_flux['GS_U_low'], geo_flux['SURF_U'] + geo_flux['SURF_U_high']]
    Sigma_Th = [geo_flux['GS_Th'] - geo_flux['GS_Th_low'], geo_flux['SURF_Th'] + geo_flux['SURF_Th_high']]
    Sigma_K = [geo_flux['GS_K'] - geo_flux['GS_K_low'], geo_flux['SURF_K'] + geo_flux['SURF_K_high']]
    SigmaLST = [Sigma_U, Sigma_Th, Sigma_K]
    sigma_mid = [geo_flux['GS_U'], geo_flux['GS_Th'], geo_flux['GS_K'], geo_flux['GS_U'], geo_flux['GS_Th'], geo_flux['GS_K']]
    for i in range(nu_contribGEO):
        nuspecGEO[i] = np.zeros_like(er_list)
    for iso in experiment_info:
        for i in range(nu_contribGEO):
            nuspecGEO[i] += Nu_spec(lab).nu_rate_electronic(nu_comp2[i], er_list, iso, element) / geo_flux[lab + tagFluxL[3*i]]

    for i in range(nu_contribGEO):
        
        erCHK = er_list[nuspecGEO[i] > 0]
        nuspecGEO[i] = nuspecGEO[i][nuspecGEO[i] > 0]
        plt.fill_between(erCHK, nuspecGEO[i]*SigmaLST[i][0], nuspecGEO[i]*SigmaLST[i][1], lw=1,
                        color=geo_clr[i], alpha=0.3, label=nu_comp2[i])
        if sve_data:
#            print test_plots + 'Electron_Recoils_in_' + element + '_' + nu_comp2[i] + '_.dat'
#            print  len(nuspecGEO[i]) , sigma_mid[i], len(erCHK)
            np.savetxt(test_plots + 'Electron_Recoils_in_' + element + '_' + nu_comp2[i] + '_.dat', np.column_stack((erCHK, nuspecGEO[i]*sigma_mid[i])))

#    coupling = "fnfp" + model[5:]
#    drdq_params = default_rate_parameters.copy()
#    drdq_params['element'] = element
#    drdq_params['mass'] = mass
#    drdq_params[model] = sigmap
#    drdq_params[coupling] = fnfp
#    drdq_params['delta'] = delta
#    drdq_params['GF'] = GF
#    drdq_params['time_info'] = time_info
#
#    time_list = np.zeros_like(er_list)
#    dm_spec = dRdQ(er_list, time_list, **drdq_params) * 10. ** 3. * s_to_yr

    ax.set_xlabel(r'Electron Recoil Energy  [keV]', fontsize=fs)
    ax.set_ylabel(r'Event Rate  [${\rm ton}^{-1} {\rm yr}^{-1} {\rm keV}^{-1}$]', fontsize=fs)

    for i in range(nu_contrib):
        pl.plot(er_list, nuspec[i], color_list[i], ls=line_list[i], lw=1, label=nu_labels[i])
        if sve_data:
            np.savetxt(test_plots + 'Electron_Recoils_in_' + element + '_' + nu_comp[i] + '_.dat', np.column_stack((er_list, nuspec[i])))

    bkg_list = bkg_electron_specs(element)
    for j,nme in enumerate(bkg_list):
        pl.plot(er_list, NEUTRINO_SPEC[nme](er_list/1e3), color_list_2[j], lw=1, label=ELEC_BKG_TAG[nme])

#    pl.plot(er_list, dm_spec, 'b', lw=1, label='Dark Matter')
#    print 'Number of dark matter events: ', np.trapz(dm_spec, er_list)
    plt.tight_layout()

    plt.xlim(xmin=Emin, xmax=Emax)
    plt.ylim(ymin=10.**-6., ymax=2*10.**2.)
    ax.set_xscale("log")
    ax.set_yscale("log")

    plt.legend(loc=1, frameon=True, framealpha=0.5, fontsize=9, ncol=1, fancybox=True)

    if save:
        plt.savefig(filename)
    return


def DM_DiffRate(Emin=0.001, Emax=100., element='Germanium', fs=18, save=True,
                    mass=6., sigmap=4.*10**-45., model='sigma_si', fnfp=1.,
                    delta=0., GF=False, time_info=False, xenlab='LZ', geo_analysis=False):
    coupling = "fnfp" + model[5:]

    filename = test_plots + 'DM_DiffRate_Recoils_in_' + element + '_'
    filename += model + '_' + coupling + '_{:.2f}'.format(fnfp)
    filename += '_DM_mass_{:.2f}_CSec_{:.2e}_Delta_{:.2f}'.format(mass, sigmap, delta)
    if element == 'xenon':
        filename += xenlab + '_'
    filename += '.pdf'

    er_list = np.logspace(np.log10(Emin), np.log10(Emax), 500)

    experiment_info, Qmin, Qmax = Element_Info(element)
    lab = laboratory(element, xen=xenlab, geo_analysis=geo_analysis)

    color_list = ['#800080', '#000080', '#000080', '#8A2BE2', '#A52A2A', '#A0522D', '#DC143C', '#B8860B',
                  '#8B008B', '#556B2F', '#FF8C00', '#9932CC', '#E9967A', '#FF1493', '#696969', '#228B22',
                  '#40E0D0', '#CD5C5C', '#90EE90','#90EE90']
    line_list = ['-', '--', '--', '-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-', '-','-']


    coupling = "fnfp" + model[5:]

    drdq_params = default_rate_parameters.copy()
    drdq_params['element'] = element
    drdq_params['mass'] = mass
    drdq_params[model] = sigmap
    drdq_params[coupling] = fnfp
    drdq_params['delta'] = delta
    drdq_params['GF'] = GF
    drdq_params['time_info'] = time_info

    time_list = np.zeros_like(er_list)
    dm_spec = dRdQ(er_list, time_list, **drdq_params) * 10. ** 3. * s_to_yr

    pl.figure()
    ax = pl.gca()

    ax.set_xlabel(r'Recoil Energy  [keV]', fontsize=fs)
    ax.set_ylabel(r'Event Rate  [${\rm ton}^{-1} {\rm yr}^{-1} {\rm keV}^{-1}$]', fontsize=fs)

    pl.plot(er_list, dm_spec, 'b', lw=1, label='Dark Matter')
    print 'Number of dark matter events: ', np.trapz(dm_spec, er_list)
    plt.tight_layout()

    plt.xlim(xmin=Emin, xmax=Emax)
    plt.ylim(ymin=10.**-5., ymax=10.**8.)
    ax.set_xscale("log")
    ax.set_yscale("log")

    plt.legend(loc=1, frameon=True, framealpha=0.5, fontsize=9, ncol=1, fancybox=True)

    if save:
        plt.savefig(filename)
    return


def test_sims(esim, e_list, dm, nu):
    pl.figure()
    ax = pl.gca()
    ax.set_xlabel(r'Recoil Energy  [keV]', fontsize=18)
    ax.set_ylabel(r'Event Rate  [${\rm ton}^{-1} {\rm yr}^{-1} {\rm keV}^{-1}$]', fontsize=18)

    pl.plot(e_list, dm, 'r', lw=1, label='Dark Matter')
    pl.plot(e_list, nu, 'blue', lw=1, label='Neutrino')


    bin = np.linspace(np.min(e_list), 2., 100)
    ax.hist(esim, bins=bin, normed=True, histtype='step', fc=None, ec='Black', lw=2)

    plt.tight_layout()

    plt.xlim(xmin=np.min(e_list), xmax=2.)
    ax.set_xscale("log")

    plt.savefig(test_plots + 'TEST.pdf')
    return


def number_dark_matter(element='Xenon', model='sigma_si', exposure=1., mass=10., sigma=1e-40,
                       fnfp=1., delta=0., GF=False, time_info=False):
    experiment_info, Qmin, Qmax = Element_Info(element)
    coupling = "fnfp" + model[5:]

    er_list = np.logspace(np.log10(Qmin), np.log10(Qmax), 100)

    drdq_params = default_rate_parameters.copy()
    drdq_params['element'] = element
    drdq_params[model] = sigma
    drdq_params[coupling] = fnfp
    drdq_params['delta'] = delta
    drdq_params['GF'] = GF
    drdq_params['time_info'] = time_info
    drdq_params['mass'] = mass
    spectrum = dRdQ(er_list, np.zeros_like(er_list), **drdq_params)
    rate = np.trapz(spectrum, er_list) * exposure * 3.154*10.**7. * 1e3

    print 'Element: ', element
    print 'Model: ', model, ' Mass {:.2f} Sigma: {:.2e}'.format(mass, sigma)
    print 'Dark Matter Events: {:.2f}'.format(rate)
    return

