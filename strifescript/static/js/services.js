'use strict'; /* global angular */

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('strifescript.services', []).
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
