var ISSChatApp = angular.module('MovieApp', []);
var socket = io.connect('https://' + document.domain + ':' + location.port + '/movie');

ISSChatApp.controller('SearchController', function($scope){
    
    $scope.name = '';
    $scope.text = '';
    $scope.searchResults = [];
    
    $scope.search = function search(){
        console.log('Search result: ', $scope.text);
        socket.emit('search', $scope.text);
        $scope.text = '';
    };
    
    socket.on('searchResults', function(results){
        for(var i = 0; i < results.length; i++){
            console.log(results[i]);
            $scope.searchResults.push(results[i]);
            $scope.$apply();
        }
        $scope.searchResults = [];
    });
    
    $scope.setName = function setName(){
      socket.emit('identify', $scope.name)  
    };
    
    socket.on('connect', function(){
       console.log('Connected'); 
    });
});

