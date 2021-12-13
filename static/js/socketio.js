var socket = io();
var swtc = document.getElementById('switch');

socket.on('state', function(data){
  var state = 'On';
  var test_threads = data.test_ws;
  if(!test_threads){
    state = 'Off'
  }

  document.getElementById('state').innerHTML = 'State: ' + state + '<br>';
  document.getElementById('state').innerHTML += 'Last update: ' + data.last_activity;
});

swtc.addEventListener('change', function(){
  if(swtc.checked){
    socket.emit('on');
  }else{
    socket.emit('off');
  }
});

socket.on('switch_mode', function(data){
  swtc.checked = data;
});