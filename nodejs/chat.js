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
var io = socketio.listen(server);

var cookieParser =require('socket.io-cookie');
var cookie_reader = require('cookie');
var querystring = require('querystring');
 
var redis = require('redis');
var sub = redis.createClient();

var messages = [];
var sockets = [];

//Subscribe to the Redis chat channel
sub.subscribe('chat');
 
io.use(cookieParser);

sub.on('message', function(channel, message){
  var data=JSON.parse(message);
  if (data.key=='poor'){
    
    var one='<div class="alert alert-danger"><strong>'+data.user+' (이)가</strong> 전 재산을 털어 쏘려고 했지만 돈이 부족합니다!</div>';
    var two='<div class="alert alert-danger"><strong>'+data.user+' (이)는</strong> 굉장히 쏘고 싶은데 돈이 없다!</div>';
    var three='<div class="alert alert-danger"><strong>'+data.user+' (이)는</strong> 지갑이 텅텅 비어서 쓸 돈이 없다ㅜㅜ</div>';
    var four='<div class="alert alert-danger"><strong>'+data.user+' (이)는</strong> 가난한 장발장이다</div>';
    var five='<div class="alert alert-danger"><strong>'+data.user+' (이)는</strong> 크레딧이 없어서 말문이 막혔다</div>';
    var r=Math.floor(Math.random() * 5);
    console.log(r);
    var state;
    switch(r){
      case 0:
        state=one;
        break;
      case 1:
        state=two;
        break;
      case 2:
        state=three;
        break;
      case 3:
        state=four;
        break;
      case 4:
        state=five;
        break;
    }
    var credit={
      key: "poor",
      state: state
    };
    messages.push(credit);
    broadcast("poor", credit);
  }
  else if (data.key=='credit'){
    var credit={
      key: "credit",
      name: data.user,
      credit: data.credit,
    };
    messages.push(credit);
    broadcast("credit", credit);
    broadcast("admin_credit",data.total);
  }
  else if(parseInt(data.value)&&data.key=='clear'){
    messages=[];
    broadcast('clear');
  }
  else if(parseInt(data.value)&&data.key=='next'){
    var info={
        key: "message",
        text: "#alert"+data.name
      }
      messages.push(info);
      broadcast('message',info);
  }
});


io.on('connection', function (socket) {
    
    messages.forEach(function (data) {
      if(data.key=="message"){
        socket.emit('message', data);
      }
      else if(data.key=="credit"){
        socket.emit('credit', data);
      }
      else{
        socket.emit('poor', data);
      }
      
    });

    sockets.push(socket);
    
    
    //--연결 해제 소켓
    socket.on('disconnect', function () {
      sockets.splice(sockets.indexOf(socket), 1);
      updateRoster();
    });
    
    //--서버 메세지 수신 소켓
    socket.on('message', function (msg) {
      console.log('message');
      var text = String(msg || '');

      if (!text)
        return;
        
      var data={
        key: "message",
        name: socket.name,
        text: text
      };

      broadcast('message', data);
      messages.push(data);
    });
    
    //--서버 이용자 등록 소켓
    socket.on('identify', function (name) {
      socket.name=String(name || 'Anonymous');
      updateRoster();
    });
    
    //--별풍선 수신 소켓
    django(socket,'credit');
    
    django(socket,'clear');
    
    django(socket,'next');
    
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

function django(socket,event){
  socket.on(event,function(data){
    console.log(event);
    values = querystring.stringify({
            key: event,
            content: data,
            sessionid: socket.request.headers.cookie.sessionid,
        });
        // console.log(socket.request.headers.cookie.sessionid);
        var options = {
            host: 'localhost',
            port: 8080,
            path: '/addict/node_api',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': values.length
            }
        };
        
        //Send message to Django server
        var req = http.request(options, function(res){
            res.setEncoding('utf8');
        });
        
        req.write(values);
        req.end();
  })
}

server.listen(8081, function(){
  var addr = server.address();
  console.log("Chat server listening at", addr.address + ":" + addr.port);
  // console.log("start");
});