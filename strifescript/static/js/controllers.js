'use strict'; /* global angular */

/* Controllers */

angular.module('strifescript.controllers', []).
  controller('UserOverviewCtrl', ['$scope', 'loginKeeper', function($scope, loginKeeper) {
    $scope.user = {'username': loginKeeper.getUsername()};
  }]).
  controller('LoginRegisterCtrl', ['$scope', '$state', 'loginKeeper', function($scope, $state, loginKeeper) {
    $scope.go = function() {
      loginKeeper.setUsername($scope.username);
      $state.transitionTo($state.params.next);
    };
    console.log($state);
  }]).
  controller('MyCtrl1', [function() {}]).
  controller('MyCtrl2', [function() {}]);
