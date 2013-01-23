basePath = '../../';

files = [
  ANGULAR_SCENARIO,
  ANGULAR_SCENARIO_ADAPTER,
  'jstests/e2e/**/*.js'
];

autoWatch = false;

browsers = ['PhantomJS'];

singleRun = true;

urlRoot = '/__testacular/';

proxies = {
  '/': 'http://localhost:6543/'
};

junitReporter = {
  outputFile: 'test_out/e2e.xml',
  suite: 'e2e'
};
