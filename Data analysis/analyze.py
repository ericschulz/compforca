# exec(open('C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/analyze.py').read())
# s = subjects[0]
# pip install plotly


##############################################################
##                        LIBRARIES                         ##
##############################################################

# Library to read json files.
import json

# Library to plot graphs
import plotly
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go

# Datetime
import datetime

import numpy



##############################################################
##                    INITIAL VARIABLES                     ##
##############################################################

# Dataset variables
filepath = 'C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/bayesian-forecasting-export.json'
dataset = json.load(open(filepath, 'r'))

#subjects = create_subjects()

##############################################################
##                     JSON PROCESSING                      ##
##############################################################

# Creates all the Subjects' objects and returns a list
def create_subjects():
    participants = []

    for subjectId in dataset.keys():
        participants.append(Subject(dataset[subjectId]))

    return participants

def plot_variable(variable, trend='stable', noiseIndex=0):
    # Get the responses for the target variable
    target_responses = responses(variable, trend, noiseIndex)

    # Generate the plotly traces for those responses
    traces = []
    for r in target_responses:
        traces.append(r.get_trace())

    # Plot the trends in one plot
    plotly.offline.plot(traces, filename='line-mode')


# Returns all the responses for a certain variable, with a specific trend and noise
# trend = {'up', 'stable', 'down'}.  noise = {0, 1, 2}
def responses(variable, trend='stable', noiseIndex=0):
    # Participants with the target noise
    participants = subjects_noise(noiseIndex)

    # Responses with the target variable and trend
    responses = []

    for p in participants:
        # Get the response for the target variable, at stage 2, of the target trend
        r = p.get_response(variable, 2, trend)

        if r != 'not found':
            responses.append(r)

    return responses



# Get all the subjects of the target noise. noise = {1,2,3}
def subjects_noise(noiseIndex):
    array = []

    for s in subjects:
        if s.get_noise_index() == noiseIndex:
            array.append(s)

    return array

# Plots the data for a certain Prolific ID:
def plot_pid( prolificId ):
    get_subject_pid(prolificId).plot()

# Returns the subject with the target Prolific ID
def get_subject_pid( prolificId ):
    for s in subjects:
        if s.userId == prolificId:
            return s

# Prints the invalid subjects
def print_invalid_subjects():
    for s in subjects:
        if not s.is_valid():
            print(s.userId)


##############################################################
##                          TOOLS                           ##
##############################################################

def get_range( variable ):
  if variable == "temperature":
      return [-10, 40]
  elif variable == "sales":
      return [0, 5000]
  elif variable == "facebook_friends":
      return [0, 1000]
  elif variable == "rain":
      return [0, 100]
  elif variable == "gym_memberships":
      return [0, 50]
  elif variable == "wage":
      return [0, 50]

# Returns a list with all the variables' names
def get_variables():
    return ['temperature', 'rain', 'sales', 'gym_memberships', 'wage', 'facebook_friends']

# Returns the number of participants
def get_number_of_subjects():
    return len(subjects)

##############################################################
##                         SUBJECT                          ##
##############################################################

class Subject:
    """A subject that participated in the experiment"""

    def __init__(self, subjectData):
        self.rawData = subjectData
        self.__processSubjectRawData()

    # Processes the raw data received in the constructor
    def __processSubjectRawData( self ):
        self.userId = self.rawData['userId']
        self.sessionId = self.rawData['sessionId']
        self.age = self.rawData['age']
        self.datetime = self.rawData['datetime']
        self.gender = self.rawData['gender']
        self.rawResponses = self.rawData['historicalData']

        self.responses = self.__processResponses(self.rawResponses)

    # Processes the raw reponses by constructing a Response object for each
    def __processResponses( self, rawResponses ):
        responses = []

        for response in rawResponses:
            # Appends the response object to the list
            responses.append(Response(response))

        return responses

    #################### GETTERS ####################


    # Returns the processed responses for a specific variable and stage
    def get_response( self, variable, stage, subcondition='' ):

        # For each variable, check if the search is finished. If it is, return that.
        for r in self.responses:
            if r.condition == variable and r.stage == stage :
                # If the subcondition is not empty, then check for equivalence
                if subcondition != '':
                    if r.get_subcondition_name() == subcondition:
                        return r
                else:
                    return r

        # If this point is reached, then the response was not found
        return 'not found'

    # Returns the items of a specific response/plot
    def get_response_items( self, variable, stage, subcondition=''):
        return self.get_response(variable, stage, subcondition).items


    # Returns true if the subject is valid for analysis
    def is_valid( self ):
        return len(self.responses) == 12

    # Returns the index of the noise set that was used:
    def get_noise_index( self ):
        # TODO: in the next version, this parameter is being saved in the experiment as 'noiseArray'
        # Get the items for the rain
        r = self.get_response_items('rain', 2)

        if round(r['y'][1], 5) == round(33.4532551009561, 5) or round(r['y'][1], 5) == round(21.5467448990438, 5) or round(r['y'][1], 5) == round(38.4532551009561, 5):
            return 0
        elif round(r['y'][1], 5) == round(29.0657829744368, 5) or round(r['y'][1], 5) == round(25.9342170255631, 5) or round(r['y'][1], 5) == round(34.0657829744368, 5):
            return 1
        elif round(r['y'][1], 5) == round(38.5965838655708, 5) or round(r['y'][1], 5) == round(16.4034161344291, 5) or round(r['y'][1], 5) == round(43.5965838655708, 5):
            return 2
        else:
            return 'error'

        #print (str(r['y'][0]) + ',' + str(r['y'][1]) + ',' + str(r['y'][2]) + ',' + str(r['y'][3]) + ',' + str(r['y'][4]))

    # Displays a plot for a single subject, and a single variable
    # variable can be {rain, gym_memberships, temperature, wage, facebook_friends, sales}
    def traces_variable( self, variable ):
        # Get the traces for the same variable, stage 1 and stage 2
        trace1 = self.get_response(variable, 1).get_trace()
        trace2 = self.get_response(variable, 2).get_trace()

        return [trace1, trace2]

    # Plots all the subject's responses
    def plot( self ):
        traces = []
        subplot_titles = []

        for v in get_variables():
            # Create a pair of traces for each variable
            traces.append( self.traces_variable(v) )

            # Prepare the subtitles for each little graph
            subplot_titles.append(v.title())
            subplot_titles.append('Stage 2 (' + self.get_response(v, 2).get_subcondition_name() + ')')

        # Add the subtitles
        fig = tools.make_subplots(rows=6, cols=2, subplot_titles=(subplot_titles))

        # Put the traces in position
        for index in range(0, len(traces)):
            fig.append_trace(traces[index][0], index+1, 1)
            fig.append_trace(traces[index][1], index+1, 2)

        # Modify the ranges of the y-axis
        for index in range( 0, len(get_variables()) ):
            # First and second stage yaxis
            first = 'yaxis' + str(index * 2 + 1)
            second = 'yaxis' + str(index * 2 + 2)

            # Update the ranges
            fig['layout'][first].update(range = get_range(get_variables()[index]) )
            fig['layout'][second].update(range = get_range(get_variables()[index]) )

        # Set up the dimensions of the plot
        fig['layout'].update(height=2400, width=1400, title='Prolific ID: ' + self.userId)

        # Plot the graphs
        plotly.offline.plot(fig, filename='make-subplots-multiple-with-titles')

##############################################################
##                         RESPONSE                         ##
##############################################################

class Response:
    """A subject's response to one variable"""

    def __init__( self, responseData ):
        self.rawData = responseData
        self.__processResponseRawData()

    def __processResponseRawData( self ):
        self.timestamp = self.rawData['now']
        self.datetime =  self.rawData['datetime']
        self.condition = self.rawData['condition']
        self.subcondition = self.rawData['subCondition']
        self.pageIndex = self.rawData['pageIndex']

        self.rawItems = self.rawData['items']
        self.orderedRawItems = sorted(self.rawItems, key=lambda k: k['x']) # Sort the data by date
        self.items = self.__processItems(self.orderedRawItems)

        self.stage = self.__get_stage(self.pageIndex)

    # Processes the items raw data to a dictionary {'x': xdata, 'y': ydata}
    def __processItems( self, rawItems ):
        xdata = []
        ydata = []

        for item in rawItems:
            # Append the y data point (transformed to a Date object)
            xdata.append(self.transform_date(item['x']))

            # Append the x data point (transformed to float)
            ydata.append(float(item['y']))

        return {'x': xdata, 'y': ydata}

    # Returns the trace of the response, for plotly
    def get_trace( self ):
        return go.Scatter(
                x = self.items['x'],
                y = self.items['y'],
                mode = 'lines+markers',
                name = 'Stage ' + str(self.stage),
                line = dict(
                    shape='spline'
                )
            )


    # Receives a date string with format "yyyy-mm-dd" and returns the
    # corresponding Date object
    def transform_date( self, dateString ):
        # Exception protection. Movement of one day. TODO: This should be fixed on the experiment itself.
        if dateString == '0000-12-31':
            dateString = '0001-01-01'

        return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

    # Returns a stage (1 or 2) given a pageIndex (integer)
    def __get_stage( self, pageIndex ):
        if pageIndex <= 7:
            return 1
        elif pageIndex <= 13:
            return 2
        else:
            return "error"

    # Returns the name of the subcondition
    def get_subcondition_name( self ):
        if self.subcondition == 1:
            return 'up'
        elif self.subcondition == 2:
            return 'stable'
        elif self.subcondition == 3:
            return 'down'
        else:
            return 'error'


##############################################################
##                         LIBRARIES                        ##
##############################################################

# Source: Wikipedia, https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
def CatmullRomSpline(P0, P1, P2, P3, nPoints=10):
    """
    P0, P1, P2, and P3 should be (x,y) point pairs that define the Catmull-Rom spline.
    nPoints is the number of points to include in this curve segment.
    """
    # Convert the points to numpy so that we can do array multiplication
    P0, P1, P2, P3 = map(numpy.array, [P0, P1, P2, P3])

    # Calculate t0 to t4
    alpha = 0.5
    def tj(ti, Pi, Pj):
        xi, yi = Pi
        xj, yj = Pj
        return ( ( (xj-xi)**2 + (yj-yi)**2 )**0.5 )**alpha + ti

    t0 = 0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    #nPoints = numpy.sqrt ( numpy.power(P2[0]-P1[0], 2) + numpy.power(P2[1]-P1[1], 2) )

    # Only calculate points between P1 and P2
    t = numpy.linspace(t1,t2,nPoints)

    # Reshape so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    t = t.reshape(len(t),1)

    A1 = (t1-t)/(t1-t0)*P0 + (t-t0)/(t1-t0)*P1
    A2 = (t2-t)/(t2-t1)*P1 + (t-t1)/(t2-t1)*P2
    A3 = (t3-t)/(t3-t2)*P2 + (t-t2)/(t3-t2)*P3

    B1 = (t2-t)/(t2-t0)*A1 + (t-t0)/(t2-t0)*A2
    B2 = (t3-t)/(t3-t1)*A2 + (t-t1)/(t3-t1)*A3

    C  = (t2-t)/(t2-t1)*B1 + (t-t1)/(t2-t1)*B2
    return C

# Source: Wikipedia, https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
def CatmullRomChain(P):
  """
  Calculate Catmull Rom for a chain of points and return the combined curve.
  """
  sz = len(P)

  # The curve C will contain an array of (x,y) points.
  C = []
  for i in range(sz-3):
    c = CatmullRomSpline(P[i], P[i+1], P[i+2], P[i+3])

    C.extend(c)

  return C


# Returns the distances on the x-axis between two points
def x_distance( p0, p1 ):
    return numpy.abs(p0[0] - p1[0])

# vim.js implementation, translated to Python
def _catmullRom (data, alpha=0.5):
    if alpha == 0:
        return 'uniform'
    else:
        #var p0, p1, p2, p3, bp1, bp2, d1, d2, d3, A, B, N, M;
        #var d3powA, d2powA, d3pow2A, d2pow2A, d1pow2A, d1powA;
        d = []
        #d.append( [ numpy.round(data[0][0]) , numpy.round(data[0][1]) ])
        d.append( data[0] )

        length = len(data)
        for i in range(length - 1):
            p0 = data[0] if i == 0 else data[i - 1]
            p1 = data[i]
            p2 = data[i + 1]
            p3 = data[i + 2] if (i + 2 < length) else p2

            d1 = numpy.sqrt(numpy.power(p0[0] - p1[0], 2) + numpy.power(p0[1] - p1[1], 2))
            d2 = numpy.sqrt(numpy.power(p1[0] - p2[0], 2) + numpy.power(p1[1] - p2[1], 2))
            d3 = numpy.sqrt(numpy.power(p2[0] - p3[0], 2) + numpy.power(p2[1] - p3[1], 2))

            # Catmull-Rom to Cubic Bezier conversion matrix

            # A = 2d1^2a + 3d1^a * d2^a + d3^2a
            # B = 2d3^2a + 3d3^a * d2^a + d2^2a

            # [   0             1            0          0          ]
            # [   -d2^2a /N     A/N          d1^2a /N   0          ]
            # [   0             d3^2a /M     B/M        -d2^2a /M  ]
            # [   0             0            1          0          ]

            d3powA = numpy.power(d3, alpha)
            d3pow2A = numpy.power(d3, 2 * alpha)
            d2powA = numpy.power(d2, alpha)
            d2pow2A = numpy.power(d2, 2 * alpha)
            d1powA = numpy.power(d1, alpha)
            d1pow2A = numpy.power(d1, 2 * alpha)

            A = 2 * d1pow2A + 3 * d1powA * d2powA + d2pow2A
            B = 2 * d3pow2A + 3 * d3powA * d2powA + d2pow2A

            N = 3 * d1powA * (d1powA + d2powA)
            if (N > 0):
                N = 1 / N

            M = 3 * d3powA * (d3powA + d2powA)
            if (M > 0):
                M = 1 / M

            bp1 = [
                ((-d2pow2A * p0[0] + A * p1[0] + d1pow2A * p2[0]) * N),
                ((-d2pow2A * p0[1] + A * p1[1] + d1pow2A * p2[1]) * N)
            ]

            bp2 = [
                (( d3pow2A * p1[0] + B * p2[0] - d2pow2A * p3[0]) * M),
                (( d3pow2A * p1[1] + B * p2[1] - d2pow2A * p3[1]) * M)
            ]

            if (bp1[0] == 0 and bp1[1] == 0):
                bp1 = p1

            if (bp2[0] == 0 and bp2[1] == 0):
                bp2 = p2

            d.append( bp1 )
            d.append( bp2 )
            d.append( p2 )

        return d

# Transforms an array of points to a trace:
def points_to_trace( points ):
    x = []
    y = []

    for p in points:
        x.append(p[0])
        y.append(p[1])

    trace = go.Scatter(
        x = x,
        y = y,
        mode = 'lines+markers'
    )

    return trace


def plotCatmull( data ):
    points = _catmullRom(data)

    points_2 = bezier_curve(points)

    #trace = points_to_trace(points_2)

    trace = go.Scatter(
        x = points_2[0],
        y = points_2[1],
        mode='lines+markers'
    )

    plotly.offline.plot([trace], filename='basic-line')

#######################

def factorial(n):
    if n == 0:
        return 1

    f = 1
    for i in range(n):
        f = (i+1) * f
    return f

def comb(n, k):
    return factorial(n) / factorial(k) / factorial(n - k)

def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezier_curve(points, nTimes=10):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.

       points should be a list of lists, or list of tuples
       such as [ [1,1],
                 [2,3],
                 [4,5], ..[Xn, Yn] ]
        nTimes is the number of time steps, defaults to 1000

        See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = numpy.array([p[0] for p in points])
    yPoints = numpy.array([p[1] for p in points])

    t = numpy.linspace(0.0, 1.0, nTimes)

    polynomial_array = numpy.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

    xvals = numpy.dot(xPoints, polynomial_array)
    yvals = numpy.dot(yPoints, polynomial_array)

    return xvals, yvals

plotCatmull([[0,0],[10,10],[11,5],[20,20],[20.1,20]])