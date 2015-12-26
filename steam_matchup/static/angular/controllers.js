angular.module('matchupControllers', ['ngCookies'])
    .controller('FilterCtrl', function ($location, $cookies, $scope, gamesLibrary, filterService) {
        function createSelectableModels(items, selectedItems) {
            var models = [];
            for (var itemIndex = 0; itemIndex < items.length; itemIndex++) {
                var item = items[itemIndex];
                var model = {
                    label: item.name,
                    count: item.count,
                    selected: selectedItems.indexOf(item.name) != -1
                };
                models.push(model);
            }
            return models;
        }

        function refreshCounts() {
            var games = gamesLibrary.getGames();
            var filteredGames = filterService.getFilteredGames();

            $scope.matched_games_count = filteredGames.length;
            $scope.total_games_count = games.length;
        }

        $scope.features = createSelectableModels(
            gamesLibrary.getFeatures(),
            filterService.getSelectedFeatures()
        );

        $scope.genres = createSelectableModels(
            gamesLibrary.getGenres(),
            filterService.getSelectedGenres()
        );

        var toggleMap = {
            genre: function (v, s) {
                filterService.toggleGenre(v, s);
            },
            feature: function (v, s) {
                filterService.toggleFeature(v, s);
            }
        };
        $scope.toggle = function toggle(type, value) {
            var f = toggleMap[type];
            f(value.label, value.selected);
            refreshCounts();
        };

        $scope.done = function done() {
            $location.path('/db');
        };

        refreshCounts();
    })
    .controller('DbCtrl', function(
        $location, $cookies, $rootScope,
        $scope, $filter, gamesLibrary, filterService
    ) {
        $scope.gamers = [];
        $scope.games = gamesLibrary.getGames();

        // paging, taken from http://jsfiddle.net/SAWsA/1754/
        $scope.sort = {
            sortingOrder: 'id',
            reverse: false
        };

        // paging config
        $scope.gap = 5;
        $scope.itemsPerPage = 10;

        $scope.filteredItems = [];
        $scope.groupedItems = [];
        $scope.pagedItems = [];
        $scope.currentPage = 0;

        $scope.prevPage = function prevPage() {
            if ($scope.currentPage > 0) {
                $scope.currentPage--;
            }
        };

        $scope.setPage = function setPage() {
            $scope.currentPage = this.n;
        };

        $scope.nextPage = function nextPage() {
            if ($scope.currentPage < $scope.pagedItems.length - 1) {
                $scope.currentPage++;
            }
        };

        $scope.search = function search() {
            $scope.filteredItems = filterService.getFilteredGames();

            if ($scope.sort.sortingOrder !== '') {
                var $orderBy = $filter('orderBy');
                $scope.filteredItems = $orderBy(
                    $scope.filteredItems,
                    $scope.sort.sortingOrder,
                    $scope.sort.reverse
                );
            }

            $scope.currentPage = 0;
            $scope.groupToPages();
        };

        $scope.groupToPages = function groupToPages() {
            $scope.pagedItems = [];

            for (var i = 0; i < $scope.filteredItems.length; i++) {
                var pageIndex = Math.floor(i / $scope.itemsPerPage);
                var item = $scope.filteredItems[i];
                if (i % $scope.itemsPerPage === 0) {
                    $scope.pagedItems[pageIndex] = [item];
                } else {
                    $scope.pagedItems[pageIndex].push(item);
                }
            }
        };

        $scope.range = function (size, start, end) {
            var ret = [];
            if (size < end) {
                end = size;
                start = size - $scope.gap;
            }

            for (var i = start; i < end; i++) {
                ret.push(i);
            }

            return ret;
        };

        $scope.search();
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
