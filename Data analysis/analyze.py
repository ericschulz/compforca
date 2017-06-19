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

##############################################################
##                     JSON PROCESSING                      ##
##############################################################

# Creates all the Subjects' objects and returns a list
def create_subjects():
    participants = []

    for subjectId in dataset.keys():
        participants.append(Subject(dataset[subjectId]))

    return participants

# Plots all the curves (Stage II) associated to a target variable
# variable: (String) name of the variable to be plotted
# trend: (String) {'stable', 'up', 'down'}
# noiseIndex: Integer {0, 1, 2}. Which of the three noise sets to target
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
def CatmullRomChain(points):
  """
  Calculate Catmull Rom for a chain of points and return the combined curve.
  """
  points = add_border_points(points)

  size = len(points)

  # The curve C will contain an array of (x,y) points.
  C = []
  for i in range(size-3):
    c = CatmullRomSpline(points[i], points[i+1], points[i+2], points[i+3])

    C.extend(c)

  return C

def add_border_points( points ):
    # Get the change in x and y between the first and second coordinates.
    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]

    #Then using the change, extrapolate backwards to find a control point.
    x1 = points[0][0] - dx
    y1 = points[0][1] - dy

    # Create the start point from the extrapolated values.
    start = [x1, y1]

    # Repeat for the end control point.
    n = len(points) - 1
    dx = points[n][0] - points[n - 1][0] / 1000
    dy = points[n][1] - points[n - 1][1] / 1000

    xn = points[n][0] + dx
    yn = points[n][1] + dy
    end = [xn, yn]

    #insert the start control point at the start of the points list.
    final_points = [start] + points

    # append the end control ponit to the end of the points list.
    final_points.append(end)

    return final_points

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
    points = CatmullRomChain(data)

    trace = points_to_trace(points)

    plotly.offline.plot([trace], filename='basic-line')

# Start:
plotCatmull([[0,0],[10,10],[11,5],[20,20], [21, -10], [30, 30]])
subjects = create_subjects()
