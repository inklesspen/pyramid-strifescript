'use strict'; /* global angular */

/* Controllers */

angular.module('strifescript.controllers', []).
  controller('UserOverviewCtrl', ['$scope', function($scope) {
    $scope.user = {'username': 'nobody'};
  }]).
  controller('MyCtrl1', [function() {}]).
  controller('MyCtrl2', [function() {}]);
