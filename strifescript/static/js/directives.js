'use strict'; /* global angular */

/* Directives */


angular.module('strifescript.directives', []).
  directive('appVersion', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }]);
