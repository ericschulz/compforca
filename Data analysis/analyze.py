# exec(open('C:/Users/panch/Google Drive/Proyectos/GitHub/compforcaQV/Data analysis/analyze.py').read())
# pip install plotly


##############################################################
##                        LIBRARIES                         ##
##############################################################

# Library to read json files.
import json

# Library to plot graphs
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


##############################################################
##                     JSON PROCESSING                      ##
##############################################################

# Analyzes the entire dataset
def analyze_dataset():
    for subjectId in dataset.keys():
        analyze_one_subject( dataset[subjectId] )

def create_subjects():
    for subjectId in dataset.keys():
        analyze_one_subject( dataset[subjectId] )

# Analyzes the data for one subject
def analyze_one_subject( subject ):
    print ( get_prolific_id( subject ) )
    print ( get_session_id( subject ) )
    print ( get_age( subject ) )
    print ( get_datetime( subject ) )
    print ( get_gender( subject ) )

def get_test():
    subject = dataset[list(dataset)[0]]
    return get_subject_variable_stage(subject, 'rain', 1)

def plot_rain():
    trace0 = go.Scatter(
        x = random_x,
        y = random_y0,
        mode = 'lines',
        name = 'lines'
    )
    trace1 = go.Scatter(
        x = random_x,
        y = random_y1,
        mode = 'lines+markers',
        name = 'lines+markers'
    )
    trace2 = go.Scatter(
        x = random_x,
        y = random_y2,
        mode = 'markers',
        name = 'markers'
    )
    data = [trace0, trace1, trace2]

    py.iplot(data, filename='line-mode')


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
        self.__processRawData()

    # Processes the raw data received in the constructor
    def __processRawData( self ):
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

    # Returns the responses for a specific variable and stage
    def get_subject_variable_stage( self, variable, stage ):

        # For each variable, check if the search is finished. If it is, return that.
        for r in self.responses:
            if r['condition'] == variable and get_stage(r['pageIndex']) == stage :
                return r

        # If this point is reached, then the response was not found
        return "not found"

    def get_rain_1( self ):
        return get_subject_variable_stage(subject, 'rain', 1)

    # Returns a stage (1 or 2) given a pageIndex (integer)
    def get_stage( pageIndex ):
        if pageIndex <= 7:
            return 1
        elif pageIndex <= 13:
            return 2
        else:
            return "error"


##############################################################
##                         RESPONSE                          ##
##############################################################

class Response:
    """A subject's response to one variable"""

    def __init__( self, responseData ):
        self.rawData = responseData
        self.__processRawData()

    def __processRawData( self ):
        self.timestamp = self.rawData['now']
        self.datetime =  self.rawData['datetime']
        self.condition = self.rawData['condition']
        self.subCondition = self.rawData['subCondition']
        self.pageIndex = self.rawData['pageIndex']
        self.rawItems = self.rawData['items']

        self.items = self.__processItems(self.rawItems)

    # Processes the items raw data to a dictionary {x: xdata, y: ydata}
    def __processItems( self, rawItems ):
        xdata = []
        ydata = []

        for item in rawItems:
            # Append the y data point (transformed to a Date object)
            xdata.append(transformDate(item['x']))

            # Append the x data point (transformed to float)
            ydata.append(float(item['y']))

        return {x: xdata, y: ydata}

    # Receives a date string with format "yyyy-mm-dd" and returns the
    # corresponding Date object
    def transformDate( dateString ):
        return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()
