'use strict'; /* global angular */

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('strifescript.services', []).
  factory('loginKeeper', ['$q', function($q) {
    var loginRequiredCallback = angular.noop();
    var currentUsername = null;
    var currentPromise = null;
    return {
      acquireLogin: function() {
        if (currentPromise !== null) {
          return currentPromise;
        }
        if (currentUsername === null) {
          var promise = loginRequiredCallback();
          promise = promise.then(function(value) {
            currentUsername = value;
            currentPromise = null;
            return value;
          });
          currentPromise = promise;
          return promise;
        } else {
          var deferred = $q.defer();
          deferred.resolve(currentUsername);
          return deferred.promise;
        }
      },
      registerLoginRequiredCallback: function(callback) {
        loginRequiredCallback = callback;
      }
    };
  }]).
  factory('preloader', ['$q', '$http', 'loginKeeper', function($q, $http, loginKeeper) {
    return {
      allConflicts: function() {
        var deferred = $q.defer();
        var loginPromise = loginKeeper.acquireLogin();
        loginPromise.then(function(username) {
          $http.get('/api/conflicts').success(function(data, status, headers, config) {
            deferred.resolve(data);
          });
        });
        return deferred.promise;
      }
    };
  }]).
  value('version', '0.1');
