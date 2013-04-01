<!doctype html>
<html lang="en" ng-app="strifescript">
<head>
  <meta charset="utf-8">
  <title>My AngularJS App</title>
  <link rel="stylesheet" href="${request.static_path('strifescript:static/vendor/bootstrap-2.3.1/css/bootstrap.css')}"/>
  <link rel="stylesheet" href="${request.static_path('strifescript:static/css/app.css')}"/>
</head>
<body>
  <div ng-controller="PreloadCtrl" ng-init="setUsername(${('\'' + request.current_user.username + '\'') if request.current_user is not None else 'null'})"></div>
  <div class="container">
    <div class="navbar" ng-controller="MenuBarCtrl">
      <div class="navbar-inner">
        <a class="brand" href="#/">Strifescript</a>
        <ul class="nav">
          <li ng-class="isActive('home')"><a href="#/">Home</a></li>
          <li ng-class="isActive('overview')"><a href="#/me">Account Overview</a></li>
        </ul>

        <ul class="nav pull-right" ng-show="loggedIn">
          <li><a href="#" ng-click="logout()">Logout</a></li>
        </ul>
      </div>
    </div>
    

      <div ui-view></div>

  </div>

  <script src="${request.static_path('strifescript:static/vendor/jquery-1.8.3.min.js')}"></script>
  <script src="${request.static_path('strifescript:static/vendor/bootstrap-2.3.1/js/bootstrap.js')}"></script>
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
