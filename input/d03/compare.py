import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# Opacity to extinction

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

RATIO = {}
RATIO['3.1_6.0'] = 1.870E-26
RATIO['4.0_4.0'] = 1.969E-26
RATIO['5.5_3.0'] = 2.199E-26

for model in ['3.1_6.0', '4.0_4.0', '5.5_3.0']:

    orig = np.loadtxt('d03_{model}_A.orig'.format(model=model))
    ax.loglog(orig[:, 0], orig[:, 3], color='black', lw=1)

    wav = np.loadtxt('d03_{model}_A/d03_{model}_A.wav'.format(model=model))
    new = np.loadtxt('d03_{model}_A/d03_{model}_A.chi'.format(model=model))
    ax.loglog(wav, new * RATIO[model], color='red', lw=1)

fig.savefig('comparison_chi.png')

# Average scattering angle

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for model in ['3.1_6.0', '4.0_4.0', '5.5_3.0']:

    orig = np.loadtxt('d03_{model}_A.orig'.format(model=model))
    ax.plot(orig[:, 0], orig[:, 2], color='black', lw=1)

    wav = np.loadtxt('d03_{model}_A/d03_{model}_A.wav'.format(model=model))
    new = np.loadtxt('d03_{model}_A/d03_{model}_A.g'.format(model=model))
    ax.plot(wav, new, color='red', lw=1)

ax.set_xscale('log')
fig.savefig('comparison_g.png')

# Albedo

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for model in ['3.1_6.0', '4.0_4.0', '5.5_3.0']:

    orig = np.loadtxt('d03_{model}_A.orig'.format(model=model))
    ax.plot(orig[:, 0], orig[:, 1], color='black', lw=1)

    wav = np.loadtxt('d03_{model}_A/d03_{model}_A.wav'.format(model=model))
    new = np.loadtxt('d03_{model}_A/d03_{model}_A.alb'.format(model=model))
    ax.plot(wav, new, color='red', lw=1)

ax.set_xscale('log')
fig.savefig('comparison_albedo.png')
