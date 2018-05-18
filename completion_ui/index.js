var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var client = require('./connection.js');  

INDEX = 'addresses'

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  socket.on('address message', function(msg){
  	//Call elasticsearch here
  	client.search({  
	  index: INDEX,
	  body: {
	    suggest:{
         name_suggest:{
            prefix: msg,
            completion:{
               field:"suggestions",
               size: 10
            }
         }
      }
	}
	},function (error, response,status) {
	    if (error){
	      console.log("search error: "+error)
	    }
	    else {
	      console.log("--- Response ---");
	      console.log(response);
	      console.log("--- Hits ---");
	      //response.hits.hits.forEach(function(hit){
	      response.suggest.name_suggest.forEach(function(hit){
	        // console.log(hit);
	        socket.emit('address message', 'clear');
	        for (var i = 0; i < hit['options'].length; i++) {
	            socket.emit('address message', JSON.stringify(hit['options'][i]['_source']['full_address']));
	            console.log(hit['options'][i]['_source']['full_address']);
	        }
	      })
	    }
	});

    console.log('message: ' + msg);
  });

  socket.on('with location', function(msg, lat, lon){
  	//Call elasticsearch here
  	client.search({  
	  index: INDEX,
	  body: {
	    suggest:{
         name_suggest:{
            prefix: msg,
            completion:{
               	field:"suggestions",
               	size: 10, 
               	contexts: {
               		location: {
               			lat: lat, 
               			lon: lon
	               		}
	               	}
	            }
	         }
	      }
		}
	},function (error, response,status) {
		console.log(lat);
	    if (error){
	      console.log("search error: "+error)
	    } else {
	      console.log("--- Response ---");
	      console.log(lat)
	      console.log(lon)
	      console.log("--- Hits ---");

	      response.suggest.name_suggest.forEach(function(hit){
	        socket.emit('with location', '----- With location below -----');
	        for (var i = 0; i < hit['options'].length; i++) {
	        	console.log(hit['options'][i]['_source']['suggestions']['contexts']); 
	            socket.emit('with location', JSON.stringify(hit['options'][i]['_source']['full_address'])); 

	            console.log(lat, lon);
	        }
	      })
	    }
	});

 //  	socket.emit('chat message', 'with location')

});
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});