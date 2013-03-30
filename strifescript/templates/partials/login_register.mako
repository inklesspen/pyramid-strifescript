<div class="row">
  <div class="span12">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#login" data-toggle="tab">Login</a></li>
      <li><a href="#register" data-toggle="tab">Register</a></li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane active" id="login">
        <form class="form-horizontal" ng-submit="actions.login()">
          <div class="control-group">
            <label for="username" class="control-label">Username</label>
            <div class="controls">
              <input type="text" name="username" value="" id="username" ng-model="username">
            </div>
          </div>
          <div class="control-group">
            <label for="password" class="control-label">Password</label>
            <div class="controls">
              <input type="password" name="password" value="" id="password" ng-model="password">
            </div>
          </div>

          <div class="control-group">
            <div class="controls">
              <button type="submit" class="btn btn-success">Login</button>
            </div>
          </div>
        </form>
      </div>
      <div class="tab-pane" id="register">
        <form class="form-horizontal" ng-submit="actions.register()">
          <div class="control-group" ng-class="{'error': !!((errors['username'] || []).length > 0)}">
            <label for="username" class="control-label">Username</label>
            <div class="controls">
              <input type="text" name="username" value="" id="username" ng-model="username" required>
              <span class="help-inline" ng-repeat="error in errors['username']">{{error}}</span>
            </div>
          </div>
          <div class="control-group">
            <label for="password" class="control-label">Password</label>
            <div class="controls">
              <input type="password" name="password" value="" id="password" ng-model="password" required>
            </div>
          </div>
          <div class="control-group">
            <label for="email" class="control-label">Email</label>
            <div class="controls">
              <input type="text" name="email" value="" id="email" ng-model="email">
            </div>
          </div>

          <div class="control-group">
            <div class="controls">
              <button type="submit" class="btn btn-success">Register</button>
            </div>
          </div>
        </form>
      </div>
    </div>    
  </div>
</div>



