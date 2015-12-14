angular.module('matchupControllers', ['ngCookies'])
    .controller('FilterCtrl', function ($location, $cookies, $scope, gamesLibrary) {
        $scope.features = gamesLibrary.getFeatures();
        $scope.genres = gamesLibrary.getGenres();
    })
    .controller('DbCtrl', function($location, $cookies, $rootScope, $scope, gamesLibrary) {
        var vm = $scope;
        vm.gamers = [];
        vm.games = gamesLibrary.getGames();
    })
    .controller('HomeCtrl', function ($location, $rootScope, $cookies) {
        var profileId = $cookies.get('profile_id');

        if (!profileId) {
            $location.path('/login');
            return;
        }

        $rootScope.profileId = profileId;
        $location.path('/db');
    });


function chunk(array, chunkSize) {
    var i, j, tempArray = [];
    for (i = 0, j = array.length; i < j; i += chunkSize) {
        tempArray.push(array.slice(i, i + chunkSize));
    }
    return tempArray;
}
