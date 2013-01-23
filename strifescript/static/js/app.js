'use strict'; /* global angular */


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.controllers', 'myApp.filters', 'myApp.services', 'myApp.directives']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/view1', {templateUrl: 'partial1', controller: 'MyCtrl1'});
    $routeProvider.when('/view2', {templateUrl: 'partial2', controller: 'MyCtrl2'});
    $routeProvider.otherwise({redirectTo: '/view1'});
  }]);
