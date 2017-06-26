# exec(open('C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/analyze.py').read())
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
import plotly.figure_factory as ff

import scipy

# Datetime
import datetime

import numpy



##############################################################
##                    INITIAL VARIABLES                     ##
##############################################################

# Dataset variables
filepath = 'C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/bayesian-forecasting-export.json'
dataset = json.load(open(filepath, 'r'))

plotly.offline.init_notebook_mode()

##############################################################
##                     JSON PROCESSING                      ##
##############################################################

# Creates all the Subjects' objects and returns a list
def create_subjects():
    participants = []

    for subjectId in dataset.keys():
        participants.append(Subject(dataset[subjectId]))

    return participants


# Returns all the responses for a certain variable, with a specific trend and noise
# trend = {'up', 'stable', 'down'}.  noise = {0, 1, 2}
# filter: whether to filter out participants that are not valid
def responses(variable, filter=False, stage=1, trend='stable', noiseIndex=0):
    # Participants
    participants = get_subjects(filter)

    # Responses with the target stage, variable, trend, and noiseIndex
    responses = []

    for p in participants:
        # Get the response for the target variable, at Stage II, of the target trend
        r = p.get_response(variable, stage, trend)

        # If the response was successfully found
        if r != 'not found':
            # And if we are interested in Stage II, we also have to check the noiseIndex
            if (stage == 2 and r.noiseIndex == noiseIndex) or stage==1:
                responses.append(r)

    return responses

# Creates a CSV with the following structure, in columns:
# UserID, Condition, Subcondition, Random Set, [x, y]
def generate_csv():
    participants = get_subjects()

    # Create new file (if it exists, it will rewrite it)
    file = open('catmull-rom-dataset.csv', 'w')

    # Titles:
    titles = 'userId, age, datetime, gender,'

    responsesTitles = 'timestamp,datetime,stage,condition,subcondition,pageIndex,noiseIndex,'

    for index in range(len(get_variables() * 2)):
        titles += responsesTitles

        for index in range(365*4+20):
            titles += 'Day ' + str(index) + ','

    file.write(titles)

    # Write each participant in a new line
    for p in participants:
        file.write(p.get_as_csv() + '\n')

    # Close the file
    file.close()


# Plots the data for a certain User ID:
# spline: set to True if instead of showing only the participant's points,
# the spline points should be calculated and shown too.
def plot_pid( userId, spline=False):
    get_subject_pid(userId).plot(spline)

# Returns the subject with the target User ID
def get_subject_pid( userId ):
    for s in get_subjects():
        if s.userId == userId:
            return s

# Prints the invalid subjects
def print_invalid_subjects():
    for s in all_subjects:
        if not s.is_valid():
            print(s.userId + ': ' + str(s.is_valid_verbose()))

# Returns the list of subjects
# One can decide whether to filter out those participants that are deemed not valid.
def get_subjects( filterNotValidSubjects = False ):
    if filterNotValidSubjects:
        list = []

        for s in all_subjects:
            if s.is_valid():
                list.append(s)

        return list

    else:
        return all_subjects

##############################################################
##                   ALL PARTICIPANTS ANALYSIS              ##
##############################################################

# Plots ALL the variables
def plot_variables(filter=False, oneColor=True):
    all_variables_traces = []
    subplot_titles = []

    # Build the traces and the subtitles
    for v in get_variables():
        # Stage I subtitle
        subplot_titles.append(v.title())

        # This list will hold several lists of traces
        variable_traces = []

        # Stage I traces
        variable_traces.append(get_traces_variable(v, filter, oneColor=oneColor))

        # Stage II
        for subcondition in get_subconditions():
            # Traces
            variable_traces.append( get_traces_variable(v, filter, 2, subcondition, 0, oneColor=oneColor) +
                                    get_traces_variable(v, filter, 2, subcondition, 1, oneColor=oneColor) +
                                    get_traces_variable(v, filter, 2, subcondition, 2, oneColor=oneColor) )

            # Subtitles
            subplot_titles.append('Stage 2 (' + subcondition + ')')

        # Append the traces to the 'all traces' variable
        all_variables_traces.append(variable_traces)

    # Create the plot
    colsCount = 4
    fig = tools.make_subplots(rows=6, cols=colsCount, subplot_titles=(subplot_titles), print_grid=False)

    # Put the traces in position
    for i in range(len(all_variables_traces)):
        # Append all the traces to that figure:
        for j in range(len(all_variables_traces[i])):

            # Traces for a specific variable, in a specific situation
            traces = all_variables_traces[i][j]

            # For all the traces, append it to the figure:
            for t in traces:
                fig.append_trace(t, i+1, j+1)


    # Modify the ranges of the y-axis
    for index in range(len(get_variables())):
        # For every column
        for col in range(colsCount):
            # Identify the plot
            plot_identifier = 'yaxis' + str(index * colsCount + col + 1)

            # Update the range
            fig['layout'][plot_identifier].update(range = get_range(get_variables()[index]) )

    # Set up the dimensions of the plot
    fig['layout'].update(height=2400, width=1200, title='Responses')

    # Plot the graphs
    plotly.offline.plot(fig, filename='jupyter/all_responses.html')


# Plots all the curves (Stage II) associated to a target variable
# variable: (String) name of the variable to be plotted
# trend: (String) {'stable', 'up', 'down'}
# noiseIndex: Integer {0, 1, 2}. Which of the three noise sets to target
def plot_variable(variable, filter=False, stage=1, trend='stable', noiseIndex=0, oneColor=False):
    # Get the traces
    traces = get_traces_variable(variable, filter, stage, trend, noiseIndex, oneColor=oneColor)

    # Plot the trends in one plot
    plotly.offline.iplot(traces, filename='jupyter/plot_variable.html')

def get_traces_variable(variable, filter=False, stage=1, trend='stable', noiseIndex=0, oneColor=False):
    # Get the responses for the target variable
    target_responses = responses(variable, filter, stage, trend, noiseIndex)

    # Generate the plotly traces for those responses
    traces = []
    for r in target_responses:
        traces.append(r.get_trace(showUserId=True, oneColor=oneColor))

    return traces


# Returns a list with the number of items each participants added for a
# certain variable in a certain stage
# filter: (Boolean) if True, if filters the participants who are NOT valid
def items_count( variable, stage, filter=False):
    # Get the responses for the target variable
    target_responses = responses(variable, filter, stage)

    # Generate the item's count for each response
    counts = []
    for r in target_responses:
        # Append the number of points that the participant added on that plot
        counts.append(r.get_participant_items_count())

    return counts

# Prints a histogram for all the variables count on a certain stage
def stage_items_count_histogram( stage, filter=False ):
    counts_list = []

    # Get the items count for every variable, for a target stage
    variables = get_variables()
    for v in variables:
        # Get and append the items' count for a specific variable
        counts_list.append(items_count(v, stage, filter))

    title = "Histogram of Items' Count: Stage " + str(stage)

    # Show the histogram
    show_histogram(counts_list, variables, title)

# Prints a histogram for all the variables count on a certain stage
def variable_items_count_histogram( variable, filter=False ):
    counts_list = []

    # Get the counts for Stage I and II
    counts_list.append(items_count(variable, 1, filter))
    counts_list.append(items_count(variable, 2, filter))

    # Build labels
    labels = [ get_label(variable, 1), get_label(variable, 2) ]

    title = "Histogram of Items' Count: " + get_label(variable)

    # Show the histogram
    show_histogram(counts_list, labels, title)


##############################################################
##                          TOOLS                           ##
##############################################################

def show_histogram(data, labels, title):
    # Build the histogram
    fig = ff.create_distplot(data, labels, show_rug=False,
                             histnorm='probability', curve_type='normal')

    fig['layout'].update(title=title, xaxis=dict(range=[0, 50]))

    plotly.offline.iplot(fig, filename='jupyter/histogram.html')


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

def get_subconditions():
    return ['up', 'stable', 'down']

# Return the label for a certain variable+stage
def get_label(variable, stage=0):
    if stage == 0:
        return variable.title()
    else:
        return 'Stage ' + str(stage) + ' (' + variable.title() + ')'

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
        self.__process_subject_raw_data()

    # Processes the raw data received in the constructor
    def __process_subject_raw_data( self ):
        self.userId = self.rawData['userId']
        self.sessionId = self.rawData['sessionId']
        self.age = self.rawData['age']
        self.datetime = self.rawData['datetime']
        self.gender = self.rawData['gender']
        self.rawResponses = self.rawData['historicalData']

        self.responses = self.__process_responses(self.rawResponses)

        self.__set_other_variables()

    # Processes the raw reponses by constructing a Response object for each
    def __process_responses( self, rawResponses ):
        responses = []

        for response in rawResponses:
            # Appends the response object to the list
            responses.append(Response(response))

        return responses

    # Sets the value of other variables that are relevant to the Response
    def __set_other_variables( self ):
        # Now that all the responses have been created, calculate the noiseIndex
        noiseIndex = self.get_noise_index()
        # And set the noiseIndex to every response
        for r in self.responses:
            r.noiseIndex = noiseIndex
            r.userId = self.userId


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

    # Returns the Subject as a CSV line
    def get_as_csv( self ):
        csvArray = [
                    self.userId,
                    self.age,
                    self.datetime,
                    self.gender,
                   ]

        # Add the responses to the array
        for v in get_variables():
             # Stage I
            csvArray += self.get_response(v, 1).get_as_array()

        for v in get_variables():
             # Stage II
            csvArray += self.get_response(v, 2).get_as_array()

        return array_to_csv(csvArray)

    # Returns the items of a specific response/plot
    def get_response_items( self, variable, stage, subcondition=''):
        return self.get_response(variable, stage, subcondition).items

    # Returns true if the subject is valid for analysis
    def is_valid( self ):
        return self.is_valid_verbose() == True

    # Returns True if the participant is valid. If not, it returns a String
    # explaining why not.
    def is_valid_verbose ( self ):
        if len(self.responses) != 12:
            return 'Participant did not answer the twelve plots.'

        if self.userId == 'a106':
            return 'Participant misunderstood the instructions and always added a point on the far right and far bottom.'

        if self.userId == 'a021':
            return 'Response in Temperature (constant -10) indicates a non-interested participant.'

        if self.userId == 'a118':
            return 'Participant indicated that he had trouble with the interface.'

        return True

    # Returns the index of the noise set that was used:
    def get_noise_index( self ):
        # TODO: in the next version, this parameter is being saved in the experiment as 'noiseArray'
        # Get the items for the rain (it could be anyone of them)
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
    # spline: (Boolean) defines whether the Traces are for the Spline or not
    def traces_variable( self, variable, spline=False ):
        # Get the traces for the same variable, stage 1 and stage 2
        trace1 = self.get_response(variable, 1).get_trace(spline, hoverinfo='all')
        trace2 = self.get_response(variable, 2).get_trace(spline, hoverinfo='all')

        return [trace1, trace2]

    # Plots all the subject's responses
    # spline: determines whether or not to calculate the Spline for the responses
    def plot( self, spline=False):
        traces = []
        subplot_titles = []

        # Build the traces and the titles
        for v in get_variables():
            # Create a pair of traces for each variable
            traces.append( self.traces_variable(v, spline) )

            # Prepare the subtitles for each little graph
            subplot_titles.append(v.title())
            subplot_titles.append('Stage 2 (' + self.get_response(v, 2).get_subcondition_name() + ')')

        # Add the subtitles
        fig = tools.make_subplots(rows=6, cols=2, subplot_titles=(subplot_titles), print_grid=False)

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
        fig['layout'].update(height=1200, width=800, title='Prolific ID: ' + self.userId)

        # Plot the graphs
        plotly.offline.iplot(fig, filename='jupyter/subject_responses.html')

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
    def get_trace( self, spline=False, showUserId=False, hoverinfo='none', oneColor=False):

        # If showUserId is True, then the name of the Trace should be the userId
        traceName = self.userId if showUserId else 'Stage ' + str(self.stage)

        # Line color and alpha
        lineOptions = dict(shape='spline')
        if oneColor:
            lineOptions['color'] = 'rgba(205, 12, 24, 0.4)'

        # If spline is True, then return the spline's Trace object
        if spline:
            return self.get_spline_trace()
        else:
            return go.Scatter(
                    x = self.items['x'],
                    y = self.items['y'],
                    mode = 'lines+markers',
                    name = traceName,
                    line = lineOptions,
                    hoverinfo = hoverinfo,
                    showlegend = not oneColor
                )

    # Returns the trace of the spline
    def get_spline_trace( self ):
        # Calculate the Catmull-Rom spline, and then transform the points to a Trace
        return self.__points_to_trace(self.get_catmull_rom())

    # Returns the number of items
    def get_items_count( self ):
        # If the lengths of the 'x' and 'y' lists are equivalent (they SHOULD be)
        if len(self.items['x']) == len(self.items['y']):
            # Return the length of one of them
            return len(self.items['x'])
        # In any other case, print and return an error
        else:
            print('error: ' + str(self.items))
            return 'error'

    # Return the amount of items added by the participant (i.e. subtracting the automatic ones)
    def get_participant_items_count( self ):
        # Stage I
        if self.stage == 1:
            return self.get_items_count()
        # Stage II
        else:
            # Because on Stage II, 5 items are initially shown and cannot be removed
            return self.get_items_count() - 5

    # Receives a date string with format "yyyy-mm-dd" and returns the
    # corresponding Date object
    def transform_date( self, dateString ):

        # "Add" 2000 years to every year by replacing '000x' to '200x',
        # because the year 0000 breaks Python)
        dateString = dateString.replace('000', '200')

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

    # Returns the items as a list of points: [{x0, y0}, {x1, y1}, {x2, y2}, ...]
    # integer_dates: (Boolean) True if the dates have to be integers
    def get_points( self, integer_dates = False):
        points = []

        # For each item, create and add a new point
        for i in range(len(self.items['x'])):

            y = self.items['y'][i]

            if integer_dates:
                x = self.__date_to_days(self.items['x'][i])
            else:
                x = self.items['x'][i]

            points.append([ x, y ])

        return points

    # Returns the RAW Centripetal Catmull-Rom points of the current Response
    def get_raw_catmull_rom( self ):
        # Thousands of Catmull-Rom points because we want great smoothness
        nPoints = 2000

        return catmull_rom_chain(self.get_points(True), nPoints)

    # Returns the FILTERED Centripetal Catmull-Rom points of the current Response
    # By filtered, it means there is one point per day.
    # This returns an array of arrays, in this form: [[x0, y0], [x1, y1], ...]
    def get_catmull_rom( self, addNils=False ):
        # Linear interpolation because there are only two points
        if self.get_items_count == 2:
            points = self.__get_linear_interpolation()
        # Length larger than 2, because the minimum length is 2
        else:
            points = self.__get_catmull_rom()

        # Should nil values be added to the array?
        if addNils:
            return self.__add_nils_to_interpolation(points)
        else:
            return points

    # Given the nature of the experiment, there are points on the beginning
    # and end of the graph that have no values
    def __add_nils_to_interpolation( self, points):

        # Get the first and last days of the interpolation
        firstDay = points[0][0]
        lastDay = points[len(points)-1][0]

        for day in range(0, firstDay):
            points = [[firstDay - day - 1, 'nil']] + points #Preppend

        for day in range(lastDay+1, 365*4+20):
            points = points + [[day, 'nil']] #Append

        return points


    # Returns the linear interpolation of the items
    def __get_linear_interpolation( self ):
        # Get the 'x' and 'y' values of the first and last point
        firstX = self.__date_to_days(self.items['x'][0])
        lastX = self.__date_to_days(self.items['x'][len(self.items)-1])

        firstY = self.items['y'][1]
        lastY = self.items['y'][len(self.items)-1]

        # Calculate the slope and the Y-intercept
        slope = (lastY - firstY)/(lastX - firstX)
        yIntercept = firstY - firstX * slope

        # Create the points, from the first one to the last one, using the slope
        points = []
        for x in range(firstX, lastX):
            y = yIntercept + slope * x

            points.append([x, y])

        return points

    # Returns the Response as an array
    def get_as_array( self ):
        # The returned points correspond to the Catmull-Rom ones
        points = self.get_catmull_rom(True)

        # Get only the yAxis
        yAxis = []
        for p in points:
            yAxis.append(p[1])

        array = [
            self.timestamp,
            self.datetime,
            self.stage,
            self.condition,
            self.subcondition,
            self.pageIndex,
            self.noiseIndex,
            array_to_csv(yAxis)
        ]

        return array

    # Returns number of days between the target date and the 31st of
    # december of 2000. Given the data, the least integer will be 0
    def __date_to_days( self, date ):
        return (date - datetime.date(2000, 12, 31)).days

    # Returns the Catmull interpolation. Only to be used when the
    # number of items is three or more
    def __get_catmull_rom( self ):
        spline = self.get_raw_catmull_rom()

        # Get the 'x' value for the first and last point of the spline
        firstX = int(round(spline[0][0]))
        lastX = int(round(spline[len(spline)-1][0]))

        searchIndex = 0

        filteredPoints = []

        # For each of the x values that need to be filled with a value...
        for x in range(firstX, lastX + 1):
            # Search for the point that it closest to it, starting with the search
            # at the searchIndex
            searchIndex = self.__find_closest_x(spline, x, searchIndex)

            # Add the found point to the filteredPoints list
            filteredPoints.append( [x, spline[searchIndex][1]] )

        return filteredPoints

    # Returns the index of the point which has the closest X value to the targetValue
    # The search is started in startSearchOn
    def __find_closest_x( self, points, targetValue, startSearchOn=0):
        minimumDistance = 999999999 # Very large number
        indexOfMinimum = -1 # Index where the minimum distance to the target is found

        # Search on the entire length of the
        for i in range(startSearchOn, len(points)):
            distance = abs(targetValue - points[i][0])

            # If the new distance is smaller than the current minimum distance, save it
            if distance <= minimumDistance:
                minimumDistance = distance
                indexOfMinimum = i
            else:
                # Given that the distance is described by a convex function,
                # once the distance increases, then it means the minimum has
                # been passed
                break

        # Return the index where the minimum distance was found
        return indexOfMinimum

    # Plots the Centripetal Catmull-Rom of the current Response
    def plot_catmull_rom( self ):
        points = self.get_catmull_rom()

        trace = self.__points_to_trace(points)

        plotly.offline.plot([trace], filename='basic-line')

    # Transforms an array of points to a trace:
    def __points_to_trace( self, points ):
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



##############################################################
##                         LIBRARIES                        ##
##############################################################

# Source: Wikipedia, https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
def catmull_rom_spline(P0, P1, P2, P3, nPoints=10):
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
def catmull_rom_chain(points, nPointsCatmullRom = 10):
  """
  Calculate Catmull Rom for a chain of points and return the combined curve.
  """
  points = add_border_points(points)

  size = len(points)

  # The curve C will contain an array of (x,y) points.
  C = []
  for i in range(size-3):
    c = catmull_rom_spline(points[i], points[i+1], points[i+2], points[i+3], nPointsCatmullRom)

    C.extend(c)

  return C

def add_border_points( points ):
    diff_resolution = 10

    # Get the change in x and y between the first and second coordinates.
    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]

    #Then using the change, extrapolate backwards to find a control point.
    x1 = points[0][0] - (dx / diff_resolution)
    y1 = points[0][1] - (dy / diff_resolution)

    # Create the start point from the extrapolated values.
    start = [x1, y1]

    # Repeat for the end control point.
    n = len(points) - 1
    dx = points[n][0] - points[n - 1][0]
    dy = points[n][1] - points[n - 1][1]

    xn = points[n][0] + (dx / diff_resolution)
    yn = points[n][1] + (dy / diff_resolution)
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


def plot_catmull_rom( points ):
    points = catmull_rom_chain(data, 1500)
    trace = points_to_trace(points)
    plotly.offline.plot([trace], filename='basic-line')

# Returns an array as a csv
def array_to_csv(array):
    # It does so by transforming the array into a String, and replacing the brackets
    return str(array).replace('[', '').replace(']', '').replace("'", '')

# Start:
#plot_catmull_rom([[0,0],[10,10],[11,5],[20,20], [21, -10], [30, 30]])
all_subjects = create_subjects()
