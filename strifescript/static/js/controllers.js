'use strict'; /* global angular */

/* Controllers */

angular.module('strifescript.controllers', []).
  controller('LoginRegisterCtrl', ['loginKeeper', '$scope', '$q', function(loginKeeper, $scope, $q) {
    $scope.showForm = false;
    var pendingLoginDeferred = null;
    var loginRequiredCallback = function() {
      if (pendingLoginDeferred === null) {
        pendingLoginDeferred = $q.defer();
        $scope.showForm = true;
      }

      return pendingLoginDeferred.promise;
    };
    loginKeeper.registerLoginRequiredCallback(loginRequiredCallback);

    $scope.yes = function() {
      pendingLoginDeferred.resolve("testUser");
      $scope.showForm = false;
    };
    $scope.no = function() {
      pendingLoginDeferred.reject("rejected");
      $scope.showForm = false;
    };
  }]).
  controller('UserOverviewCtrl', ['allConflicts', function(allConflicts) {}]).
  controller('MyCtrl1', [function() {}]).
  controller('MyCtrl2', [function() {}]);
