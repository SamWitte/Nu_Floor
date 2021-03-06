"""

Code info:

"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import quad
from scipy.integrate import romberg
from rate_UV import *
from helpers import *
import os
import time
from experiments import *
from constants import *
import copy

path = os.getcwd()


gF = 1.16637 * 10. ** -5. # Gfermi in GeV^-2
sw = 0.2312 # sin(theat_weak)^2
MeVtofm = 0.0050677312
s_to_yr = 3.154*10.**7.


class Likelihood_analysis(object):

    def __init__(self, model, coupling, mass, dm_sigp, fnfp, exposure, element, isotopes,
                 energies, times, nu_names, lab, nu_spec, er_nu, nu_d_response, nu_response,
                 Qmin, Qmax, delta=0., time_info=False, GF=False,
                 DARK=True, reduce_uncer=1., uncertain_dict={}):

        self.nu_lines = ['b7l1', 'b7l2', 'pepl1']
        self.line = [0.380, 0.860, 1.440]
        self.reduce_uncer = reduce_uncer

        self.nu_diff_evals = np.zeros(nu_spec, dtype=object)
        self.nu_resp = np.zeros(nu_spec, dtype=object)
        self.nu_int_resp = np.zeros(nu_spec, dtype=object)
        er = np.zeros(nu_spec, dtype=object)
        nu_resp_h = np.zeros(nu_spec, dtype=object)
        for i in range(nu_spec):
            er[i] = er_nu[i][nu_d_response[i] > 0]
            nu_resp_h[i] = nu_d_response[i][nu_d_response[i] > 0]
            self.nu_resp[i] = interp1d(np.log10(er[i]), np.log10(nu_resp_h[i]),
                                       kind='cubic', bounds_error=False,
                                       fill_value=-100.)
            self.nu_int_resp[i] = nu_response[i]
            self.nu_diff_evals[i] = 10. ** self.nu_resp[i](np.log10(energies))


        self.events = energies

        self.element = element
        self.mass = mass
        self.dm_sigp = dm_sigp
        self.exposure = exposure

        self.Qmin = Qmin
        self.Qmax = Qmax

        self.nu_spec = nu_spec
        self.nu_names = nu_names
        self.lab = lab

        self.times = times

        like_params = default_rate_parameters.copy()

        like_params['element'] = element
        like_params['mass'] = mass
        like_params[model] = dm_sigp
        like_params[coupling] = fnfp
        like_params['GF'] = GF
        like_params['time_info'] = time_info
        like_params['delta'] = delta

        if DARK:
            self.dm_recoils = dRdQ(energies, times, **like_params) * 10.**3. * s_to_yr
            self.dm_integ = R(Qmin=self.Qmin, Qmax=self.Qmax, **like_params) * 10.**3. * s_to_yr
        else:
            self.dm_recoils = np.zeros_like(energies)
            self.dm_integ = 0.

        for i in uncertain_dict:
            NEUTRINO_SIG[i] = uncertain_dict[i]

    def like_nu_bound(self, normsDM, normsNu):
        nu_norm = np.zeros(self.nu_spec, dtype=object)
        for i in range(self.nu_spec):
            nu_norm[i] = normsNu[i]
        sig_dm = normsDM
        likeDM = self.likelihood(nu_norm, sig_dm, SkipPnlty=True)
        return likeDM
    
    def like_nu_bnd_jac(self, norms, noDML, qval=2.7):
        nu_norm = np.zeros(self.nu_spec, dtype=object)
        for i in range(self.nu_spec):
            nu_norm[i] = norms[i]
        sig_dm = norms[-1]
        likeDM = self.likelihood(nu_norm, sig_dm)
        jacTerm = self.likegrad_multi_wrapper(norms)
        termX = likeDM - noDML - qval
        if termX > 0:
            return jacTerm
        else:
            return -jacTerm

    def like_multi_wrapper(self, norms, grad=False):
        nu_norm = np.zeros(self.nu_spec, dtype=object)
        for i in range(self.nu_spec):
            nu_norm[i] = norms[i]
        sig_dm = norms[-1]
        return self.likelihood(nu_norm, sig_dm)

    def like_multi_wrapper2(self, norms1, norms2, normdm, idnu=False):
        sig_dm = normdm
        nu_norm = np.concatenate((norms1, norms2))
        if idnu:
            skparr = np.asarray(range(len(norms1), len(norms1)+len(norms2)))
        else:
            skparr = np.array([])
        return self.likelihood(nu_norm, sig_dm, skip_index=skparr, SkipPnlty=True)

    def like_multi_wrapper2_grad(self, norms1, norms2, normdm, idnu=False):
        if idnu:
            skparr = np.asarray(range(len(norms1), len(norms1)+len(norms2)))
        else:
            skparr = np.array([])

        return self.like_gradi(norms1, normdm, skip_index=skparr)

    def test_num_events(self, nu_norm, sig_dm):
        print 'DM events Predicted: ', 10. ** sig_dm * self.dm_integ * self.exposure
        for i in range(self.nu_spec):
            nu_events = 10. ** nu_norm[i] * self.exposure * self.nu_int_resp[i]
            print 'Events from ' + self.nu_names[i] + ': ', nu_events
        return

    def likelihood(self, nu_norm, sig_dm, skip_index=np.array([]), SkipPnlty=False):
        # - 2 log likelihood
        # nu_norm in units of cm^-2 s^-1, sig_dm in units of cm^2

        like = 0.
        diff_nu = np.zeros(self.nu_spec, dtype=object)
        nu_events = np.zeros(self.nu_spec, dtype=object)

        n_obs = len(self.events)
        # total rate contribution

        dm_events = 10. ** sig_dm * self.dm_integ * self.exposure
        
        for i in range(self.nu_spec):
            nu_events[i] = 10. ** nu_norm[i] * self.exposure * self.nu_int_resp[i]
#            print self.nu_names[i], nu_events[i]
#        print 'DM Events: ', dm_events

        like += 2. * (dm_events + sum(nu_events))

        # nu normalization contribution
        if not SkipPnlty:
            for i in range(self.nu_spec):
                test1 = i not in skip_index
                test2 = nu_norm[i] > 0
                if test1 or test2:
                    like += self.nu_gaussian(self.nu_names[i], nu_norm[i])

        if self.element == 'Fluorine':
            return like

        # Differential contribution
        diff_dm = self.dm_recoils * self.exposure

        lg_vle = (10. ** sig_dm * diff_dm)
        for i in range(self.nu_spec):
            diff_nu[i] = self.nu_diff_evals[i] * self.exposure * 10.**nu_norm[i]
            lg_vle += diff_nu[i]

        for i in range(len(lg_vle)):
            like += -2. * np.log(lg_vle[i])
        return like
    
    def likelihood_electronic(self, nu_norm, sig_dm, skip_index=np.array([]), SkipPnlty=False):
        # - 2 log likelihood
        # nu_norm in units of cm^-2 s^-1, sig_dm in units of cm^2

        like = 0.
        diff_nu = np.zeros(self.nu_spec, dtype=object)
        nu_events = np.zeros(self.nu_spec, dtype=object)

        n_obs = len(self.events)
        # total rate contribution

        dm_events = 10. ** sig_dm * self.dm_integ * self.exposure
        for i in range(self.nu_spec):
            nu_events[i] = 10. ** nu_norm[i] * self.exposure * self.nu_int_resp[i]

        like += 2. * (dm_events + sum(nu_events))

        # nu normalization contribution
        if not SkipPnlty:
            for i in range(self.nu_spec):
                if i not in skip_index:
                    like += self.nu_gaussian(self.nu_names[i], nu_norm[i])

        if self.element == 'Fluorine':
            return like

        # Differential contribution
        diff_dm = self.dm_recoils * self.exposure

        lg_vle = (10. ** sig_dm * diff_dm)
        for i in range(self.nu_spec):
            diff_nu[i] = self.nu_diff_evals[i] * self.exposure * 10.**nu_norm[i]
            lg_vle += diff_nu[i]
        
        for i in range(len(lg_vle)):
            like += -2. * np.log(lg_vle[i])
        return like

    def likegrad_multi_wrapper(self, norms):
        nu_norm = np.zeros(self.nu_spec, dtype=object)
        for i in range(self.nu_spec):
            nu_norm[i] = norms[i]
        sig_dm = norms[-1]
        return self.like_gradi(nu_norm, sig_dm, ret_just_nu=False)

    def like_gradi(self, nu_norm, sig_dm, skip_index=np.array([]), ret_just_nu=True,
                    ret_just_dm=False, SkipPnlty=False):
        grad_x = 0.
        diff_nu = np.zeros(len(nu_norm), dtype=object)
        grad_nu = np.zeros(len(nu_norm))
        nu_events = np.zeros(len(nu_norm), dtype=object)

        dm_events = 10. ** sig_dm * self.dm_integ * self.exposure
        grad_x += 2. * np.log(10.) * dm_events

        for i in range(len(nu_norm)):
            grad_nu[i] += 2. * np.log(10.) * 10.**nu_norm[i] * self.exposure * self.nu_int_resp[i]

        if not SkipPnlty:
            for i in range(len(nu_norm)):
                test1 = i not in skip_index
                test2 = nu_norm[i] > 0
                if test1 or test2:
                    grad_nu[i] += self.nu_gaussian(self.nu_names[i], nu_norm[i], return_deriv=True)

        if self.element != 'fluorine':
            diff_dm = self.dm_recoils * self.exposure
            lg_vle = (10. ** sig_dm * diff_dm)
            for i in range(len(nu_norm)):
                diff_nu[i] = self.nu_diff_evals[i] * self.exposure * 10.**nu_norm[i]
                lg_vle += diff_nu[i]

            for i in range(len(lg_vle)):
                grad_x += -2. * np.log(10.) * diff_dm[i] * 10. ** sig_dm / lg_vle[i]
            for i in range(len(nu_norm)):
                for j in range(len(lg_vle)):
                    grad_nu[i] += -2. * np.log(10.) * diff_nu[i][j] / lg_vle[j]

        if ret_just_nu:
            return grad_nu
        else:
            if ret_just_dm:
                return np.array([grad_x])
            else:
                return np.concatenate((grad_nu, np.array([grad_x])))

    def neutrino_poisson_likelihood(self, nu_norm, bins=10):
        # - 2 log likelihood
        # nu_norm in units of cm^-2 s^-1, sig_dm in units of cm^2

        bedge = np.linspace(self.Qmin, self.Qmax, bins+1)

        n_count = np.zeros(bins)
        pred = np.zeros(bins)
        like = 0.
        for i in range(bins):
            erg = np.logspace(np.log10(bedge[i]), np.log10(bedge[i + 1]), 100)

            n_count[i] = ((self.events > bedge[i]) & (bedge[i+1] > self.events)).sum()
            for j in range(self.nu_spec):
                pred[i] += 10.**nu_norm[j] * self.exposure * np.trapz(10.**self.nu_resp[j](np.log10(erg)), erg)

        like = 2. * (pred - n_count * np.log(pred)).sum()
        return like

    def neutrino_poisson_grad(self, nu_norm, bins=10):
        # - 2 log likelihood
        # nu_norm in units of cm^-2 s^-1, sig_dm in units of cm^2
        bedge = np.linspace(self.Qmin, self.Qmax, bins+1)
        n_count = np.zeros(bins)
        pred = np.zeros(bins*len(nu_norm)).reshape((bins, len(nu_norm)))
        deriv = np.zeros(len(nu_norm))
        for i in range(bins):
            erg = np.logspace(np.log10(bedge[i]), np.log10(bedge[i+1]), 100)
            n_count[i] = len(self.events[(self.events > bedge[i]) & (bedge[i+1] < self.events)])
            for j in range(self.nu_spec):
                pred[i, j] += 10.**nu_norm[j] * self.exposure * np.trapz(10.**self.nu_resp[j](np.log10(erg)), erg)

        prefactor = 2. * (1. - n_count / np.sum(pred, axis=1))
        for j in range(self.nu_spec):
            deriv[j] += np.dot(prefactor, pred[:, j] * np.log(10.))

        return deriv


    def nu_gaussian(self, nu_component, flux_n, return_deriv=False, err_multiply=True):
        # - 2 log of gaussian flux norm comp

        if nu_component == "reactor":
            nu_mean_f, nu_sig = reactor_flux(loc=self.lab)
        elif nu_component == "geoU":
            nu_mean_f, nu_sig = geo_flux(loc=self.lab, el='U')
        elif nu_component == "geoTh":
            nu_mean_f, nu_sig = geo_flux(loc=self.lab, el='Th')
        elif nu_component == "geoK":
            nu_mean_f, nu_sig = geo_flux(loc=self.lab, el='K')
        else:
            nu_mean_f = NEUTRINO_MEANF[nu_component]
            nu_sig = NEUTRINO_SIG[nu_component]
        if err_multiply:
            #print nu_component, nu_sig, nu_sig*self.reduce_uncer
            nu_sig *= self.reduce_uncer
        if return_deriv:
            return nu_mean_f**2./nu_sig**2.*(10.**flux_n - 1.) * \
                       np.log(10.)*2.**(flux_n + 1.)*5.**flux_n
        else:
            return nu_mean_f**2. * (10. ** flux_n - 1.)**2. / nu_sig**2.


class Nu_spec(object):
    # Think about defining some of these neutino parameters as variables in constants.py (e.g. mean flux)
    def __init__(self, lab):
        self.lab = lab
        self.nu_lines = ['b7l1', 'b7l2','pepl1']
        self.line = [0.380, 0.860, 1.440]


    def nu_spectrum_enu(self, nu_component, emin=0.1):
        if 'atm' in nu_component:
            e_nu_min = 13. + 1e-3
        elif nu_component == 'reactor':
            e_nu_min = 0.5 + 1e-3
        else:
            e_nu_min = emin

        e_nu_max = NEUTRINO_EMAX[nu_component] + 1.

        e_list = np.logspace(np.log10(e_nu_min), np.log10(e_nu_max), 500)
        if nu_component == "reactor":
            nu_mean_f = reactor_flux(loc=self.lab)[0]
        elif nu_component == "geoU":
            nu_mean_f = geo_flux(loc=self.lab, el='U')[0]
        elif nu_component == "geoTh":
            nu_mean_f = geo_flux(loc=self.lab, el='Th')[0]
        elif nu_component == "geoK":
            nu_mean_f = geo_flux(loc=self.lab, el='K')[0]
        else:
            nu_mean_f = NEUTRINO_MEANF[nu_component]

        if nu_component not in self.nu_lines:
            return e_list, NEUTRINO_SPEC[nu_component](e_list) * nu_mean_f
        else:
            for i in range(len(self.line)):
                if nu_component == self.nu_lines[i]:
                    return np.array([self.line[i],self.line[i]+1e-5,self.line[i]-1e-5]), np.array([0.,nu_mean_f,0.])


    def nu_rate(self, nu_component, er, element_info):

        mT, Z, A, xi = element_info
        conversion_factor = xi / mT * s_to_yr * (0.938 / (1.66 * 10.**-27.)) \
                            * 10**-3. / (0.51 * 10.**14.)**2.

        diff_rate = np.zeros_like(er)
        for i,e in enumerate(er):
            if 'atm' in nu_component:
                e_nu_min = 13.
            elif nu_component == 'reactor':
                e_nu_min = 0.5
            else:
                e_nu_min = np.sqrt(mT * e / 2.)

            e_nu_max = NEUTRINO_EMAX[nu_component]
            if nu_component == "reactor":
                nu_mean_f = reactor_flux(loc=self.lab)[0]
            elif nu_component == "geoU":
                nu_mean_f = geo_flux(loc=self.lab, el='U')[0]
            elif nu_component == "geoTh":
                nu_mean_f = geo_flux(loc=self.lab, el='Th')[0]
            elif nu_component == "geoK":
                nu_mean_f = geo_flux(loc=self.lab, el='K')[0]
            else:
                nu_mean_f = NEUTRINO_MEANF[nu_component]

            if nu_component not in self.nu_lines:
                ergs = np.logspace(np.log10(e_nu_min), np.log10(e_nu_max), 100)
                diff_rate[i] = np.trapz(self.nu_recoil_spec(ergs, e, mT, Z, A, nu_component), ergs)
                #diff_rate[i] = romberg(self.nu_recoil_spec, e_nu_min, e_nu_max, args=(e, mT, Z, A, nu_component))

            else:
                for j in range(len(self.line)):
                    if nu_component == self.nu_lines[j]:
                        diff_rate[i] = self.nu_recoil_spec(self.line[j], e, mT, Z, A, nu_component)

            diff_rate[i] *= nu_mean_f * conversion_factor

        return diff_rate
    
    def nu_rate_electronic(self, nu_component, er, element_info, elem):

        mT, Z, A, xi = element_info
        
        mass_e = 5.11e-4
        conversion_factor = Z * xi / mT * s_to_yr * (0.938 / (1.66 * 10.**-27.)) \
                            * 10**-3. / (0.51 * 10.**14.)**2.

        diff_rate = np.zeros_like(er)
        for i,e in enumerate(er):
            if 'atm' in nu_component:
                e_nu_min = 13.
            elif nu_component == 'reactor':
                e_nu_min = 0.5
            else:
                e_nu_min = 0.5*(e*1e-3 + np.sqrt((e*1e-3)**2. + 2.*mass_e * e))

            # WHAT TO DO WITH THIS
            e_nu_max = NEUTRINO_EMAX[nu_component]
            
            if nu_component == "reactor":
                nu_mean_f = reactor_flux(loc=self.lab)[0]
            elif nu_component == "geoU":
                nu_mean_f = geo_flux(loc=self.lab, el='U')[0]
            elif nu_component == "geoTh":
                nu_mean_f = geo_flux(loc=self.lab, el='Th')[0]
            elif nu_component == "geoK":
                nu_mean_f = geo_flux(loc=self.lab, el='K')[0]
            else:
                nu_mean_f = NEUTRINO_MEANF[nu_component]

            if nu_component not in self.nu_lines:
                ergs = np.logspace(np.log10(e_nu_min), np.log10(e_nu_max), 600)
                diff_rate[i] = np.trapz(self.nu_electron_recoil_spec(ergs, e, nu_component), ergs)

            else:
                for j in range(len(self.line)):
                    if nu_component == self.nu_lines[j]:
                        diff_rate[i] = self.nu_electron_recoil_spec(self.line[j], e, nu_component)
            
            diff_rate[i] *= nu_mean_f * conversion_factor
        
        return diff_rate

    def max_er_from_nu(self, enu, mT):
        return 2. * enu**2. / (mT + 2. * enu * 1e-3)

    def nu_recoil_spec(self, enu, er, mT, Z, A, nu_comp):
        if nu_comp in self.nu_lines:
            for i in range(len(self.line)):
                if enu == self.line[i] and nu_comp == self.nu_lines[i]:
                    return self.nu_csec(enu, er, mT, Z, A)
        else:
            return self.nu_csec(enu, er, mT, Z, A) * NEUTRINO_SPEC[nu_comp](enu)

    def nu_electron_recoil_spec(self, enu, er, nu_comp):
        if nu_comp in self.nu_lines:
            for i in range(len(self.line)):
                if enu == self.line[i] and nu_comp == self.nu_lines[i]:
                    return self.nu_electron_xsec(enu, er, nu_comp)
        else:
            
            return self.nu_electron_xsec(enu, er, nu_comp) * NEUTRINO_SPEC[nu_comp](enu)

    def nu_csec(self, enu, er, mT, Z, A):
        # enu can be array, er cannot be
        Qw = (A - Z) - (1. - 4. * sw) * Z
        if type(enu) is not np.ndarray:
            enu = np.array([enu])
        ret = np.zeros_like(enu)
        for i,en in enumerate(enu):
            if er < self.max_er_from_nu(en, mT):
                ret[i] = gF ** 2. / (4. * np.pi) * Qw**2. * mT * \
                        (1. - mT * er / (2. * en**2.)) * self.helm_ff(er, A, Z, mT)
        return ret

    def helm_ff(self, er, A, Z, mT):
        q = np.sqrt(2. * mT * er) * MeVtofm
        if ((1.23*A**0.33 - 0.6)**2. +7*np.pi/3.*0.52**2. - 5*0.9**2.) <= 0:
            R1 = 1.
        else:
            R1 = np.sqrt((1.23*A**0.33 - 0.6)**2. +7*np.pi/3.*0.52**2. - 5*0.9**2.)
        j1 = np.sin(q*R1)/(q*R1)**2. - np.cos(q*R1)/(q*R1)
        ff = (3*j1/(q*R1))**2.*np.exp(-(q*5*0.9**2.)**2)
        return ff

    def nu_electron_xsec(self, enu, er, nu_comp):
        if nu_comp == 'b8':
            SF = 0.35
            fracSV = [SF, 1. - SF]
        else:
            fracSV = [0.55, 1. - 0.55]
    
        mass_e = 5.11e-4

        if type(enu) is not np.ndarray:
            enu = np.array([enu])
        ret = np.zeros_like(enu)
        
        if nu_comp == 'reactor' or 'geo' in nu_comp:
            couplings_x = [[2. * sw, 2. * sw + 1.] , [2. * sw, 2. * sw - 1.]]
        else:
            couplings_x = [[2. * sw + 1., 2. * sw] , [2. * sw - 1., 2. * sw]]
        
        for j in range(2):
            ge_1 = couplings_x[j][0]
            ge_2 = couplings_x[j][1]
            
            for i,en in enumerate(enu):
                if er < self.max_er_from_nu(en, mass_e):
                    ret[i] += fracSV[j] * gF ** 2. / (2. * np.pi) * mass_e * (ge_1**2. +
                            ge_2**2.*(1. - er/en*1e-3)**2. + ge_1*ge_2*mass_e*er/en**2.)
        return ret

