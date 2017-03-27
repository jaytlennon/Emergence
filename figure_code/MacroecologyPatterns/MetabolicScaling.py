from __future__ import division
import  matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import scipy as sc
from scipy import stats
import statsmodels.stats.api as sms
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import summary_table


def xfrm(X, _max): return -np.log10(_max-np.array(X))


def figplot(x, y, xlab, ylab, fig, n):
    
    fig.add_subplot(3, 3, n)
    x = np.log10(x)
    y = np.log10(y)
    y2 = list(y)
    x2 = list(x)

    #X, Y = (np.array(t) for t in zip(*sorted(zip(x2, y2))))
    #Xi = xfrm(X, max(X)*1.05)
    #bins = np.linspace(np.min(Xi), np.max(Xi)+1, 400)
    #ii = np.digitize(Xi, bins)
    #y2 = np.array([np.mean(Y[ii==i]) for i in range(1, len(bins)) if len(Y[ii==i]) > 0])
    #x2 = np.array([np.mean(X[ii==i]) for i in range(1, len(bins)) if len(X[ii==i]) > 0])

    d = pd.DataFrame({'size': list(x2)})
    d['rate'] = list(y2)
    f = smf.ols('rate ~ size', d).fit()

    coef = f.params[1]
    st, data, ss2 = summary_table(f, alpha=0.05)
    fitted = data[:,2]
    mean_ci_low, mean_ci_upp = data[:,4:6].T
    ci_low, ci_upp = data[:,6:8].T

    x2, y2, fitted, ci_low, ci_upp = zip(*sorted(zip(x2, y2, fitted, ci_low, ci_upp)))

    plt.scatter(x2, y2, color = 'SkyBlue', alpha= 1 , s = 12, linewidths=0.5, edgecolor='Steelblue')
    plt.fill_between(x2, ci_upp, ci_low, color='b', lw=0.1, alpha=0.15)
    plt.plot(x2, fitted,  color='b', ls='--', lw=1.0, alpha=0.9)
    plt.xlabel(xlab, fontsize=9)
    plt.ylabel(ylab, fontsize=9)
    plt.tick_params(axis='both', labelsize=6)
    plt.xlim(0.9*min(x2), 1.1*max(x2))
    plt.ylim(min(ci_low), max(ci_upp))
    plt.title('$z$ = '+str(round(coef, 2)), fontsize=10)
    return fig



mydir = os.path.expanduser('~/GitHub/simplex')
tools = os.path.expanduser(mydir + "/tools")

df = pd.read_csv(mydir + '/results/simulated_data/SimData.csv')
#df = df[df['ct'] > 200]

df2 = pd.DataFrame({'length' : df['length'].groupby(df['sim']).mean()})
df2['N'] = df['total.abundance'].groupby(df['sim']).mean()
df2['NS'] = df['avg.pop.size'].groupby(df['sim']).mean()

state = 'all'
df2['Biomass'] = df[state+'.biomass'].groupby(df['sim']).median()
df2['size'] = df[state+'.size'].groupby(df['sim']).mean()
df2['M'] = df[state+'.avg.per.capita.maint'].groupby(df['sim']).mean()

df2['Na'] = df['N.active'].groupby(df['sim']).mean()
df2['Ma'] = df['active.avg.per.capita.maint'].groupby(df['sim']).mean()
df2['MFa'] = df['active.avg.per.capita.mf'].groupby(df['sim']).mean()
df2['Nd'] = df['N.dormant'].groupby(df['sim']).mean()
df2['Md'] = df['dormant.avg.per.capita.maint'].groupby(df['sim']).mean()
df2['MFd'] = df['dormant.avg.per.capita.mf'].groupby(df['sim']).mean()
df2['Mw'] = df2['Ma']*(df2['Na']/df2['N']) + df2['Md']*(df2['Nd']/df2['N'])

df2['B'] =  df2['M'] * df2['size']
df2['MSB'] = df2['B']/df2['size']
df2['Pdens'] = df2['Biomass']/(df2['length']**2)

#df2 = df2[np.log10(df2['Pdens']) > -10]
df2 = df2[np.log10(df2['size']) < 10]

df2 = df2.replace([np.inf, -np.inf], np.nan).dropna()

fig = plt.figure()
xlab = r"$log_{10}$"+'(Body size)'
ylab = r"$log_{10}$"+'(Metabolic rate)'
fig = figplot(df2['size'], df2['B'], xlab, ylab, fig, 1)

xlab = r"$log_{10}$"+'(Body size)'
ylab = r"$log_{10}$"+'(Mass specific rate)'
fig = figplot(df2['size'], df2['MSB'], xlab, ylab, fig, 2)

xlab = r"$log_{10}$"+'(Body size)'
ylab = r"$log_{10}$"+'(Pop. density)'
fig = figplot(df2['size'], df2['Pdens'], xlab, ylab, fig, 3)

plt.subplots_adjust(wspace=0.4, hspace=0.4)
plt.savefig(mydir + '/results/figures/MetabolicScaling.png', dpi=200, bbox_inches = "tight")