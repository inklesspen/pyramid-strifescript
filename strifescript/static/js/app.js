'use strict'; /* global angular */


// Declare app level module which depends on filters, and services
angular.module('strifescript', ['ui.state', 'strifescript.controllers', 'strifescript.directives', 'strifescript.filters', 'strifescript.services']).
  config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $stateProvider.
      state('view1', {
        url: '/view1',
        templateUrl: 'partial1',
        controller: 'MyCtrl1'
      }).
      state('view2', {
        url: '/view2',
        templateUrl: 'partial2',
        controller: 'MyCtrl2'
      }).
      state('overview', {
        url: '/me',
        templateUrl: 'user_overview',
        controller: 'UserOverviewCtrl',
        auth: true
      });

    $urlRouterProvider.otherwise('view1');
  }]).
  run(['$rootScope', 'loginKeeper', '$state', function($rootScope, loginKeeper, $state) {
    $rootScope.$on('$stateChangeStart', function(event, to, toParams, from, fromParams) {
//      console.log([event, to, toParams, from, fromParams]);
      if (to.auth && !loginKeeper.isLoggedIn()) {
        event.preventDefault();
        $state.transitionTo('view1');
      }
    });
  }]);
