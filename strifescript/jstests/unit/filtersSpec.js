'use strict'; /* global describe, beforeEach, module, it, inject, expect */

/* jasmine specs for filters go here */

describe('filter', function() {
  beforeEach(module('strifescript.filters'));


  describe('interpolate', function() {
    beforeEach(module(function($provide) {
      $provide.value('version', 'TEST_VER');
    }));


    it('should replace VERSION', inject(function(interpolateFilter) {
      expect(interpolateFilter('before %VERSION% after')).toEqual('before TEST_VER after');
    }));
  });
});
