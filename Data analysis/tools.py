
# coding: utf-8

# # Libraries

# In[1]:

import GPflow
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import tensorflow as tf
get_ipython().magic('matplotlib inline')

import csv
import time
import copy
import json
import pandas as pd
import scipy as sp
import scipy.stats
import random
import copy

Xpredictions = np.linspace(31, 1426, 280)[:,None]

# In[5]:

# Transformation of array to matrix
def array_to_matrix(x):
    X = []
    for i in range(len(x)):
        X.append([float(x[i])])
    X = np.array(X)
    return X


# # Gaussian Processes
# Docs:
# - [GP Regression](http://gpflow.readthedocs.io/en/latest/notebooks/regression.html)

# In[6]:

def compute(X, Y, kernel_name, full_bayesian = False, prior_gps = []):
    # Get kernel
    if not full_bayesian:
        kernel = get_new_kernel(kernel_name)
    else:
        kernel = get_full_bayesian_new_kernel(kernel_name, prior_gps)

        # If a White Kernel was added in the prior, set it to different values
        if prior_gps[kernel_name]['white_added']:
            kernel.white.variance = 0.05
            kernel.white.variance.prior = None
            kernel.white.fixed = True

    model = GPflow.gpr.GPR(X, Y, kern = kernel)

    white_added = False
    second_exception = False

    # If the kernel already has a White Kernel, prevent a second one being added on top of it.
    if len(prior_gps) > 0:
        if prior_gps[kernel_name]['white_added']:
            white_added = True

    try:
        #print('Begin optimization of kernel: ' + kernel_name)
        model.optimize()
    except:

        if not white_added:
            # Add white kernel
            white_added = True

            w = GPflow.kernels.White(1, variance = 0.05)
            w.variance.fixed = True
            model = GPflow.gpr.GPR(X, Y, kern = kernel + w)

        try:
            print('Adding White Kernel to', kernel_name)
            model.optimize()
        except:
            second_exception = True
            print('Exception caught computing', kernel_name)

    return {'model': model, 'white_added': white_added, 'second_exception': second_exception}


# In[7]:

def lml(model):
    """Log marginal likelihood of a GP"""

    try:
        return model.compute_log_likelihood()
    except:
        print('Exception caught in lml')
        return -999999999


# In[8]:

def predict(gps, X):
    predictions = {}

    # For every GP, build predictions
    for key in gps.keys():

        try:
            mean, var = gps[key]['model'].predict_y(X)
        except:
            print('Exception caught in predict')
            mean, var = np.array([0]), np.array([0])

        predictions[key] = {'mean': mean.tolist(),
                            'var': var.tolist()}

    return predictions


# In[9]:

def get_new_kernel(kernel_string):
    # Initial new non-optimized kernels
    l = GPflow.kernels.Linear(1)
    p = GPflow.kernels.PeriodicKernel(1)
    r = GPflow.kernels.RBF(1)

    if   kernel_string == 'l': return l
    elif kernel_string == 'p': return p
    elif kernel_string == 'r': return r

    elif kernel_string == 'l+r': return  l+r
    elif kernel_string == 'l+p': return  l+p
    elif kernel_string == 'p+r': return  p+r

    elif kernel_string == 'l*r': return  l*r
    elif kernel_string == 'l*p': return  l*p
    elif kernel_string == 'p*r': return  p*r

    elif kernel_string == 'l+r+p': return l+r+p
    elif kernel_string == 'l+r*p': return l+r*p
    elif kernel_string == 'l*r+p': return l*r+p
    elif kernel_string == 'l*p+r': return l*p+r
    elif kernel_string == 'l*r*p': return l*r*p

    else: return 'error'


# In[10]:

## From Stackoverflow. https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects ##
import functools

def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

sentinel = object()
def rgetattr(obj, attr, default=sentinel):
    if default is sentinel:
        _getattr = getattr
    else:
        def _getattr(obj, name):
            return getattr(obj, name, default)
    return functools.reduce(_getattr, [obj]+attr.split('.'))
## End copy-paste ##


# In[11]:

#s_kernel: string kernel
def get_kernel_attributes(s_kernel, results):
    x0 = s_kernel.find('kern')
    x1 = s_kernel.find('\x1b[1m') # end of the kernel name
    x2 = s_kernel.find('\x1b[0m') # end of variable name

    new_result = s_kernel[x0 : x1] + s_kernel[x1+4 : x2]

    results.append(new_result)

    new_s_kernel = s_kernel[(x2+1) : ]

    if new_s_kernel.find('kern') == -1:
        return results
    else:
        return get_kernel_attributes(new_s_kernel, results)


# In[12]:

# GP Model
# String of the variable to change
def set_variable(kernel, s_variable, new_value, set_prior=False):
    #Remove the first part
    s_variable = s_variable[s_variable.find('.')+1 : ]

    if set_prior:
        s_variable = s_variable + '.prior'

    rsetattr(kernel, s_variable, new_value)


# In[13]:

#Returns the value of a specific variable within a kernel
def get_value(kernel, s_variable):
    #Remove the first part
    s_variable = s_variable[s_variable.find('.')+1 : ]

    # Return the value
    return rgetattr(kernel, s_variable).value[0]


# In[14]:

def get_full_bayesian_new_kernel(kernel_name, prior_gps):

    # The structure of this object is :
    # {'model': <GPflow.gpr.GPR object at 0x000001B2C940CFD0>, 'white_added': False, 'second_exception': False}
    gp_result = copy.deepcopy(prior_gps[kernel_name])

    kernel = gp_result['model'].kern

    # Get all the variables of the kernel
    all_variables = get_kernel_attributes(str(kernel), [])

    # Move the values to the Priors and reset the values
    for variable in all_variables:
        # Get the value
        value = get_value(kernel, variable)

        # Set the value in the prior
        prior = GPflow.priors.Gaussian(value, 1.)
        set_variable(kernel, variable, prior, set_prior = True)

        # Set the value to 1
        set_variable(kernel, variable, 1.)

    return kernel


# In[15]:

def normalize(Y):
    std = np.std(Y)
    mu = np.mean(Y)

    return ((Y - mu)/std)



# In[16]:

def compute_gps(X, Y0, full_bayesian = False, prior_gps = []):
    # Subtract the mean
    Y = Y0 - np.mean(Y0)

    gps = {}

    gps['l'] = compute(X, Y, 'l', full_bayesian, prior_gps)
    gps['p'] = compute(X, Y, 'p', full_bayesian, prior_gps)
    gps['r'] = compute(X, Y, 'r', full_bayesian, prior_gps)

    gps['l+r'] = compute(X, Y, 'l+r', full_bayesian, prior_gps)
    gps['l+p'] = compute(X, Y, 'l+p', full_bayesian, prior_gps)
    gps['p+r'] = compute(X, Y, 'p+r', full_bayesian, prior_gps)

    gps['l*r'] = compute(X, Y, 'l*r', full_bayesian, prior_gps)
    gps['l*p'] = compute(X, Y, 'l*p', full_bayesian, prior_gps)
    gps['p*r'] = compute(X, Y, 'p*r', full_bayesian, prior_gps)

    gps['l+r+p'] = compute(X, Y, 'l+r+p', full_bayesian, prior_gps)
    gps['l+r*p'] = compute(X, Y, 'l+r*p', full_bayesian, prior_gps)
    gps['l*r+p'] = compute(X, Y, 'l*r+p', full_bayesian, prior_gps)
    gps['l*p+r'] = compute(X, Y, 'l*p+r', full_bayesian, prior_gps)
    gps['l*r*p'] = compute(X, Y, 'l*r*p', full_bayesian, prior_gps)

    return gps


# In[17]:

def compute_lmls(models):
    lmls = {}
    for key in models.keys():
        e = {
            'lml': lml(models[key]['model']),
            'white_added': models[key]['white_added'],
            'second_exception': models[key]['second_exception']
            }
        lmls[key] = e

    return lmls


# In[18]:

def gps_to_string(gps):
    strings = {}
    for key in gps.keys():
        strings[key] = str(gps[key])

    return strings


# In[19]:

def dict_max(d):
    maxval = max(d.values())
    keys = [k for k,v in d.items() if v==maxval]
    return keys, maxval


# In[20]:

def save_results(results, filename, new_format):

    if not new_format:
        with open('output/' + filename + '.json', 'w') as fp:
            json.dump(results, fp)

    else:
        #lmls: pid, composition, lml, white_added, second_exception
        with open('output/' + filename + '_lmls.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            #title
            writer.writerow(['pid', 'composition', 'lml', 'white_added', 'second_exception'])

            for pid in results['lmls']:
                for composition in results['lmls'][pid]:
                    writer.writerow([
                                     pid,
                                     composition,
                                     results['lmls'][pid][composition]['lml'],
                                     results['lmls'][pid][composition]['white_added'],
                                     results['lmls'][pid][composition]['second_exception']
                                    ])

        #Xpredictions #predictions
        with open('output/' + filename + '_predictions.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            #title
            writer.writerow(['pid', 'composition', 'Xpredictions', 'predictions_mean', 'predictions_var'])

            for pid in results['predictions']:
                for composition in results['predictions'][pid]:
                    for index, element in enumerate(results['predictions'][pid][composition]['mean']):
                        writer.writerow([
                                         pid,
                                         composition,
                                         results['Xpredictions'][index][0],
                                         #results['predictions'][pid][composition]['mean'][index][0],
                                         #results['predictions'][pid][composition]['var'][index][0]
                                         results['predictions'][pid][composition]['mean'][index],
                                         results['predictions'][pid][composition]['var'][index]
                                        ])



# Compute Gaussian Process Models for a dataset

# In[21]:

def compute_gps_for_dataset(dataset, Xpredictions=Xpredictions, full_bayesian = False, dataset_posterior = []):
    t0 = time.time()

    ids = np.unique(dataset['f0'])

    gpss_objects = {}
    gpss = {}
    predictions = {}
    lmls = {}
    maxs = {}

    for i in ids:
        print(i)
        # Filter the relevant data
        filtered_data = dataset[dataset['f0'] == i]

        # Get X and Y
        X = array_to_matrix(filtered_data['f3'])
        Y = array_to_matrix(filtered_data['f4'])

        # Compute GPs
        gps = compute_gps(X, Y)

        print('First Compute OK')

        # Full Bayesian condition
        if full_bayesian:
            # Filter the relevant data
            filtered_data = dataset_posterior[dataset_posterior['f0'] == i]

            # Get X and Y
            X = array_to_matrix(filtered_data['f3'])
            Y = array_to_matrix(filtered_data['f4'])

            # Compute de GPs AGAIN. However, use the data of the previous optimization as a prior to do so.
            gps = compute_gps(X, Y, full_bayesian = True, prior_gps = gps)

            print('Full-Bayesian Compute OK')

        # Calculate the log marginal likelihoods
        likelihoods = compute_lmls(gps)
        print('LMLs OK')

        # Calculate the predictions of the GPs
        gps_predictions = predict(gps, Xpredictions)
        print('Predictions OK')

        # Save
        i = str(i)
        #gpss_objects[i] = gps
        predictions[i] = gps_predictions
        lmls[i] = likelihoods


    print('Minutes:', str(round((time.time() - t0) / 60)))

    return {
            #'gpss_objects': gpss_objects, #Actual objects
            'Xpredictions': Xpredictions.tolist(),
            'predictions': predictions,
            'lmls': lmls
           }


# In[22]:

def plot(X, Y, mean, var):
    xx = Xpredictions
    plt.clf()
    plt.figure(figsize=(12, 6))
    plt.plot(X, Y, 'kx', mew=2)
    plt.plot(xx, mean, 'b', lw=2)
    plt.fill_between(xx[:,0], mean[:,0] - 2*np.sqrt(var[:,0]), mean[:,0] + 2*np.sqrt(var[:,0]), color='blue', alpha=0.2)
    plt.xlim(31, 365*4)
    #plt.ylim(-2, 2)


# In[23]:

def plot_predictions(results, data, target_id, target_kernel):

    dat = data[data['f0'] == target_id]

    X = array_to_matrix(dat['f3'])
    Y = normalize(array_to_matrix(dat['f4']))

    mean = np.array(results['predictions'][str(target_id)][target_kernel]['mean'])
    var = np.array(results['predictions'][str(target_id)][target_kernel]['var'])

    plot(X, Y, mean, var)


# # Compute Gaussian Processes

# In[24]:

def debug_filtering(dataset):
    #dataset = dataset[dataset['f0'] == 59]
    #dataset = dataset[dataset['f0'] < 3 ]

    return dataset


# In[25]:

def scenario(dataset, scenario):
    return dataset[dataset['f2'] == scenario]


# ### Compare the best kernel composition SSE versus those of `l` and `r`

# Functions

# In[ ]:

def get_posterior_curve(cid):
    cid = int(cid)
    dataset = data_posterior

    # Filter the relevant data
    filtered_data = dataset[dataset['f0'] == cid]

    # Get X and Y
    x = filtered_data['f3']
    y = filtered_data['f4']

    df = pd.DataFrame([x, y]).T

    df.columns=["x", "y"]

    return df


# In[ ]:

def get_posterior_prediction(cid, kernel_name):
    # Get the target values
    x = Xpredictions

    y = results_posterior['predictions'][cid][kernel_name]['mean']

    y_var = results_posterior['predictions'][cid][kernel_name]['var']

    # Squeeze the matrices
    x = np.squeeze(x); y = np.squeeze(y); y_var = np.squeeze(y_var);

    df = pd.DataFrame([x, y, y_var]).T

    df.columns=["x", "y", "y_var"]

    return df


# In[ ]:

def get_y_value(df, x):
    return df[df['x']==x]['y'].tolist()[0]


# In[ ]:

def compute_SSE(true_dataframe, prediction_dataframe, minX = 365-31):

    df1 = true_dataframe[true_dataframe['x'] > minX]
    df2 = prediction_dataframe[prediction_dataframe['x'] > minX]

    sse = 0

    for x in df1['x'] :
        error = get_y_value(df1, x) - get_y_value(df2, x)
        sse += (error*error)

    # Root mean squared deviation
    rmsd = np.sqrt(sse / len(df1))

    # Normalized
    return rmsd / (np.max(df1['y']) - np.min(df1['y']))


# End functions


# In[ ]:

def mean_confidence_interval(data, confidence=0.99):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h
