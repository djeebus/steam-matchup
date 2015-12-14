angular
    .module('matchupApp', ['ngRoute', 'matchupControllers'])
    .config(['$compileProvider', function ($compileProvider) {
        // steam:// links are also acceptable
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|steam):/);
    }])
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
                templateUrl: 'db.html',
                resolve: {'init': function (init) { return init; }}
            })
            .when('/filters', {
                controller: 'FilterCtrl',
                templateUrl: 'filter.html',
                resolve: {'init': function (init) { return init; }}
            })
            .otherwise({
                redirectTo: '/'
            });
    }])
    .factory('profileId', function ($cookies, $location) {
        var profileId = $cookies.get('profile_id');
        if (!profileId) {
            $location.path('/login');
            return;
        }

        return profileId;
    })
    .factory('init', function (profileId, apiClient, gamesLibrary, $q) {
        return $q(function (resolve, reject) {
            apiClient
                .getGamers([profileId])
                .then(function (gamers) {
                    var gamer = gamers[0];

                    var missingGameIds = [];
                    angular.forEach(gamer.gameIds, function (gameId) {
                        if (!gamesLibrary.hasGame(gameId)) {
                            missingGameIds.push(gameId);
                        }
                    });

                    apiClient.getGames(missingGameIds)
                        .then(function (games) {
                            angular.forEach(games, function (game) {
                                gamesLibrary.addGame(game);
                            });

                            resolve();
                        });
                });
        });
    })
    .factory('gamesLibrary', function () {
        return new GamesLibrary();
    })
    .factory('apiClient', function ($http, $q) {
        return new ApiClient($http, $q);
    });


function GamesLibrary() {
    var self = this;

    var gameMap = {};
    var gameList = [];
    var features = {};
    var genres = {};

    self.getGame = function getGame(gameId) {
        if (!self.hasGame(gameId)) {
            return null;
        }

        return gameMap[gameId];
    };

    self.hasGame = function hasGame(gameId) {
        return gameMap.hasOwnProperty(gameId);
    };

    self.addGame = function addGame(game) {
        if (self.hasGame(game.id)) {
            console.warn('game already exists: ', game);
            return;
        }

        gameMap[game.id] = game;
        gameList.push(game);

        angular.forEach(game.features, function (f) {
            if (!features.hasOwnProperty(f)) {
                features[f] = 0;
            }

            features[f]++;
        });

        angular.forEach(game.genres, function (g) {
            if (!genres.hasOwnProperty(g)) {
                genres[g] = 0;
            }

            genres[g]++;
        });
    };

    self.getGames = function getGames() {
        return gameList;
    };

    self.getFeatures = function getFeatures() {
        return Object.keys(features);
    };

    self.getFeatureCounts = function getFeatureCounts() {
        return features;
    };

    self.getGenres = function getGenres() {
        return Object.keys(genres);
    };

    self.getGenreCounts = function getGenreCounts() {
        return genres;
    };
}

function ApiClient($http, $q) {
    var self = this;

    self.getGamers = function getGamers(gamerIds) {
        var qsParams = gamerIds.map(function (gamerId) {
            return 'gamerId=' + gamerId;
        });

        return $q(function (resolve, reject) {
            $http.get('/api/gamers?' + qsParams.join('&'))
                .then(function (response) {
                    resolve(response.data.results);
                }, reject);
        });
    };

    self.getGames = function getGames(gameIds) {
        var qsParams = gameIds.map(function (gameId) {
            return 'gameId=' + gameId;
        });

        return $q(function (resolve, reject) {
            $http.get('/api/games?' + qsParams.join('&'))
                .then(function (response) {
                    var games = [];
                    angular.forEach(response.data.results, function (game) {
                        if (!game.isValid) {
                            return;
                        }

                        games.push(game);
                    });

                    resolve(games);
                }, reject);
        });
    };
}
