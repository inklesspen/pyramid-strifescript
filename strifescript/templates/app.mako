<!doctype html>
<html lang="en" ng-app="strifescript">
<head>
  <meta charset="utf-8">
  <title>My AngularJS App</title>
  <link rel="stylesheet" href="${request.static_path('strifescript:static/vendor/bootstrap-2.3.1/css/bootstrap.css')}"/>
  <link rel="stylesheet" href="${request.static_path('strifescript:static/css/app.css')}"/>
</head>
<body>
  <div >
  
    
    <div>
      <ul class="menu">
        <li><a href="#/">home</a></li>
        <li><a href="#/me">me</a></li>
      </ul>

      <div ui-view></div>

    </div>
  </div>

  <!-- In production use:
  <script src="//ajax.googleapis.com/ajax/libs/angularjs/1.0.2/angular.min.js"></script>
  -->
  <script src="${request.static_path('strifescript:static/lib/angular/angular.js')}"></script>
  <script src="${request.static_path('strifescript:static/lib/angular-ui-states.js')}"></script>
  <script src="${request.static_path('strifescript:static/js/app.js')}"></script>
  <script src="${request.static_path('strifescript:static/js/services.js')}"></script>
  <script src="${request.static_path('strifescript:static/js/controllers.js')}"></script>
  <script src="${request.static_path('strifescript:static/js/filters.js')}"></script>
  <script src="${request.static_path('strifescript:static/js/directives.js')}"></script>

% for partial in ['home', 'user_overview', 'login_register']:
<script type="text/ng-template" id="${partial}">
<%include file="strifescript:templates/partials/${partial}.mako" />
</script>
% endfor

</body>
</html>
