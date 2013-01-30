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

describe('strifescript.services / loginKeeper', function() {
  beforeEach(function() {
    module('strifescript.services');
  });

  it('should return a promise which is resolved with the logged in username. should only call the callback once, and keep the provided username', inject(function($rootScope, loginKeeper, $q) {
    var deferred = $q.defer();
    var callback = jasmine.createSpy('loginRequiredCallback');
    callback.andReturn(deferred.promise);
    loginKeeper.registerLoginRequiredCallback(callback);
    var promise = loginKeeper.acquireLogin();
    var promiseThen = jasmine.createSpy('promiseThen');
    promise.then(promiseThen);

    var promise2 = loginKeeper.acquireLogin();
    var promiseThen2 = jasmine.createSpy('promiseThen');
    promise2.then(promiseThen2);
    deferred.resolve('testUser');
    $rootScope.$apply();
    expect(promiseThen).toHaveBeenCalledWith('testUser');
    expect(promiseThen2).toHaveBeenCalledWith('testUser');
    expect(callback.calls.length).toBe(1);
  }));
});
