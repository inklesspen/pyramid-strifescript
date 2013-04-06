<h1><small>Teams</small></h1>
<ul>
  <li ng-repeat="team in conflict.teams">
    <b>{{team.name}}</b><br>
    <ul>
      <li ng-repeat="participant in team.participants">
        {{participant}}
      </li>
    </ul>
  </li>
</ul>

<h1><small>Current Exchange</small></h1>
<table class="table table-condensed table-hover">
  <caption>Exchange {{conflict.exchanges.length}}</caption>
  <thead>
    <tr>
      <th>Team</th><th>Volley 1</th><th>Volley 2</th><th>Volley 3</th><th>Permitted Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr ng-repeat="teamId in teamIds">
      <td>{{teams[teamId].name}}</td>
      <td ng-repeat="volley in currentExchange[teamId].script">
        <span ui-if="isArray(volley)">
          <span ng-repeat="action in volley"><span ui-if="! $first">| </span><span>{{action}}</span>
          </span>
        </span>
        <span ui-if="isString(volley)" class="hidden-volley">hidden</span>
      </td>
      <td ui-if="teams[teamId].myTeam">
        <span class="btn-group"><a class="btn" ng-repeat="choice in actionChoices[teamId]" ng-click="doAction(teamId, choice)">{{choice}}</a></span>
      </td>
      <td ui-if="! teams[teamId].myTeam">
        <span ng-repeat="choice in actionChoices[teamId]"><span ui-if="! $first">| </span><span>{{choice}}</span></span>
      </td>
    </tr>
  </tbody>
</table>

<h1><small>Past Exchanges</small></h1>
<table class="table table-condensed table-hover" ng-repeat="exchange in pastExchanges">
  <caption>Exchange {{exchange[0]}}</caption>
  <thead>
    <tr>
      <th>Team</th><th>Volley 1</th><th>Volley 2</th><th>Volley 3</th>
    </tr>
  </thead>
  <tbody>
    <tr ng-repeat="teamId in teamIds">
      <td>{{teams[teamId].name}}</td>
      <td ng-repeat="volley in exchange[1][teamId].script">
        <span ng-repeat="action in volley"><span ui-if="! $first">| </span><span>{{action}}</span>
        </td>
    </tr>
  </tbody>
</table>
