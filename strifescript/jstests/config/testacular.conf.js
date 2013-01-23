basePath = '../../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'static/lib/angular/angular.js',
  'static/lib/angular/angular-*.js',
  'jstests/lib/angular/angular-mocks.js',
  'static/js/**/*.js',
  'jstests/unit/**/*.js'
];

autoWatch = true;

browsers = ['PhantomJS'];

junitReporter = {
  outputFile: 'test_out/unit.xml',
  suite: 'unit'
};
