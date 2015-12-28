angular
    .module('matchupApp', ['ngRoute', 'ngStorage', 'matchupControllers'])
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
            .when('/cards', {
                controller: 'CardCtrl',
                templateUrl: 'cards.html',
                resolve: {'init': function (init) { return init; }}
            })
            .when('/table', {
                controller: 'DbCtrl',
                templateUrl: 'table.html',
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
    .factory('filterService', function (filterFilter, $localStorage, gamesLibrary) {
        return new FilterService(filterFilter, $localStorage, gamesLibrary);
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
    var tags = {};

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

        function addToIndex(items, index) {
            angular.forEach(items, function (item) {
                if (!index.hasOwnProperty(item)) {
                    index[item] = 0;
                }

                index[item]++;
            })
        }

        addToIndex(game.features, features);
        addToIndex(game.genres, genres);
        addToIndex(game.tags, tags);
    };

    self.getGames = function getGames() {
        return gameList;
    };

    self.getFeatures = function getFeatures() {
        var featureModels = [];
        for (var feature in features) {
            if (!features.hasOwnProperty(feature)) {
                continue;
            }

            featureModels.push({
                name: feature,
                count: features[feature]
            })
        }
        return featureModels;
    };

    self.getGenres = function getGenres() {
        var genreModels = [];
        for (var genre in genres) {
            if (!genres.hasOwnProperty(genre)) {
                continue;
            }

            genreModels.push({
                name: genre,
                count: genres[genre]
            })
        }
        return genreModels;
    };

    self.getTags = function getTags() {
        var tagModels = [];
        for (var tag in tags) {
            if (!tags.hasOwnProperty(tag)) {
                continue;
            }

            tagModels.push({
                name: tag,
                count: tags[tag]
            });
        }
        return tagModels;
    }
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

function FilterService($filterFilter, $localStorage, gamesLibrary) {
    var self = this;

    var storage = $localStorage.$default({
        features: [],
        genres: [],
        tags: []
    });

    function toggle(items, value, select) {
        var index = items.indexOf(value);
        if (select == undefined) {
            select = index == -1;
        }

        if (select) {
            items.push(value);
        } else {
            items.splice(index, 1);
        }
    }

    self.toggleFeature = function toggleFeature(feature) {
        toggle(storage.features, feature);
    };

    self.toggleGenre = function toggleGenre(genre) {
        toggle(storage.genres, genre);
    };

    self.toggleTag = function toggleTag(tag) {
        toggle(storage.tags, tag);
    };

    self.getSelectedFeatures = function getSelectedFeatures() {
        return storage.features;
    };

    self.getSelectedGenres = function getSelectedGenres() {
        return storage.genres;
    };

    self.getSelectedTags = function getSelectedTags() {
        return storage.tags;
    };

    function hasAllItems(needles, haystack) {
        if (needles.length == 0) {
            return true;
        }

        for (var index = 0; index < needles.length; index++) {
            if (haystack.indexOf(needles[index]) === -1) {
                return false;
            }
        }

        return true;
    }

    self.getFilteredGames = function getFilteredGames() {
        var games = gamesLibrary.getGames();

        var selectedFeatures = self.getSelectedFeatures();
        var selectedGenres = self.getSelectedGenres();
        var selectedTags = self.getSelectedTags();

        return $filterFilter(games, function (game) {
            if (!hasAllItems(selectedFeatures, game.features)) {
                return false;
            }

            if (!hasAllItems(selectedGenres, game.genres)) {
                return false;
            }

            if (!hasAllItems(selectedTags, game.tags)) {
                return false;
            }

            return true;
        });
    }
}
