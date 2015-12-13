angular
    .module('matchupApp', ['ngRoute', 'matchupControllers'])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                controller: 'HomeCtrl',
                template: ''
            })
            .when('/login', {
                templateUrl: 'auth.html'
            })
            .when('/db', {
                controller: 'DbCtrl',
                templateUrl: 'db.html'
            })
            .otherwise({
                redirectTo: '/'
            });
    }]);
