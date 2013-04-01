'use strict'; /* global angular */

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('strifescript.services', []).
  factory('loginKeeper', [function() {
    var current = {
      username: null
    };
    return {
      isLoggedIn: function() {
        return current.username !== null;
      },
      getUsername: function(username) {
        return current.username;
      },
      setUsername: function(username) {
        current.username = username;
      }
    };
  }]).
  factory('api', ['$http', '$q', function($http, $q) {
    return {
      register: function(username, password, email) {
        var args = {'username': username, 'password': password};
        if (email) {
          args['email'] = email;
        }
        return $http.post('/api/register', args).then(function(response) {
          if (response.data.errors) {
            return $q.reject(response.data.errors);
          }
          return username;
        });
      },
      login: function(username, password) {
        var args = {'username': username, 'password': password};
        return $http.post('/api/login', args).then(function(response) {
          if (response.data.errors) {
            return $q.reject(response.data.errors);
          }
          return response.data['current_user'];
        });
      },
      logout: function() {
        return $http.post('/api/logout', {}).then(function(response) {
          if (response.data.errors) {
            return $q.reject(response.data.errors);
          }
          return null;
        });
      }
    };
  }]).
  factory('oldloginKeeper', ['$q', function($q) {
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
