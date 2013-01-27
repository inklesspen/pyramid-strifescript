'use strict'; /* global angular */

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('strifescript.services', []).
  value('version', '0.1');
