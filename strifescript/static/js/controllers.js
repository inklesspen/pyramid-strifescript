'use strict'; /* global angular */

/* Controllers */

angular.module('strifescript.controllers', []).
  controller('PreloadCtrl', ['$scope', 'loginKeeper', function($scope, loginKeeper) {
    $scope.setUsername = function(username) {
      loginKeeper.setUsername(username);
    };
  }]).
  controller('MenuBarCtrl', ['$scope', '$state', 'loginKeeper', 'api', function($scope, $state, loginKeeper, api) {
    $scope.loggedIn = loginKeeper.isLoggedIn();
    $scope.$watch(function(scope) {return loginKeeper.isLoggedIn();}, function(newValue, oldValue, scope) {scope.loggedIn = newValue;});
    $scope.isActive = function(stateName) {
      return $state.is(stateName) ? "active" : "";
    };
    $scope.logout = function() {
      api.logout().then(function() {
        loginKeeper.setUsername(null);
        $state.transitionTo('home');
      });
    };
  }]).
  controller('UserOverviewCtrl', ['$scope', 'loginKeeper', function($scope, loginKeeper) {
    $scope.user = {'username': loginKeeper.getUsername()};
  }]).
  controller('LoginRegisterCtrl', ['$scope', '$state', 'api', 'loginKeeper', function($scope, $state, api, loginKeeper) {
    var go = function(username) {
      loginKeeper.setUsername(username);
      $state.transitionTo($state.params.next);
    };

    var actions = {
      register: function() {
        api.register($scope.username, $scope.password, $scope.email).then(go, function(errors) {
          $scope.errors = errors;
        });
      },
      login: function() {
        api.login($scope.username, $scope.password).then(go, function(errors) {
          $scope.errors = errors;
        });
      }
    };

    $scope.actions = actions;
  }]);
