'use strict'; /* global angular */


// Declare app level module which depends on filters, and services
angular.module('strifescript', ['ui', 'ui.state', 'strifescript.controllers', 'strifescript.directives', 'strifescript.filters', 'strifescript.services']).
  config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $stateProvider.
      state('home', {
        url: '/',
        templateUrl: 'home'
      }).
      state('login', {
        templateUrl: 'login_register',
        controller: 'LoginRegisterCtrl',
        params: ['next']
      }).
      state('overview', {
        url: '/me',
        templateUrl: 'user_overview',
        controller: 'UserOverviewCtrl',
        auth: true
      }).
      state('conflict', {
        url: '/conflict/:conflictId',
        templateUrl: 'conflict',
        controller: 'ConflictCtrl',
        auth: true
      });

    $urlRouterProvider.otherwise('/');
  }]).
  run(['$rootScope', 'loginKeeper', '$state', function($rootScope, loginKeeper, $state) {
    $rootScope.$on('$stateChangeStart', function(event, to, toParams, from, fromParams) {
//      console.log([event, to, toParams, from, fromParams]);
      if (to.auth && !loginKeeper.isLoggedIn()) {
        event.preventDefault();
        // TODO: find some way of preserving the next stateParams?
        $state.transitionTo('login', {next: to.name});
      }
    });
  }]);
