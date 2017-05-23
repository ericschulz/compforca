var n=200;
var mucollect =[];
var mupresentcollect = [];
var mutruthcollect = [];
var prescollect = [];
var sigmacollect = [];
var kernelcollect = [];
var pointscollect = [];
var index = 0;
var trials=50;

var database = new Firebase("https://kernelcomp.firebaseio.com/");

function update()
{
 drawSplines();
}

function $(id)
{
 return document.getElementById(id);
}

var canvas=$("canvas"), ctx=canvas.getContext("2d");
function setCanvasSize()
{
 canvas.width = 600;
 canvas.height = 400;
}

window.onload = window.onresize = setCanvasSize();

function mousePositionOnCanvas(e)
{
  var el=e.target, c=el;
  var scaleX = c.width/c.offsetWidth || 1;
  var scaleY = c.height/c.offsetHeight || 1;
  if (!isNaN(e.offsetX))
              return { x:e.offsetX*scaleX, y:e.offsetY*scaleY };
  var x=e.pageX, y=e.pageY;
          do {
            x -= el.offsetLeft;
            y -= el.offsetTop;
            el = el.offsetParent;
          } while (el);
          return { x: x*scaleX, y: y*scaleY };
}

var setpoint = 0;
canvas.onclick = function(e)
{
          var p = mousePositionOnCanvas(e);
           if (setpoint===0 & p.x>10)
           {
             alert("The first point has to be behind the black line.");
             drawLine(10, 0, 10, 400, "black");
           } else{
                   if (p.x>setpoint)
                   {
                      addSplinePoint(p.x, p.y);
                      setpoint = p.x
                    }
                    if (p.x>550)
                    {
                      drawLine(590, 0, 590, 400)
                    }
                    if (p.x>590)
                    {
                     document.getElementById("submit").innerHTML='<button type="button" name="button"; onclick="dotrial()"; >Submit</button>';
                    }
                  }
};

function drawPoint(x,y,color)
{
 ctx.save();
 ctx.fillStyle=color;
 ctx.beginPath();
 ctx.arc(x,y,0.1,0,0.1*Math.PI);
 ctx.fill()
 ctx.restore();
}

var pts=[]; // a list of x and ys

      // given an array of x,y's, return distance between any two,
      // note that i and j are indexes to the points, not directly into the array.
function dista(arr, i, j)
{
        return Math.sqrt(Math.pow(arr[2*i]-arr[2*j], 2) + Math.pow(arr[2*i+1]-arr[2*j+1], 2));
}

function va(arr, i, j)
{
  return [arr[2*j]-arr[2*i], arr[2*j+1]-arr[2*i+1]]
}

function ctlpts(x1,y1,x2,y2,x3,y3)
{
  //Smoothness
  var t = 0.25;
  var v = va(arguments, 0, 2);
  var d01 = dista(arguments, 0, 1);
  var d12 = dista(arguments, 1, 2);
  var d012 = d01 + d12;
  return [x2 - v[0] * t * d01 / d012, y2 - v[1] * t * d01 / d012,
          x2 + v[0] * t * d12 / d012, y2 + v[1] * t * d12 / d012 ];
}

function addSplinePoint(x, y)
{
  pts.push(x); pts.push(y);
  drawSplines();
}

function removeSplinePoint()
{
 if (setpoint>10)
  {
    pts.pop(); pts.pop();
    drawSplines();
    setpoint=pts[pts.length-2]
  }
  if (setpoint<=590)
  {
    document.getElementById("submit").innerHTML=''
  }
  if (setpoint<=10)
  {
    drawLine(10, 0, 10, 400, "black");
    setpoint=0;
    pts=[];
  }
}

function drawSplines()
{
   clear();
   cps = []; // There will be two control points for each "middle" point, 1 ... len-2e
   for (var i = 0; i < pts.length - 2; i += 1)
   {
      cps = cps.concat(ctlpts(pts[2*i], pts[2*i+1], pts[2*i+2], pts[2*i+3], pts[2*i+4], pts[2*i+5]));
   }

   drawPoints(pts);
   drawCurvedPath(cps, pts);
     var scalex = d3.scale.linear()
                    .domain([0, 10])
                    .range([10, 590]);

    var scaley = d3.scale.linear()
                    .domain([Math.min(...mu), Math.max(...mu)])
                    .range([10, 390]);

    function gppoints(input, mu)
    {
      for(var j=0; j<inp.length; j++)
      {
       showPt(scalex(input[j]+5),mu[j], "red");
      }
    }
   gppoints(inp, mupresent);
   drawLine(scaleline(cmin), 0, scaleline(cmin), 400, "blue");
   drawLine(scaleline(cmax), 0,scaleline(cmax), 400, "blue");
}

function drawPoints(pts)
{
          for (var i = 0; i < pts.length; i += 2)
          {
              showPt(pts[i], pts[i+1], "black");
          }
}

function drawCurvedPath(cps, pts)
{
  var len = pts.length / 2; // number of points
  if (len < 2) return;

  if (len == 2)
  {
    ctx.beginPath();
    ctx.moveTo(pts[0], pts[1]);
    ctx.lineTo(pts[2], pts[3]);
    ctx.stroke();
  }
  else
  {

    ctx.beginPath();
    ctx.moveTo(pts[0], pts[1]);
    // from point 0 to point 1 is a quadratic
    ctx.quadraticCurveTo(cps[0], cps[1], pts[2], pts[3]);
    // for all middle points, connect with bezier
    for (var i = 2; i < len-1; i += 1)
    {
      // console.log("to", pts[2*i], pts[2*i+1]);
      ctx.bezierCurveTo(cps[(2*(i-1)-1)*2], cps[(2*(i-1)-1)*2+1],
                        cps[(2*(i-1))*2], cps[(2*(i-1))*2+1],
                        pts[i*2], pts[i*2+1]);
    }
    ctx.quadraticCurveTo(cps[(2*(i-1)-1)*2], cps[(2*(i-1)-1)*2+1],
                         pts[i*2], pts[i*2+1]);
    ctx.stroke();
  }
}

function clear()
{
  ctx.save();
    // use alpha to fade out
  ctx.fillStyle = "rgba(255,255,255,.7)"; // clear screen
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.restore();
}

function clearfull()
{
  ctx.save();
    // use alpha to fade out
  ctx.fillStyle = "rgb(255,255,255)"; // clear screen
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.restore();
}

function showPt(x,y,fillStyle)
{
  // console.log("showPt", x, y);
  ctx.save();
  ctx.beginPath();
  if (fillStyle) {
    ctx.fillStyle = fillStyle;
  }
  ctx.arc(x, y, 2.5, 0, 2*Math.PI);
  ctx.fill();
  ctx.restore();
}

function drawLine(x1, y1, x2, y2, strokeStyle)
{
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  if (strokeStyle) {
    ctx.save();
    ctx.strokeStyle = strokeStyle;
    ctx.stroke();
    ctx.restore();
  }
  else {
    ctx.save();
    ctx.strokeStyle = "black";
    ctx.stroke();
    ctx.restore();
  }
}

function clickStart(hide, show)
{
        //hide gets none, show gets block, window to the top
        document.getElementById(hide).style.display="none";
        document.getElementById(show).style.display = "block";
        window.scrollTo(0,0);
}

drawLine(10, 0, 10, 400, "black");



/////////////////////////////////////////////////////////
//GP FUNCTIONS
/////////////////////////////////////////////////////////

Array.prototype.contains = function(obj) {
    var i = this.length;
    while (i--) {
        if (this[i] == obj) {
            return true;
        }
    }
    return false;
}


function sq(x)
{
 var y=Math.pow(x,2)
 return(y)
}

//Function to randomly shuffle an array:
function shuffle(o)
{
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
};

//generates a standard normal using Box-Mueller transformation
function myNorm()
{
    var x1, x2, rad;
     do {
        x1 = 2 * Math.random() - 1;
        x2 = 2 * Math.random() - 1;
        rad = x1 * x1 + x2 * x2;
    } while(rad >= 1 || rad == 0);
     var c = Math.sqrt(-2 * Math.log(rad) / rad);
     return (x1 * c);
};

//Single multivariate draw
function mvgsingle(mu, L)
{
var n = mu.length, r = new Float64Array(n);
for (i = 0; i < n; ++i) r[i] = myNorm();
return numeric.add(mu, numeric.dot(L, r));
};

//multivariate draw using the Cholesky approach
function mvg(mu, cov, n)
{
var L = chol(cov);
if (arguments.length > 2 && typeof n !== "undefined") {
var i, samples = new Array(n);
for (i = 0; i < n; ++i) samples[i] =mvgsingle(mu, L);
return samples;
}
return mvgsingle(mu, L);
};

function kernel(X1,X2,n)
{
  var mysigma = [];
  for(var i=0; i<X1.length; i++)
  {
    mysigma[i] = new Array(X2.length);
  }
  for(var i=0; i<X1.length; i++)
  {
   for(var j=0; j<X1.length; j++)
   {

     //Squared-Exponential
     if(n===1) mysigma[i][j]=Math.exp((-sq(X1[i]-X2[j])/2.0));
     //Periodic
     if(n===2) mysigma[i][j]=Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))));
     //Linear
     if(n===3) mysigma[i][j]=((X1[i]-5)*(X2[j]-5));
     //Squared Exponential PLUS Periodic
     if(n===4) mysigma[i][j]=Math.exp((-sq(X1[i]-X2[j])/2.0)+Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25)))));
     //Periodic PLUS Linear
     if(n===5) mysigma[i][j]=Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))+((X1[i]-5)*(X2[j]-5));;
     //Linear PLUS Squared Exponential
     if(n===6) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))+Math.exp(-sq(X1[i]-X2[j])/2.0);
     //Squared Exponential TIMES Periodic
     if(n===7) mysigma[i][j]=Math.exp((-sq(X1[i]-X2[j])/2.0)*Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25)))));
     //linear times periodic
     if(n===8) mysigma[i][j]=Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))*((X1[i]-5)*(X2[j]-5));;
     //Linear TIMES Squared Exponential
     if(n===9) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))*Math.exp(-sq(X1[i]-X2[j])/2.0);
     //Linear PLUS Periodic PLUS Squared Exponential
     if (n===10) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))+Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))+Math.exp(-sq(X1[i]-X2[j])/2.0)
     //Linear TIMES Periodic PLUS Squared Exponential
     if (n===11) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))*Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))+Math.exp(-sq(X1[i]-X2[j])/2.0)
     //Linear PLUS Periodic TIMES Squared Exponential
     if (n===12) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))+Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))*Math.exp(-sq(X1[i]-X2[j])/2.0)
     //Linear PLUS Squared Exponential TIMES Periodic
     if (n===13) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))+Math.exp(-sq(X1[i]-X2[j])/2.0)*Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))
     //Linear PLUS Periodic TIMES Squared Exponential
     if (n===14) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))+3*Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))*Math.exp(-sq(X1[i]-X2[j])/2.0)
     //Linear TIMES Periodic TIMES Squared Exponential
     if (n===15) mysigma[i][j]=0.1*((X1[i]-5)*(X2[j]-5))*Math.exp(-sq(Math.sin((Math.abs(X1[i]-X2[j])*Math.PI*0.25))))*Math.exp(-sq(X1[i]-X2[j])/2.0)
    }
   }
 //Return covariance matrix
 return(mysigma)
}



function generateinput(n)
{
 var inp = new Array(n+1);
 //create input space
 for(var j=0; j<n+1; j++) {
    inp[j]=-5.0+j*10/n
  }
return(inp)
}

function generatecov(inp, k)
{
 var co=kernel(inp,inp, k);
 return(co)
}


function generategp(n,c)
{
 m=Array.apply(null, new Array(n+1)).map(Number.prototype.valueOf,0);
 var y=mvg(m, c, 1)[0];
 return(y)
};

var scaleline = d3.scale.linear()
                    .domain([0, 201])
                    .range([10, 590]);

//Initialize first round:
var inp=generateinput(n);
var k = Math.floor(Math.random() * (15 - 1 + 1)) + 1;
var mycov=generatecov(inp, k);
var mu=generategp(n,mycov);

var scalex = d3.scale.linear()
                    .domain([0, 10])
                    .range([10, 590]);

var scaley = d3.scale.linear()
                    .domain([Math.min(...mu), Math.max(...mu)])
                    .range([30, 370]);


mupresent=[];
var mutruth=[]
//var pres=Math.floor(Math.random() * (201 - 50 + 1)) + 30;
var pres=201;
var sigma=Math.floor(Math.random() * (900 - 9 + 1)) + 9;
var ones=Array.apply(null, Array(pres)).map(Number.prototype.valueOf,1);
var mills=Array.apply(null, Array(201-pres)).map(Number.prototype.valueOf,-100000);
var present=ones.concat(mills);
var present=shuffle(present)
var coversize=Math.floor(Math.random() * (50 - 5 + 1)) + 5;
var cmax=Math.floor(Math.random() * (201 - coversize + 1)) + coversize;
var cmin=cmax-coversize;
cmin=cmin
for(var j=0; j<201; j++)
{
  if(cmin < j & cmax >j)
  {
    present[j]=-100000;
  }
}
for(var j=0; j<n+1; j++) {
    mupresent[j]=(scaley(mu[j])+myNorm()*Math.sqrt(sigma))*present[j];
    mutruth[j]=scaley(mu[j]);

  }

function gppoints(input, mu)
{
  for(var j=0; j<inp.length; j++)
  {
   showPt(scalex(input[j]+5),mu[j], "red");
  }
}

gppoints(inp, mupresent);
drawLine(10, 0, 10, 400, "black");
drawLine(scaleline(cmin), 0, scaleline(cmin), 400, "blue");
drawLine(scaleline(cmax), 0,scaleline(cmax), 400, "blue");

function dotrial()
{
   trials=trials-1;
   mucollect[index]=mu;
   mupresentcollect[index]=mupresent;
   mutruthcollect[index]=mutruth;
   prescollect[index]=pres;
   sigmacollect[index]=sigma;
   kernelcollect[index]=k;
   pointscollect[index]=pts;
   index=index+1;

if (trials>0)
{
    var insertp1 ="Number of trials left: "+trials;
    document.getElementById("remain1").innerHTML = insertp1;
    clearfull();
   setpoint=0;
   //Initialize first round:
  inp=generateinput(n);
  k = Math.floor(Math.random() * (15 - 1 + 1)) + 1;
  var mycov=generatecov(inp, k);
  mu=generategp(n,mycov);

  var scalex = d3.scale.linear()
                      .domain([0, 10])
                      .range([10, 590]);

  var scaley = d3.scale.linear()
                      .domain([Math.min(...mu), Math.max(...mu)])
                      .range([30, 370]);

  mupresent=[];
  mutruth=[];

  pres=Math.floor(Math.random() * (201 - 50 + 1)) + 30;
  sigma=Math.floor(Math.random() * (900 - 9 + 1)) + 9;
  var ones=Array.apply(null, Array(pres)).map(Number.prototype.valueOf,1);
  var mills=Array.apply(null, Array(201-pres)).map(Number.prototype.valueOf,-100000);
  var present=ones.concat(mills);
  var present=shuffle(present)
  var coversize=Math.floor(Math.random() * (100 - 5 + 1)) + 5;
  cmax=Math.floor(Math.random() * (201 - coversize + 1)) + coversize;
  cmin=cmax-coversize;
  cmin=cmin
  for(var j=0; j<201; j++)
  {
    if(cmin < j & cmax >j)
    {
      present[j]=-100000;
    }
  }
  for(var j=0; j<n+1; j++) {
      mupresent[j]=(scaley(mu[j])+myNorm()*Math.sqrt(sigma))*present[j];
      mutruth[j]=scaley(mu[j]);
    }

  function gppoints(input, mu)
  {
    for(var j=0; j<inp.length; j++)
    {
     showPt(scalex(input[j]+5),mu[j], "red");
    }
  }

  gppoints(inp, mupresent);
  pts=[];

  drawLine(10, 0, 10, 400, "black");
  drawLine(scaleline(cmin), 0, scaleline(cmin), 400, "blue");
  drawLine(scaleline(cmax), 0,scaleline(cmax), 400, "blue");
  document.getElementById("submit").innerHTML='';
 }else{
 clickStart('page2', 'page3');
 }

}

function senddata(){
    var age=90;
    if (document.getElementById('age1').checked) {var  age = 20}
    if (document.getElementById('age2').checked) {var  age = 30}
    if (document.getElementById('age3').checked) {var  age = 40}
    if (document.getElementById('age4').checked) {var  age = 50}

    var gender=3;
    if (document.getElementById('gender1').checked) {var  gender = 1}
    if (document.getElementById('gender2').checked) {var  gender = 2}

    database.push({gender: gender, age: age, mucollect: mucollect, mutruthcollect: mutruthcollect, mupresentcollect: mupresentcollect,
      prescollect: prescollect, sigmacollect: sigmacollect, kernelcollect: kernelcollect, pointscollect: pointscollect});
    clickStart('page5','page6');

}
