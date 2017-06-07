# exec(open('C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/analyze.py').read())
# s = Subject()
# pip install plotly


##############################################################
##                        LIBRARIES                         ##
##############################################################

# Library to read json files.
import json

# Library to plot graphs
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# Datetime
import datetime



##############################################################
##                    INITIAL VARIABLES                     ##
##############################################################

# Dataset variables
filepath = 'C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/bayesian-forecasting-export.json'
dataset = json.load(open(filepath, 'r'))

subjects = create_subjects()

##############################################################
##                     JSON PROCESSING                      ##
##############################################################

# Creates all the Subjects' objects and returns a list
def create_subjects():
    participants = []

    for subjectId in dataset.keys():
        participants.append(Subject(dataset[subjectId]))

    return participants

# Analyzes the data for one subject
def analyze_one_subject( index ):
    subject = subjects[index]

    plot_subject_variable(subject, 'rain')

# Displays a plot for a single subject, and a single variable
# variable can be {rain, gym_memberships, temperature, wage, facebook_friends, sales}
def plot_subject_variable( subjectIndex, variable):
    subject = subjects[subjectIndex]

    trace0 = go.Scatter(
        x = subject.get_response_items(variable, 1)['x'],
        y = subject.get_response_items(variable, 1)['y'],
        mode = 'lines+markers',
        name = 'Stage 1',
        line = dict(
            shape='spline'
        )
    )

    trace1 = go.Scatter(
        x = subject.get_response_items(variable, 2)['x'],
        y = subject.get_response_items(variable, 2)['y'],
        mode = 'lines+markers',
        name = 'Stage2',
        line = dict(
            shape='spline'
        )
    )

    data = [trace0, trace1]

    plotly.offline.plot(data, filename='line-mode')


##############################################################
##                          TOOLS                           ##
##############################################################


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
    def get_response( self, variable, stage ):

        # For each variable, check if the search is finished. If it is, return that.
        for r in self.responses:
            if r.condition == variable and r.stage == stage :
                return r

        # If this point is reached, then the response was not found
        return "not found"

    def get_response_items( self, variable, stage ):
        return self.get_response(variable, stage).items

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
        self.subCondition = self.rawData['subCondition']
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
            xdata.append(self.transformDate(item['x']))

            # Append the x data point (transformed to float)
            ydata.append(float(item['y']))

        return {'x': xdata, 'y': ydata}

    # Receives a date string with format "yyyy-mm-dd" and returns the
    # corresponding Date object
    def transformDate( self, dateString ):
        return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()

    # Returns a stage (1 or 2) given a pageIndex (integer)
    def __get_stage( self, pageIndex ):
        if pageIndex <= 7:
            return 1
        elif pageIndex <= 13:
            return 2
        else:
            return "error"
