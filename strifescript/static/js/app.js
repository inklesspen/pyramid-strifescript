'use strict'; /* global angular */


// Declare app level module which depends on filters, and services
angular.module('strifescript', ['strifescript.controllers', 'strifescript.directives', 'strifescript.filters', 'strifescript.services']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/me', {templateUrl: 'user_overview', controller: 'UserOverviewCtrl', resolve: {'allConflicts': ['preloader', function(preloader) {return preloader.allConflicts();}]}});
    $routeProvider.when('/view1', {templateUrl: 'partial1', controller: 'MyCtrl1'});
    $routeProvider.when('/view2', {templateUrl: 'partial2', controller: 'MyCtrl2'});
    $routeProvider.otherwise({redirectTo: '/view1'});
  }]);
