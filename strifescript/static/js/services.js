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
      },
      list_conflicts: function() {
        return $http.get('/api/conflicts').then(function(response) {
          return response.data;
        });
      },
      get_conflict: function(id) {
        return $http.get('/api/conflict/' + id).then(function(response) {
          return response.data;
        });
      }
    };
  }]);
