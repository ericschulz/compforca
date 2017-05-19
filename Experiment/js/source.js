var userId = Math.random();
var pageIndex = 0;
var pagesNames = [];

var condition = shuffle(['temperature', 'sales', 'facebook_friends', 'rain','gym_memberships', 'wage']);
var subCondition = getSubConditions();

historicalData = [];

// Firebase database
var database = new Firebase("https://bayesian-forecasting.firebaseio.com/");

$(function() {
  showPlayGraph();
  //debug(8);
});

function toggleInstructions() {
  $("#instructions").fadeToggle();
}

function hideShow(hideSelector, showSelector){
  // Hides the 'hideSelector' element(s) and shows (fades in) the 'showSelector' element(s)
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
    hideShow('#page1', '#page2');
  }
  else if (getExperimentStage() == 1 || getExperimentStage() == 2) {
    $("#instructions").hide();
    $('#canvasPage').fadeIn();
    disableContinueButton();

    // First page of section 2
    if(pageIndex == 2 + getConditionsCount()) {
      $("#instructions").show();
      window.scrollTo(0,0);
      $('#instructions_title').text('Instructions - PART 2');
      $('#second_section_instruction').show();
    }

    // Create, show, and save graph
    graph = showGraph();

    // Remove all items if we are on Stage 1
    if (getExperimentStage() == 1) {
      items = [];
    }
  }
  // Demographics page
  else if (getExperimentStage() == 3) {
    $('#demographicsPage').fadeIn();
    $('#page2').hide();
    $('#canvasPage').hide();
    disableContinueButton();
  }
  // Thank you page
  else if (getExperimentStage() == 4) {
    // Save and send all the information to the server
    sendData();

    // Hide the demographics' page and the continue button
    $('#demographicsPage').hide();
    $('#continueButtonPage').hide();
    disableContinueButton();

    // Show the final page
    $('#thankYouPage').fadeIn();
  }
}

// Play graph
function showPlayGraph() {
  var container = document.getElementById('play_graph');

  items = [
    {x: '0000-01-01', y: 10},
    {x: '0000-06-01', y: 20},
    {x: '0000-12-01', y: 30}
  ];

  var dataset = new vis.DataSet(items);

  var options = {
    moveable: false,
    zoomable: false,
    min:  '0000-01-01',
    max:  '0004-01-05',

    dataAxis: {
        left: {
            range: getMinMax(getYAxisRange()),
            title: {text: "Y-axis"}
        }
    },

    timeAxis: {scale: 'month', step: 2},

    start:'0000-01-01',
    end:  '0004-01-05'
  };

  // Show and return Graph2d object
  graph = new vis.Graph2d(container, dataset, options);

  graph.on("click", graphOnClick);
}

// Graph
function showGraph(pageName) {
  var container = document.getElementById('graph');

  $('#specificInstructions').html(getSpecificInstructions);

  items = getInitialItems();

  var dataset = new vis.DataSet(items);

  var options = {
    moveable: false,
    zoomable: false,
    //zoomMin: 315360000000,
    //zoomMax: 315360000000,
    min:  '0000-01-01',
    max:  '0004-01-05',

    dataAxis: {
        left: {
            range: getMinMax(getYAxisRange()),
            title: {text: getYAxisLabel()}
        }
    },

    interpolation: {
      enabled: true,
      parametrization: 'centripetal'
    },

    timeAxis: {scale: 'month', step: 2},

    start:'0000-01-01',
    end:  '0004-01-05'
  };

  // Updates the labels
  updateLabels(checkItems(items));

  // Show and return Graph2d object
  var g = new vis.Graph2d(container, dataset, options);

  g.on("click", graphOnClick);

  return g;
}

// Saves the current items
function saveItems() {
  var now = $.now();

  var pageData = {
    'now': now,
    'datetime': (new Date(now)).toString(),
    'pageIndex': pageIndex,
    'condition': getCurrentCondition(),
    'subCondition': getCurrentPageSubcondition(),
    'items': items
  };

  historicalData = historicalData.concat(pageData);
}

// Saves the current data on the database
function sendData() {
  var now = $.now();

  database.push({
    'userId': getUserId(),
    'now': now,
    'datetime': (new Date(now)).toString(),
    'gender': getGender().toString(),
    'age': getAge().toString(),
    'historicalData': historicalData
  });
}

function getYAxisRange() {
  if (getCurrentCondition() == 'temperature') { return [-10, 40]; }
  else if (getCurrentCondition() == 'sales') { return [0, 5000]; }
  else if (getCurrentCondition() == 'facebook_friends') { return [0, 1000]; }
  else if (getCurrentCondition() == 'rain') { return [0, 100]; }
  else if (getCurrentCondition() == 'gym_memberships') { return [0, 50]; }
  else if (getCurrentCondition() == 'wage') { return [0, 50]; }
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
  if (getCurrentCondition() == 'temperature') { return 'Temperature (Celsius)'; }
  else if (getCurrentCondition() == 'sales') { return 'Sales (Units)'; }
  else if (getCurrentCondition() == 'facebook_friends') { return 'Number of total Facebook friends'; }
  else if (getCurrentCondition() == 'rain') { return 'Probability of a rainy day (%)'; }
  else if (getCurrentCondition() == 'gym_memberships') { return 'Number of total gym members'; }
  else if (getCurrentCondition() == 'wage') { return 'Hourly wage (US dollars)'; }
}

// Returns the initial values for the graphs of the first section of the experiment
function getInitialValue() {
  // If condition
  if (getCurrentCondition() == 'temperature') return 15;

  else if (getCurrentCondition() == 'sales') return 2500;

  else if (getCurrentCondition() == 'facebook_friends') return 200;

  else if (getCurrentCondition() == 'rain') return 30;

  else if (getCurrentCondition() == 'gym_memberships') return 30;

  else if (getCurrentCondition() == 'wage') return 20;
}

// Converts the values into an items object by adding dates
function addDatesToFirstYearPredictions(values) {
  return [
    {x: '0000-01-01', y: values[0]},
    {x: '0000-03-01', y: values[1]},
    {x: '0000-05-01', y: values[2]},
    {x: '0000-07-01', y: values[3]},
    {x: '0000-09-01', y: values[4]},
    {x: '0000-11-01', y: values[5]},
    {x: '0001-01-01', y: values[6]}
  ];
}

// Returns the first year values of the current variable
function getFirstYearValues() {
  if (getCurrentPageSubcondition() == 1) return getLinearUp(getInitialValue());
  else if (getCurrentPageSubcondition() == 2) return getStable(getInitialValue());
  else if (getCurrentPageSubcondition() == 3) return getLinearDown(getInitialValue());
}

// Returns the initial items to be shown on the graph
function getInitialItems() {
  if(getExperimentStage() == 1) {
    return [{x: '0005-01-01', y: getInitialValue()}];
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
    return 3
  }
  else {
    return 4;
  }
}

function getSpecificInstructions() {
  var text = ''

  if (getCurrentCondition() == 'temperature') text = 'Please draw the <strong>weather forecast</strong> for a large city';
  else if (getCurrentCondition() == 'sales') text = 'Please draw the <strong>sales forecast</strong> for a large company';
  else if (getCurrentCondition() == 'facebook_friends') text = 'Please draw a graph showing the <strong>number of total Facebook friends</strong> of a 25 year old male';
  else if (getCurrentCondition() == 'rain') text = 'Please draw the <strong>probability of a rainy day</strong> for a large city';
  else if (getCurrentCondition() == 'gym_memberships') text = 'Please draw the <strong>number gym members</strong> of a small gym';
  else if (getCurrentCondition() == 'wage') text = 'Please draw the <strong>hourly wage</strong> of a 25 year old male';


  if(getExperimentStage() == 1) {
    text = text.concat('.');
  }
  else if(getExperimentStage() == 2) {
    text = text.concat(', given the information for the first year.')
  }

  return text;
}

function getCurrentCondition() {
  return condition[(pageIndex - 2) % getConditionsCount()];
}

function getCurrentPageSubcondition() {
  return subCondition[(pageIndex - 2) % getConditionsCount()];
}

function getConditionsCount() {
  return condition.length;
}

function graphOnClick(params) {
  // Clicked value
  var value = params['value'][0];

  // Clicked date
  datetime = params['time'];
  timeString =  getTimeString(datetime)

  console.log(timeString)

  // Create an items dataset
  newItem = [
    {x: timeString, y: value}
  ];

  // Searches for newItem[0] in items, and returns its index
  var index = indexOf(newItem[0], items)

  // If the item was found
  if(index >= 0) {
    removePoint(index);
  }
  // In other case, it is added
  else {
    // If the experiment is on its second stage and the item is first year, the item shouldnt be added
    if(!( getExperimentStage() == 2 && firstYear(newItem) ) && nonNegativeYear(newItem)) {
      items = items.concat(newItem)
    }
  }

  // Updates the items shown
  updateItems(items);
}

// Removes a point from the points' array
function removePoint(index) {
  if(index >= 0) {
    // If the experiment is on its second stage, then the index must be 6 or larger
    if(!(getExperimentStage() == 2 && index <= 6)) {
      // Remove the item (remove/delete 1 element in position 'index' from 'items')
      items.splice(index, 1)
    }
  }
}

// Removes the last point added (called by the Undo button)
function removeLastPoint() {
  removePoint(items.length-1);
  updateItems(items);
}


// Returns true if the year of the item is not "000-x"
function nonNegativeYear(item) {
  return item[0].x.split('-')[0] != '000';
}

// Returns true when the item is of the first year
// Receives an array of objects, with only one item
function firstYear(item) {
  return item[0].x.split('-')[0] == '0000';
}

function updateItems(items) {
  // Set the items
  graph.setItems(items)

  // Check the items and update the labels
  updateLabels(checkItems(items))
}


// Checks whether the items attain the rules
// Returns a boolean's array
function checkItems(items) {
  firstMonth = false;
  lastMonth = false;

  for(i=0; i < items.length; i++) {
    dateElements = items[i].x.split('-')

    firstMonth = firstMonth || (dateElements[0] == '0000' && dateElements[1] == '01')

    lastMonth = lastMonth || (dateElements[0] == '0003' && dateElements[1] == '12')
  }

  return [firstMonth, lastMonth]
}

function updateLabels(booleanArray) {

  // Show or hide the 'checks' for the messages
  if(booleanArray[0]) {
    $('#firstMonth').fadeIn();
  }
  else {
    $('#firstMonth').fadeOut();
  }
  if(booleanArray[1]) {
    $('#lastMonth').fadeIn();
  }
  else {
    $('#lastMonth').fadeOut();
  }

  // Enable the 'Continue' button when both conditions are OK
  if(booleanArray[0] && booleanArray[1]){
    enableContinueButton();
  }
}


// Returns a datetime written as "yyyy-mm-dd"
function getTimeString(datetime) {
  year = '000'+ (datetime.getYear()+1900)

  month = addZero(datetime.getMonth()+1)

  day = addZero(datetime.getDate())

  return (year + '-' + month + '-' + day)
}

function addZero(value) {
  valueString = value.toString();

  if(valueString.length == 1) {
    valueString = '0' + valueString;
  }

  return valueString;
}

// Returns the index of a certain element in an array
// The element and the array are 'items' for Graph2d
function indexOf(element, array) {

  for(i=0; i<array.length; i++) {
    // If the items are equivalent, return the index
    if(compareItems(element, array[i])) return i
  }

  return -1;
}

// Returns true if both dates are equal
function compareItems(item1, item2) {
  components1 = item1.x.split('-');
  components2 = item2.x.split('-');

  equalYears = components1[0] == components2[0]
  equalMonths = components1[1] == components2[1]
  equalDays = Math.abs(components1[2] - components2[2]) <= 10 // Less than X days of difference

  // The range of acceptance depends on the Y variable
  var range = getAcceptanceRange();

  equalY = Math.abs(item1.y - item2.y) <= range

  return equalYears && equalMonths && equalDays && equalY
}

function getUserId() {
  return userId;
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


// Check the demographics data when the form changes.
$('#demographics').change(function(){
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
  $('button[name=continue]').prop('disabled', false);
}

function disableContinueButton() {
  $('button[name=continue]').prop('disabled', true);
}

// Returns the age on the demographics' form
function getAge() {
  return $('input[name=age]:checked', '#demographics').val();
}

// Returns the gender on the demographics' form
function getGender() {
  return $('input[name=gender]:checked', '#demographics').val();
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
  subc = shuffle(subc)

  return subc;
}

function getLinearUp(base, slopeScale = 1){
  var values = [];

  var scale = 0.05 * base; // The scale is 5% of the base

  var slope = scale * slopeScale; // If the slopeScale is 1, the slope is 5% of the base

  for(var i=0; i < 7; i++) {
    // Each value is the base + the slope*i + the random_number*scaling
    values = values.concat( base + slope * i + getSevenRandom()[i] * scale * 4);
  }

  return addDatesToFirstYearPredictions(values);
}

function getStable(base){
  return getLinearUp(base, 0);
}

function getLinearDown(base, slopeScale = 1){
  return getLinearUp(base, slopeScale * -1);
}

// Returns seven random numbers, from -0.5 to 0.5
// Generated in Python 3.5.2 by "random.random() - 0.5" from the random.py library
function getSevenRandom() {
  var sets =
    [
      [ 0.16933093785196052 - 0.5,
        0.7642726400978779 - 0.5,
        0.59420237112108 - 0.5,
        0.8045676111568967 - 0.5,
        0.3616072333221285 - 0.5,
        0.4333995695523616 - 0.5,
        0.3448741485276291  - 0.5 ],

      [ 0.2330127377152953 - 0.5,
        0.44558333713334464 - 0.5,
        0.7720815219200008 - 0.5,
        0.091949620524298 - 0.5,
        0.3371284569763776 - 0.5,
        0.8147280055034919 - 0.5,
        0.5571889833319483 - 0.5 ],

      [ 0.015973944458846367 - 0.5,
        0.6163862558959631 - 0.5,
        0.04367949448727826 - 0.5,
        0.057026095449790204 - 0.5,
        0.040766425126964156 - 0.5,
        0.17492704212711474 - 0.5,
        0.08634859133712236 - 0.5 ]
    ];

  return sets[Math.floor(userId * sets.length)];
}

// ######################### DEBUG

function debug(value){
  for(var i=0; i<value; i++) {
    nextPage();
  }
}
