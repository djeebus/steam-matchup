angular.module('matchupControllers', ['ngCookies'])
    .controller('HomeCtrl', function ($location, $rootScope, $cookies) {
        var profileId = $cookies.get('profile_id');

        if (!profileId) {
            $location.path('/login');
            return;
        }

        $rootScope.profileId = profileId;
        $location.path('/db');
    })
    .controller('DbCtrl', function($location, $cookies, $scope, $http) {
        var profileId = $cookies.get('profile_id');
        if (!profileId) {
            $location.path('/login');
            return;
        }

        var vm = $scope;
        vm.gamers = [];
        vm.games = [];

        $http
            .get('/api/gamers?gamerIds=' + profileId)
            .then(function (response) {
                angular.forEach(response.data.results, function (gamer) {
                    angular.forEach(gamer.friends, function (friend) {
                        vm.gamers.push(friend);
                    });

                    angular.forEach(chunk(gamer.gameIds, 20), function (chunkOfGameIds) {
                        var qs = chunkOfGameIds.map(function (id) {
                            return 'gameIds=' + id;
                        });
                        $http
                            .get('/api/games?' + qs.join('&'))
                            .then(function (response) {
                                var chunkOfGameInfos = response.data.results;
                                angular.forEach(chunkOfGameInfos, function (gameInfo) {
                                    if (!gameInfo.isValid) {
                                        console.log("invalid game!", gameInfo);
                                        return;
                                    }
                                    vm.games.push(gameInfo);
                                });
                            });
                    });
                });
            });
    })
    .controller('AppCtrl', function ($rootScope) {
        $rootScope.on('$routeChangeError', function () {
            console.log('failed to change routes');
        });
    });


function chunk(array, chunkSize) {
    var i, j, tempArray = [];
    for (i = 0, j = array.length; i < j; i += chunkSize) {
        tempArray.push(array.slice(i, i + chunkSize));
    }
    return tempArray;
}
