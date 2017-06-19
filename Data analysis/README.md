# Data analysis README

## bayesian-forecasting-export.json

This is the raw data exported directly from Firebase.

The JSON is a list of element. Each element is the data of a single participant.
Each element (participant) is modeled in the following way:

- age: String
- datetime: String
- gender: String
- historicalData: see below
- now: String (Unix timestamp)
- sessionId: String (Session ID set by Prolific Academic)
- userId: String (Unique User ID set by Prolific Academic -- the real values have been replaced by a sequential ID)



# Check the responses of a specific user (by Prolific ID)
plot_pid('a001')
