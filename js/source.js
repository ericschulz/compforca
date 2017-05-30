var pageIndex = 0;
var pagesNames = [];

// Debug parameters
var forcedRandomSet = -1;
var forcedCondition = -1;
var forcedSubCondition = -1;

var condition = shuffle(["temperature", "sales", "facebook_friends", "rain","gym_memberships", "wage"]);
var subCondition = getSubConditions();

historicalData = [];

var noisePointsCount = 5;
var noiseArray = 0; // The noise array is constant across one subject

// Firebase database
var database = new Firebase("https://bayesian-forecasting.firebaseio.com/");

$(function() {
  showPlayGraph();

  if(getUrlParameter("multi") !== undefined) {
    console.log("multipage");
    multiPage();
  }
  else if(getUrlParameter("debug") !== undefined) {
    console.log("debug");
    debug(getUrlParameter("debug"));
  }
});

function toggleInstructions() {
  $("#instructions").fadeToggle();
}

function hideShow(hideSelector, showSelector){
  // Hides the "hideSelector" element(s) and shows (fades in) the "showSelector" element(s)
  $(hideSelector).hide();
  $(showSelector).fadeIn();
}

// Canvas variables
var graph;
var items = [];
var newItem;

function nextPage(){
  if(pageIndex > 1 && pageIndex < 2 + getConditionsCount()*2){
    // Destroy the previous graph
    graph.destroy();

    // Save the items information.
    saveItems();
  }

  pageIndex++;

  if(getExperimentStage() === 0) {
    hideShow("#page1", "#page2");
  }
  else if (getExperimentStage() == 1 || getExperimentStage() == 2) {
    $("#instructions").hide();
    $("#canvasPage").fadeIn();
    disableContinueButton();

    // First page of section 2
    if(pageIndex == 2 + getConditionsCount()) {
      $("#instructions").show();
      window.scrollTo(0,0);
      $("#instructions_title").text("Instructions - PART 2");
      $("#second_section_instruction").show();
    }

    // Create, show, and save graph
    graph = showGraph("graph");

    // Remove all items if we are on Stage 1
    if (getExperimentStage() == 1) {
      items = [];
    }
  }
  // Demographics page
  else if (getExperimentStage() == 3) {
    $("#demographicsPage").fadeIn();
    $("#page2").hide();
    $("#canvasPage").hide();
    disableContinueButton();
  }
  // Thank you page
  else if (getExperimentStage() == 4) {
    // Save and send all the information to the server
    sendData();

    // Hide the demographics" page and the continue button
    $("#demographicsPage").hide();
    $("#continueButtonPage").hide();
    disableContinueButton();

    // Show the final page
    $("#thankYouPage").fadeIn();
  }
}

// Play graph
function showPlayGraph() {
  var container = document.getElementById("play_graph");

  items = [
    {x: "0000-01-01", y: 10},
    {x: "0000-06-01", y: 20},
    {x: "0000-12-01", y: 30}
  ];

  var dataset = new vis.DataSet(items);

  var options = getGraphOptions();

  // Show and return Graph2d object
  graph = new vis.Graph2d(container, dataset, options);

  graph.on("click", graphOnClick);
}

// Graph
function showGraph(elementId) {
  var container = document.getElementById(elementId);

  $("#specificInstructions").html(getSpecificInstructions);

  items = getInitialItems();

  var dataset = new vis.DataSet(items);

  var options = getGraphOptions();

  // Updates the labels
  updateLabels(checkItems(items));

  // Show and return Graph2d object
  var g = new vis.Graph2d(container, dataset, options);

  g.on("click", graphOnClick);

  return g;
}

// Returns the graph options;
function getGraphOptions() {

  var yAxisLabel = "Y-axis";

  if( pageIndex > 0 ) {
    yAxisLabel = getYAxisLabel();
  }

  var options = {
    moveable: false,
    zoomable: false,
    min:  "0000-01-01",
    max:  "0004-01-05",

    dataAxis: {
        left: {
            range: getMinMax(getYAxisRange()),
            title: {text: yAxisLabel}
        }
    },

    interpolation: {
      enabled: true,
      parametrization: "centripetal"
    },

    timeAxis: {scale: "month", step: 1},

    format: {
      minorLabels: {
        month:      "MMM"
      },
      majorLabels: {
        month:      "[Year] YY"
      }
    },

    start:"0000-01-01",
    end:  "0004-01-05"
  };

  return options;
}

// Saves the current items
function saveItems() {
  var now = $.now();

  var pageData = {
    "now": now,
    "datetime": (new Date(now)).toString(),
    "pageIndex": pageIndex,
    "condition": getCurrentCondition(),
    "subCondition": getCurrentPageSubcondition(),
    "items": items
  };

  historicalData = historicalData.concat(pageData);
}

// Saves the current data on the database
function sendData() {
  var now = $.now();

  database.push({
    "userId": getUserId().toString(),
    "sessionId": getSessionId().toString(),
    "now": now.toString(),
    "datetime": (new Date(now)).toString(),
    "gender": getGender().toString(),
    "age": getAge().toString(),
    "historicalData": historicalData
  });
}

function getYAxisRange() {
  if (getCurrentCondition() == "temperature") { return [-10, 40]; }
  else if (getCurrentCondition() == "sales") { return [0, 5000]; }
  else if (getCurrentCondition() == "facebook_friends") { return [0, 1000]; }
  else if (getCurrentCondition() == "rain") { return [0, 100]; }
  else if (getCurrentCondition() == "gym_memberships") { return [0, 50]; }
  else if (getCurrentCondition() == "wage") { return [0, 50]; }
  else { return [0, 100]; }
}

// range = [min, max]
function getMinMax(range) {
  var range_value = range[1] - range[0];

  return {
    min: range[0] - 0.03 * range_value,
    max: range[1] + 0.03 * range_value
  };
}

function getYAxisLabel() {
  if (getCurrentCondition() == "temperature"){ return "Temperature (Celsius)"; }

  else if (getCurrentCondition() == "sales") { return "Sales (Units)"; }

  else if (getCurrentCondition() == "facebook_friends") { return "Number of total Facebook friends"; }

  else if (getCurrentCondition() == "rain") { return "Probability of a rainy day (%)"; }

  else if (getCurrentCondition() == "gym_memberships") { return "Number of total gym members"; }

  else if (getCurrentCondition() == "wage") { return "Hourly wage (US dollars)"; }
}

// Returns the initial values for the graphs of the first section of the experiment
function getInitialValue() {
  // If condition
  if (getCurrentCondition() == "temperature") { return 15; }

  else if (getCurrentCondition() == "sales") { return 2500; }

  else if (getCurrentCondition() == "facebook_friends") { return 200; }

  else if (getCurrentCondition() == "rain") { return 30; }

  else if (getCurrentCondition() == "gym_memberships") { return 30; }

  else if (getCurrentCondition() == "wage") { return 20; }
}

// Returns the lower and upper bound depending on the current condition
function getBounds() {
  var largeNumber = 4194304;

  // If condition
  if (getCurrentCondition() == "temperature") { return [-273, largeNumber]; } // Absolute zero to large number (hehe)

  else if (getCurrentCondition() == "sales") { return [0, largeNumber]; }

  else if (getCurrentCondition() == "facebook_friends") { return [0, largeNumber]; }

  else if (getCurrentCondition() == "rain") { return [0, 100]; } // Percentage

  else if (getCurrentCondition() == "gym_memberships") { return [0, largeNumber]; }

  else if (getCurrentCondition() == "wage") { return [0, largeNumber]; }

  else { return [-largeNumber, largeNumber]; }
}

// Converts the values into an items object by adding dates
function addDatesToFirstYearPredictions(values) {
  // The first date in the noise vector
  var firstDate = new Date("0000-01-01");

  // Interval between each noises' point. 365 (days) divided by the amount of noisePoints (minus 1)
  var interval = (365-31) / (noisePointsCount - 1);

  var firstYearValues = [];

  for(var i=0; i < noisePointsCount; i++) {
    // Transform the datetime to string
    var datetime = getTimeString(firstDate);

    // Concatenate the element to the vector
    firstYearValues = firstYearValues.concat({
      x: datetime,
      y: values[i]
    });

    // Add the interval (for the next loop's step)
    firstDate.setDate(firstDate.getDate() + interval);
  }

  return firstYearValues;
}

// Returns the first year values of the current variable
function getFirstYearValues() {
  if (getCurrentPageSubcondition() == 1) { return getLinearUp(getInitialValue(), 1, 1); }
  else if (getCurrentPageSubcondition() == 2) { return getStable(getInitialValue()); }
  else if (getCurrentPageSubcondition() == 3) { return getLinearDown(getInitialValue(), 1); }
}

// Returns the initial items to be shown on the graph
function getInitialItems() {
  if(getExperimentStage() == 1) {
    return [{x: "0005-01-01", y: getInitialValue()}];
  }
  else if(getExperimentStage() == 2) {
    return getFirstYearValues();
  }
}

function getExperimentStage() {
  if(pageIndex <= 1) {
    return 0;
  }
  else if(pageIndex <= 1 + getConditionsCount()) {
    return 1;
  }
  else if(pageIndex <= 1 + 2 * getConditionsCount()) {
    return 2;
  }
  else if (pageIndex == 2 + 2 * getConditionsCount()) {
    return 3;
  }
  else {
    return 4;
  }
}

function getSpecificInstructions() {
  var text = "";

  if (getCurrentCondition() == "temperature") { text = "Please draw the <strong>weather forecast</strong> for a large city"; }
  else if (getCurrentCondition() == "sales") { text = "Please draw the <strong>sales forecast</strong> for a large company"; }
  else if (getCurrentCondition() == "facebook_friends") { text = "Please draw a graph showing the <strong>number of total Facebook friends</strong> of a 25 year old male"; }
  else if (getCurrentCondition() == "rain") { text = "Please draw the <strong>probability of a rainy day</strong> for a large city"; }
  else if (getCurrentCondition() == "gym_memberships") { text = "Please draw the <strong>number of total gym members</strong> of a small gym"; }
  else if (getCurrentCondition() == "wage") { text = "Please draw the <strong>hourly wage</strong> of a 25 year old male"; }


  if(getExperimentStage() == 1) {
    text = text.concat(".");
  }
  else if(getExperimentStage() == 2) {
    text = text.concat(", given the information for the first year.");
  }

  return text;
}

function getCurrentCondition() {
  if(forcedCondition == -1) {
    return condition[(pageIndex - 2) % getConditionsCount()];
  }
  else {
    return forcedCondition;
  }
}

function getCurrentPageSubcondition() {
  if(forcedSubCondition < 0) {
    return subCondition[(pageIndex - 2) % getConditionsCount()];
  }
  else {
    return forcedSubCondition;
  }
}

function getConditionsCount() {
  return condition.length;
}

function graphOnClick(params) {
  // Clicked value
  var value = params.value[0];

  // Clicked date
  datetime = params.time;
  timeString =  getTimeString(datetime);

  console.log(timeString);

  // Create an items dataset
  newItem = [
    {x: timeString, y: value}
  ];

  // Searches for newItem[0] in items, and returns its index
  var index = indexOf(newItem[0], items);

  // If the item was found
  if(index >= 0) {
    removePoint(index);
  }
  // In other case, it is added
  else {
    addPoint(newItem);
  }

  // Updates the items shown
  updateItems(items);
}

// Adds a new point into the items' array, as long as the new point is
// in accordance to the rules
function addPoint(newItem) {
  // If the experiment is on its second stage and the item is first year, the item shouldnt be added
  if(!( getExperimentStage() == 2 && firstYear(newItem) ) && nonNegativeYear(newItem)) {
    // The item has to be within the acceptable value boundaries
    if( withinValueBoundaries(newItem[0]) ) {
      // and the item is more than X days distant to the rest of the items
      if ( moreThanXDays(newItem[0], items, 25) ) {
        items = items.concat(newItem);
      }
      else {
        //window.alert("The new point has to be at least 30 days away from the closest point.");
      }
    }
  }
}

// Removes a point from the points" array
function removePoint(index) {
  if(index >= 0) {
    // If the experiment is on its second stage, then the index must be 6 or larger
    if(!(getExperimentStage() == 2 && index <= 6)) {
      // Remove the item (remove/delete 1 element in position "index" from "items")
      items.splice(index, 1);
    }
  }
}

// Removes the last point added (called by the Undo button)
function removeLastPoint() {
  removePoint(items.length-1);
  updateItems(items);
}

// Returns true if the newItem is more than X days off every other item in the list
function moreThanXDays(newItem, items, x) {
  var moreThanThirty = true;

  for(var i=0; i < items.length; i++) {
    // Check the distance between the newItem and every other item
    moreThanThirty = moreThanThirty && ( distanceInDays(newItem, items[i]) > x );
  }

  return moreThanThirty;
}

// Returns the distance, in months, between two items
function distanceInDays(item1, item2) {
  var date1 = new Date(item1.x);
  var date2 = new Date(item2.x);

  // Returns the absolute distance between the dates, in days
  return Math.abs(date2 - date1)/1000/60/60/24;
}

// Returns true if the new point is within the acceptable value boundaries
function withinValueBoundaries(item) {
  var lowerBound = getBounds()[0];
  var upperBound = getBounds()[1];

  // Get the item's value
  var value = item.y;

  return value > lowerBound && value < upperBound;
}

// Returns true if the year of the item is not "000-x"
function nonNegativeYear(item) {
  return item[0].x.split("-")[0] != "000";
}

// Returns true when the item is of the first year
// Receives an array of objects, with only one item
function firstYear(item) {
  return item[0].x.split("-")[0] == "0000";
}

function updateItems(items) {
  // Set the items
  graph.setItems(items);

  // Check the items and update the labels
  updateLabels(checkItems(items));
}


// Checks whether the items attain the rules
// Returns a boolean"s array
function checkItems(items) {
  var firstMonth = false;
  var lastMonth = false;

  for(var i=0; i < items.length; i++) {
    dateElements = items[i].x.split("-");

    firstMonth = firstMonth || (dateElements[0] == "0000" && dateElements[1] == "01");

    lastMonth = lastMonth || (dateElements[0] == "0003" && dateElements[1] == "12");

    lastMonth = lastMonth || (dateElements[0] == "0004" && dateElements[1] == "01");
  }

  return [firstMonth, lastMonth];
}

function updateLabels(booleanArray) {

  // Show or hide the "checks" for the messages
  if(booleanArray[0]) {
    $("#firstMonth").fadeIn();
  }
  else {
    $("#firstMonth").fadeOut();
  }
  if(booleanArray[1]) {
    $("#lastMonth").fadeIn();
  }
  else {
    $("#lastMonth").fadeOut();
  }

  // Enable the "Continue" button when both conditions are OK
  if(booleanArray[0] && booleanArray[1]){
    enableContinueButton();
  }
  // In any other case, disable the continue button, as long as we're on stage 2
  else {
    if(pageIndex > 0) {
      disableContinueButton();
    }
  }
}


// Returns a datetime written as "yyyy-mm-dd"
function getTimeString(datetime) {
  year = "000"+ (datetime.getYear()+1900);

  month = addZero(datetime.getMonth()+1);

  day = addZero(datetime.getDate());

  return (year + "-" + month + "-" + day);
}

function addZero(value) {
  valueString = value.toString();

  if(valueString.length == 1) {
    valueString = "0" + valueString;
  }

  return valueString;
}

// Returns the index of a certain element in an array
// The element and the array are "items" for Graph2d
function indexOf(element, array) {

  for(i=0; i<array.length; i++) {
    // If the items are equivalent, return the index
    if(compareItems(element, array[i])) return i;
  }

  return -1;
}

// Returns true if both dates are equal
function compareItems(item1, item2) {
  components1 = item1.x.split("-");
  components2 = item2.x.split("-");

  equalYears = components1[0] == components2[0];
  equalMonths = components1[1] == components2[1];
  equalDays = Math.abs(components1[2] - components2[2]) <= 10; // Less than X days of difference

  // The range of acceptance depends on the Y variable
  var range = getAcceptanceRange();

  equalY = Math.abs(item1.y - item2.y) <= range;

  return equalYears && equalMonths && equalDays && equalY;
}

// Returns the user id
function getUserId() {
  //https://panchoqv.github.io/compforcaQV/?prolific_pid={{%PROLIFIC_PID%}}&session_id={{%SESSION_ID%}}
  return undefinedStringify(getUrlParameter("prolific_pid"));
}

// Returns the session id
function getSessionId() {
  return undefinedStringify(getUrlParameter("session_id"));
}

// If the object is undefined, it returns "undefined"
function undefinedStringify(o){
  if(o === undefined){
    return "undefined";
  }
  else {
    return o;
  }
}

// Returns the acceptance range that is used to evaluate when a point is deleted.
function getAcceptanceRange() {
  var yRange = getYAxisRange();
  return (yRange[1] - yRange[0])/50;
}

// ######################## TOOLS

// From here: http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

// From: http://stackoverflow.com/questions/122102/what-is-the-most-efficient-way-to-deep-clone-an-object-in-javascript
function cloneObject(object) {
  return jQuery.extend(true, {}, oldObject);
}

// From: https://stackoverflow.com/questions/19491336/get-url-parameter-jquery-or-how-to-get-query-string-values-in-js
// It returns the URL GET parameter indicated by (string) sParam
var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split("&"),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split("=");

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
}


// Check the demographics data when the form changes.
$("#demographics").change(function(){
  // If the data is full, then enable the Continue button
  var full = (getAge() !== undefined) && (getGender() !== undefined)

  if (full) {
    enableContinueButton();
  }
  else {
    disableContinueButton();
  }
});

// Activate the Continue button
function enableContinueButton() {
  $("button[name=continue]").prop("disabled", false);
}

function disableContinueButton() {
  $("button[name=continue]").prop("disabled", true);
}

// Returns the age on the demographics" form
function getAge() {
  return $("input[name=age]:checked", "#demographics").val();
}

// Returns the gender on the demographics" form
function getGender() {
  return $("input[name=gender]:checked", "#demographics").val();
}

function getSubConditions() {
  var subc = [];

  // Create an ordered and balanced subconditions array.
  // If there are three conditions, it will create this: [1,2,3,1,2,3]
  // It can be seen that there are the same amount of each subcondition
  for(var i=0; i < getConditionsCount(); i++) {
    var oneToThree = (i % 3) + 1;
    subc = subc.concat(oneToThree);
  }

  // Now shuffle it:
  subc = shuffle(subc);

  return subc;
}

function getLinearUp(base, slopeScale, noiseScale){
  var values = [];

  //var scale = 0.05 * base; // The scale is 5% of the base
  var scale = 0.025 * ( getYAxisRange()[1] - getYAxisRange()[0] );

  var slope = scale * slopeScale; // If the slopeScale is 1, the slope is 5% of the base

  for(var i=0; i < noisePointsCount; i++) {
    // Each value is the base + the slope*i + the random_number*scaling
    values = values.concat( base + slope * i + getNoiseArray()[i] * scale * 4 * noiseScale); // 4
    //values = values.concat( base + slope * i);
  }

  return addDatesToFirstYearPredictions(values);
}

function getStable(base){
  return getLinearUp(base, 0, 1);
}

function getLinearDown(base, slopeScale){
  return getLinearUp(base, slopeScale * -1, -1);
}

// Returns a noise array for the trends
function generateNoiseArray() {
  var fiveRandom = getFiveRandom();

  console.log(forcedRandomSet);
  console.log(fiveRandom);

  var arrayAverage = getArrayAverage(fiveRandom);

  var noiseArray = [0];

  // Subtract the array's average to every element
  for(var i=0; i < noisePointsCount - 2; i++) {
    noiseArray = noiseArray.concat(fiveRandom[i] - arrayAverage);
  }

  // Returns the five random, each minus the array's average, and surrounded by zeroes.
  // i.e., [0, random_1, ..., random_n, 0]
  return noiseArray.concat([0]);
}

function getNoiseArray() {
  if(noiseArray === 0){
    noiseArray = generateNoiseArray();
  }
  return noiseArray;
}

// Returns the array's average value
function getArrayAverage(array){
  var sum = 0;

  for(var i=0; i < array.length; i++) {
    sum = sum + array[i];
  }

  return sum/array.length;
}

// Returns five random numbers
// Generated in Python 3.5.2 by "random.random()" from the random.py library
function getFiveRandom() {
  var sets =
    [
      [ 0.7642726400978779,
        0.59420237112108,
        0.8045676111568967,
        0.3616072333221285,
        0.4333995695523616 ],

      [ 0.44558333713334464,
        0.7720815219200008,
        0.091949620524298,
        0.3371284569763776,
        0.8147280055034919 ],

      [ 0.6163862558959631,
        0.04367949448727826,
        0.057026095449790204,
        0.040766425126964156,
        0.17492704212711474 ]
    ];

  if (forcedRandomSet < 0) {
    // Randomly returns one of the random sets
    return sets[Math.floor(Math.random() * sets.length)];
  }
  else {
    return sets[forcedRandomSet];
  }

}

// ######################### DEBUG

function debug(value){
  for(var i=0; i<value; i++) {
    nextPage();
  }
}

function multiPage() {
  forcedRandomSet = getUrlParameter("randomset");
  forcedCondition = ["temperature", "sales", "facebook_friends", "rain","gym_memberships", "wage"][getUrlParameter("condition")];
  forcedSubCondition = getUrlParameter("subcondition");
  debug(9);
}
