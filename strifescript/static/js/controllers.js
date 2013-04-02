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
  controller('UserOverviewCtrl', ['$scope', 'loginKeeper', 'api', function($scope, loginKeeper, api) {
    $scope.user = {'username': loginKeeper.getUsername()};
    api.list_conflicts().then(function(conflicts) {
      $scope.conflicts = conflicts;
    });
  }]).
  controller('ConflictCtrl', ['$scope', '$state', 'api', 'loginKeeper', function($scope, $state, api, loginKeeper) {
    $scope.isArray = angular.isArray;
    $scope.isString = angular.isString;
    var deconstruct = function(conflict) {
      var username = loginKeeper.getUsername();
      _.forEach(conflict.teams, function(team) {
        team.myTeam = _.contains(team.participants, username);
      });
      
      $scope.teamIds = _.pluck(conflict.teams, 'id');
      $scope.teams = _.zipObject($scope.teamIds, conflict.teams);

      $scope.currentExchange = _.zipObject(_.last(conflict.exchanges));

      $scope.pastExchanges = _.map(_.initial(conflict.exchanges), function(exchange, i) {return [i+1, _.zipObject(exchange)];});
      $scope.pastExchanges.reverse();

      $scope.actionChoices = _.zipObject(conflict.action_choices);

//      var exchangesByTeam = _.map(conflict.exchanges, function(exchange) {return _.zipObject(exchange);});
      
//      $scope.teamExchanges = _.zipObject($scope.teamIds, conflict.

      $scope.teamIds.sort();

    };

    api.get_conflict($state.params.conflictId).then(function(conflict) {
      console.log(conflict);
      deconstruct(conflict);
      $scope.conflict = conflict;
    });
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
