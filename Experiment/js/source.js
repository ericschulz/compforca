var userId = Math.random();
var pageIndex = 0;
var pagesNames = [];

var condition = shuffle(['temperature', 'sales', 'partners']);
var subCondition = shuffle([1, 1, 1, 2, 2, 2, 3, 3, 3]);

historicalData = [];

// Firebase database
var database = new Firebase("https://bayesian-forecasting.firebaseio.com/");

$(function() {
    //debug(5);
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
  if(pageIndex > 1 && pageIndex < 8){
    // Destroy the previous graph
    graph.destroy();

    // Save the items information.
    saveItems();
  }

  pageIndex++;

  if(pageIndex == 1) {
    hideShow('#page1', '#page2');
  }
  else if (pageIndex <= 7) {
    $("#instructions").hide();
    $('#canvasPage').fadeIn();
    disableContinueButton();

    // First page of section 2
    if(pageIndex == 5) {
      $("#instructions").show();
      window.scrollTo(0,0);
      $('#instructions_title').text('Instructions - PART 2');
      $('#second_section_instruction').show()
    }

    // Create, show, and save graph
    graph = showGraph()

    // Remove all items
    if (pageIndex <= 4) {
      items = []
    }
  }
  // Demographics page
  else if (pageIndex == 8) {
    $('#demographicsPage').fadeIn()
    $('#page2').hide()
    $('#canvasPage').hide()
    disableContinueButton();
  }
  // Thank you page
  else if (pageIndex == 9) {
    // Save and send all the information to the server
    sendData();

    // Hide the demographics' page and the continue button
    $('#demographicsPage').hide()
    $('#continueButtonPage').hide()
    disableContinueButton();

    // Show the final page
    $('#thankYouPage').fadeIn()
  }
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
    max:  '0003-12-31',

    dataAxis: {
        left: {
            range: getYAxisRange(),
            title: {text: getYAxisLabel()}
        },

    },

    start:'0000-01-01',
    end:  '0003-12-31'
  };

  // Updates the labels
  updateLabels(checkItems(items))

  // Show and return Graph2d object
  g = new vis.Graph2d(container, dataset, options);

  g.on("click", graphOnClick)

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
  if (getCurrentCondition() == 'temperature') return {min:-11, max:41}
  else if (getCurrentCondition() == 'sales') return {min:-100, max:5100}
  else return {min:-0.5, max:10.5}
}

function getYAxisLabel() {
  if (getCurrentCondition() == 'temperature') return 'Temperature (Celsius)'
  else if (getCurrentCondition() == 'sales') return 'Sales (Units)'
  else return 'Partners'
}

// Returns the initial values for the graphs of the first section of the experiment
function getInitialValue() {
  if (getCurrentCondition() == 'temperature') return 15;
  else if (getCurrentCondition() == 'sales') return 2500;
  else return 0;
}

// Returns the predictions for the first year of the current task
function getFirstYearPrediction() {
  if (getCurrentCondition() == 'temperature') {
    return getFirstYearTemperature();
  }
  else if (getCurrentCondition() == 'sales') {
    return getFirstYearSales();
  }
  else {
    return getFirstYearPartners();
  }
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

// Returns the values for the first year of temperatures
function getFirstYearTemperature() {
  if (getCurrentPageSubcondition() == 1) {
    return addDatesToFirstYearPredictions([6, 10, 17, 20, 21, 14, 8]); //London
  }
  else if (getCurrentPageSubcondition() == 2) {
    return addDatesToFirstYearPredictions([30, 27, 18, 15, 16, 22, 32]); //Santiago
  }
  else if (getCurrentPageSubcondition() == 3) {
    return addDatesToFirstYearPredictions([3, 2, 5, 11, 13, 6, 5]); //Reijkavik
  }
}

// Returns the values for the first year of sales
function getFirstYearSales() {
  if (getCurrentPageSubcondition() == 1) {
    return addDatesToFirstYearPredictions([2000, 2100, 2200, 2300, 2400, 2500, 2600]);
  }
  else if (getCurrentPageSubcondition() == 2) {
    return addDatesToFirstYearPredictions([2000, 2100, 2000, 1950, 1900, 2000, 2000]);
  }
  else if (getCurrentPageSubcondition() == 3) {
    return addDatesToFirstYearPredictions([2000, 1900, 1800, 1700, 1600, 1500, 1400]);
  }
}

// Returns the values for the first year of partners
function getFirstYearPartners() {
  if (getCurrentPageSubcondition() == 1) {
    return addDatesToFirstYearPredictions([0, 0, 0, 0, 0, 0, 1]);
  }
  else if (getCurrentPageSubcondition() == 2) {
    return addDatesToFirstYearPredictions([0, 0, 0, 1, 1, 2, 2]);
  }
  else if (getCurrentPageSubcondition() == 3) {
    return addDatesToFirstYearPredictions([0, 1, 2, 2, 2, 3, 4]);
  }
}

// Returns the initial items to be shown on the graph
function getInitialItems() {
  if(getExperimentStage() == 1) {
    return [{x: '0004-01-01', y: getInitialValue()}];
  }
  else if(getExperimentStage() == 2) {
    return getFirstYearPrediction();
  }
}

function getExperimentStage() {
  if(pageIndex <= 1) {
    return 0;
  }
  else if(pageIndex <= 4) {
    return 1;
  }
  else if(pageIndex <= 7) {
    return 2;
  }
  else {
    return 3;
  }
}

function getSpecificInstructions() {
  if(pageIndex <= 4) {
    if (getCurrentCondition() == 'temperature') return 'Please draw the <strong>weather forecast</strong> for a large city.'
    else if (getCurrentCondition() == 'sales') return 'Please draw the <strong>sales forecast</strong> for a large company.'
    else return 'Please draw a graph showing the <strong>number of cummulative sexual partners</strong> that a 21 year old male will have in the future.'
  }
  else {
    if (getCurrentCondition() == 'temperature') return 'Please draw the <strong>weather forecast</strong> for a large city, given the information for the first year.'
    else if (getCurrentCondition() == 'sales') return 'Please draw the <strong>sales forecast</strong> for a large company, given the information for the first year.'
    else return 'Please draw a graph showing the <strong>number of cummulative sexual partners</strong> that a 21 year old male will have in the future, given the information for the first year.'
  }
}

function getCurrentCondition() {
  return condition[(pageIndex - 2) % 3];
}

function getCurrentPageSubcondition() {
  return subCondition[(pageIndex - 2) % 3];
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
    // If the experiment is on its second stage, then the index must be 6 or larger
    if(!(getExperimentStage() == 2 && index <= 6)) {
      // Remove the item (remove/delete 1 element in position 'index' from 'items')
      items.splice(index, 1)
    }
  }
  // In other case, it is added
  else {
    // If the experiment is on its second stage and the item is first year, the item shouldnt be added
    if(!( getExperimentStage() == 2 && firstYear(newItem) ) && nonNegativeYear(newItem)) {
      items = items.concat(newItem)
    }
  }

  // Updates the items shown
  updateItems(items)
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
  var range = 1;
  if (getCurrentCondition() == 'temperature') range = 1
  else if (getCurrentCondition() == 'sales') range = 100
  else range = 0.3

  equalY = Math.abs(item1.y - item2.y) <= range

  return equalYears && equalMonths && equalDays && equalY
}

function getUserId() {
  return userId;
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
  var full = (getAge() != undefined) && (getGender() != undefined)

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

// ######################### DEBUG

function debug(value){
  for(var i=0; i<value; i++) {
    nextPage();
  }
}
