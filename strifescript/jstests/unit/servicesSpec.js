'use strict'; /* global describe, beforeEach, afterEach, module, it, inject, expect, jasmine */

/* jasmine specs for services go here */

describe('strifescript.services / preloader', function() {
  var $httpBackend;

  beforeEach(function() {
    module('strifescript.services');
    module(function($provide) {
      $provide.factory('loginKeeper', function ($q) {
        var loginDeferred;
        return {
          acquireLogin: function() {
            loginDeferred = $q.defer();
            return loginDeferred.promise;
          },
          resolveDeferred: function(data) {
            loginDeferred.resolve(data);
          }
        };
      });
    });
   inject(function($injector) {
     $httpBackend = $injector.get('$httpBackend');
   });
  });

 afterEach(function() {
   $httpBackend.verifyNoOutstandingExpectation();
   $httpBackend.verifyNoOutstandingRequest();
 });

  it('should be able to fetch user info', inject(function($rootScope, preloader, loginKeeper) {
    var conflictInfo = ["derp", "herp"];
    $httpBackend.expectGET('/api/conflicts').respond(conflictInfo);
    var promise = preloader.allConflicts();
    loginKeeper.resolveDeferred('testUser');
    var promiseThen = jasmine.createSpy('promiseThen');
    promise.then(promiseThen);
    $rootScope.$apply();
    $httpBackend.flush();
    expect(promiseThen).toHaveBeenCalledWith(conflictInfo);
  }));
});
