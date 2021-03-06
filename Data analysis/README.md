# Data analysis README

## bayesian-forecasting-export.json

This is the raw data exported directly from Firebase.

The JSON is a list of element. Each element is the data of a single participant.
Each element (participant) is modeled in the following way:

- `age`: (String) The participant's age range
- `datetime`: (String)
- `gender`: (String) {male, female}
- `historicalData`: (List) Data of each plot. One object per plot
- `now`: (String) Unix timestamp
- `sessionId`: (String) Session ID set by Prolific Academic
- `userId`: (String) Unique User ID set by Prolific Academic -- the real values have been replaced by a sequential ID

### (Partial) Example of the JSON

<blockquote>

    {
      "-Km3ZOBPMI8ADj1vQ-cU" : {
        "age" : "36-45",
        "datetime" : "Wed Jun 07 2017 22:59:11 GMT+0100 (BST)",
        "gender" : "male",
        "historicalData" : [...],
        "now" : "1496872751882",
        "sessionId" : "593875c4e9b44100013ae848",
        "userId" : "a001"
      },
      "-Km3ZSCt5DB0kMIOsRzs" : {
        "age" : "26-35",
        "datetime" : "Wed Jun 07 2017 22:59:28 GMT+0100 (GMT Daylight Time)",
        "gender" : "female",
        "historicalData" : [...],
        "now" : "1496872768147",
        "sessionId" : "59387630771f6b00014b17b7",
        "userId" : "a002"
      },
      ...
    }

</blockquote>


## historicalData

This is the core data of the participant, and it consists of a list of 12 elements.
Each element represents a different plot, and is composed by the following subelements:

- condition: (String) {temperature, sales, rain, wage, gym_memberships, facebook_friends}
- datetime: (String)
- items: (List) Points on the plot. Each point has an "x" (String; date yyyy-mm-dd) and a "y" value (float)
- now: (String) Unix timestamp
- pageIndex: (Integer) Represents in which page of the experiment the plot was showed {2, ..., 13}. From 2 to 7, it was Stage I of the experiment. From 8 onwards, it was Stage II.
- subCondition: (Integer) Represents the subcondition of the experiment. Only useful on Stage II. {1: up, 2: stable, 3: down}

### Example of an element in historicalData

<blockquote>
    historicalData: [
      {
        "age" : "36-45",
        "datetime" : "Wed Jun 07 2017 22:59:11 GMT+0100 (BST)",
        "gender" : "male",
        "historicalData" : [ {
          "condition" : "facebook_friends",
          "datetime" : "Wed Jun 07 2017 22:55:03 GMT+0100 (BST)",
          "items" : [ {
            "id" : "24dd098f-9fe2-426e-b4f1-cdc8fee76a5f",
            "x" : "0001-05-17",
            "y" : 213.79999999999998
          },

          [more items...]

          ],
          "now" : 1496872503236,
          "pageIndex" : 2,
          "subCondition" : 3
        },

        [more elements in historicalData...]

        ],
        "now" : "1496872751882",
        "sessionId" : "593875c4e9b44100013ae848",
        "userId" : "a001"
      }
    ...
    ]

</blockquote>

# analyze.py

Contains all the data analysis code. It is composed of three parts: static code,
Subject class, and Response Class.

When the program is run, a list of Subjects is created on the basis of the json.
Each Subject has its own demographics data, plus a list of Responses. Each plot
is a Response (i.e., each element in the historicalData list of the json).

## Useful functions in analyze.py

### Check the responses of a specific user (by User ID). It creates plots on the browser.

- `spline`: (Boolean) If spline is True, it calculates all the spline points

        plot_pid('a001', spline=False)

### Plot all the curves (of Stage II) associated to a target variable

- `variable`: (String) {'temperature', 'rain', 'sales', 'gym_memberships', 'wage', 'facebook_friends'}. Name of the variable to be plotted
- `trend`: (String) {'stable', 'up', 'down'}. The slope of the trend.
- `noiseIndex`: Integer {0, 1, 2}. Which of the three noise sets to target

        plot_variable(variable, trend='stable', noiseIndex=0)


### Print the IDs of those subjects that were deemed invalid because of their responses

        print_invalid_subjects()

### Total of participants

        def get_number_of_subjects()
