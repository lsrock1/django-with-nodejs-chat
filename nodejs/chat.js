// var http = require('http');
// var async = require('async');
// var server = http.createServer();
// var io = require('socket.io')(server);
var http =require('http');
var async = require('async');
var socketio = require('socket.io');
var express = require('express');

var router = express();
var server = http.createServer(router);
var io = socketio.listen(server,{log:false, origins:'*:*'});

var cookie_reader = require('cookie');
var querystring = require('querystring');
 
var redis = require('redis');
var sub = redis.createClient();

var messages = [];
var sockets = [];

//Subscribe to the Redis chat channel
sub.subscribe('chat');
 

//Configure socket.io to store cookie set by Django
io.set('authorization', function(data, accept){
    if(data.headers.cookie){
        data.cookie = cookie_reader.parse(data.headers.cookie);
        return accept(null, true);
    }
    return accept('error', false);
});
 
io.on('connection', function (socket) {
    
    //Grab message from Redis and send to client
    sub.on('message', function(channel, message){
        socket.send(message);
    });
    messages.forEach(function (data) {
      socket.emit('message', data);
    });//이전에 등록되어있는 메세지 출력

    sockets.push(socket);//소켓 array에 지금 연결된 소켓 푸쉬

    socket.on('disconnect', function () {
      sockets.splice(sockets.indexOf(socket), 1);
      updateRoster();
    });

    socket.on('message', function (msg) {
      console.log('message');
      var text = String(msg || '');

      if (!text)
        return;
        
      var data={
        name: socket.name,
        text: text
      };

      broadcast('message', data);
      messages.push(data);
    });

    socket.on('identify', function (name) {
      socket.name=String(name || 'Anonymous');
      updateRoster();
    });
    
    socket.on('clear',function(data){
      messages=[];
      broadcast('clear');
    })
    
    socket.on('next',function(name){
      console.log(name);
      var data={
        text: "#alert"+name
      }
      messages.push(data);
      broadcast('next',name);
    })
    //Client is sending message through socket.io
    // socket.on('send_message', function (message) {
    //     values = querystring.stringify({
    //         comment: message,
    //         sessionid: socket.handshake.cookie['sessionid'],
    //     });
        
    //     var options = {
    //         host: 'localhost',
    //         port: 3000,
    //         path: '/node_api',
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/x-www-form-urlencoded',
    //             'Content-Length': values.length
    //         }
    //     };
        
    //     //Send message to Django server
    //     var req = http.get(options, function(res){
    //         res.setEncoding('utf8');
            
    //         //Print out error message
    //         res.on('data', function(message){
    //             if(message != 'Everything worked :)'){
    //                 console.log('Message: ' + message);
    //             }
    //         });
    //     });
        
    //     req.write(values);
    //     req.end();
    // });
});

function updateRoster() {
  async.map(
    sockets,
    function (socket, callback) {
      var name=socket.name;
      callback(null,name);
    },
    function (err, names) {
      broadcast('roster', names);
    }
  );
}

function broadcast(event, data) {
  sockets.forEach(function (socket) {
    socket.emit(event, data);
  });
}

server.listen(8081, function(){
  var addr = server.address();
  console.log("Chat server listening at", addr.address + ":" + addr.port);
  // console.log("start");
});