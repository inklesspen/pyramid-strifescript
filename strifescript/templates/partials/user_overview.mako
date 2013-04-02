<p>Username is {{user.username}}.
Let's do this thing.</p>


<table class="table table-condensed table-hover">
  <thead>
    <tr>
      <th>Conflict Name</th>
    </tr>
  </thead>
  <tbody>
    <tr ng-repeat="conflict in conflicts">
      <td><a ng-href="#/conflict/{{conflict.id}}">{{conflict.name}}</a></td>
    </tr>
  </tbody>
</table>