// http://store.steampowered.com/tagdata/populartags/english -- get popular tags
// http://store.steampowered.com/api/appdetails/?appids=550 -- get details for a game

function configureAjaxHandling() {
    var currentAjaxRequests = 0;
    $(document).ajaxSend(function () {
        currentAjaxRequests++;

        $('#ajax-in-progress').show();
    });

    $(document).ajaxComplete(function () {
        if (currentAjaxRequests <= 0) {
            return;
        }

        currentAjaxRequests--;

        if (currentAjaxRequests == 0) {
            $('#ajax-in-progress').hide();
        }
    });
}

var ViewModel = function () {
    var self = this;

    this.searchTerm = ko.observable('');

    this.results = ko.observableArray([]);
    this.results.subscribe(function (newValue) {
        if (!newValue || !newValue.length) {
            return;
        }

        if (newValue.length != 1) {
            return;
        }


        var result = newValue[0];
        if (!result.canSelect()) {
            return;
        }

        self.results([]);

        result.addResult();
    });

    this.numberOfCommonGamers = ko.observable(1);

    this.gamers = ko.observableArray([]);

    this.games = ko.observableArray([]);

    this.friends = ko.observableArray([]);

    this.features = ko.observableArray([]);

    this.genres = ko.observableArray([]);

    this.commonUsers = ko.observableArray([]);

    this.isSearching = ko.observable(false);

    this.displayFeatures = ko.observable(false);
    this.toggleFeatures = function () {
        this.displayFeatures(!this.displayFeatures());
    };

    this.showFilterDialog = function () {
        $('#filter-dialog').dialog({ width: 600 });
    };

    this.numberOfCommonGamers.subscribe(function () {
        self.recalculateGamesTable();
    });

    this.games.subscribe(function (newValue) {
        console.log('recalculating features of ' + newValue.length + ' games ... ');

        updateSelectableList(self.features, newValue, function (g) { return g.features; });
        updateSelectableList(self.genres, newValue, function (g) { return g.genres; });
    });

    this.games.subscribe(function () {
        self.recalculateGamesTable();
    });
    this.gamers.subscribe(function () {
        self.recalculateGamesTable();

        checkForMissingGameMetadata();

        updateCommonUsersList();
    });

    function updateCommonUsersList() {
        var gamers = rootModel.gamers();

        var users = [];
        for (var x = 1; x <= gamers.length; x++) {
            users.push({ name: x.toString(), value: x, id: 'u_' + x });
        }

        rootModel.commonUsers(users);
    }

    this.recalculateGamesTable = function () {
        console.log('recalculating games table ... ');

        var gamers = self.gamers();
        var games = self.games();

        games = filterGamesBySelectables(self.features, games, function (g) { return g.features; });
        games = filterGamesBySelectables(self.genres, games, function (g) { return g.genres; });

        var result = _.map(games, function (g) {
            var players = _.filter(gamers, function (p) {
                var gid = _.find(p.gameIds, function (gid) {
                    return gid == g.id;
                });

                return gid != null;
            });

            return {
                name: g.name,
                iconUrl: g.iconUrl,
                storeUrl: 'http://store.steampowered.com/app/' + g.id + '/',
                playUrl: 'steam://run/' + g.id,
                players: _.map(players, function (p) { return p.name; }),
                genres: g.genres,
                features: g.features
            };
        });

        var currentPlayers = self.numberOfCommonGamers();

        result = _.filter(result, function (r) {
            return r.players.length >= currentPlayers;
        });

        this.gamesTable(result);

        this.gridViewModel.currentPageIndex(0);

        self.gamesTable.sort(currentSort);
    };

    this.gamesTable = ko.observableArray([]);

    this.gridViewModel = new ko.simpleGrid.viewModel({
        data: this.gamesTable,
        columns: [
            { headerText: 'Game', cssClass: 'iconCol', rowHtml: function (row) {
                return '<a target="_blank" href="' + row.storeUrl + '"><img src="' + row.iconUrl + '" alt="' + row.name + '" /></a>';
            }
            },

            { headerText: 'Players', cssClass: 'playersCol', rowHtml: function (row) {
                return _.map(row.players, function (p) { return '<span>' + p + '</span>'; }).join('');
            }
            },

            { headerText: 'Genres', cssClass: 'genresCol', rowHtml: function (row) {
                return _.map(row.genres, function (g) { return '<span>' + g + '</span>'; }).join('');
            }
            },

            { headerText: 'Features', cssClass: 'featuresCol', rowHtml: function (row) {
                return _.map(row.features, function (f) { return '<span>' + f + '</span>'; }).join('');
            }
            },

            { headerText: 'Action', cssClass: 'actionsCol', rowHtml: function (row) {
                return '<a target="_blank" href="' + row.storeUrl + '">store</a><a href="' + row.playUrl + '">play</a>';
            }
            }
        ],
        pageSize: 10
    });

    this.sortTableByName = function () {
        updateCurrentSort(function (a, b) {
            return a.name < b.name ? -1 : 1;
        });
    };

    this.sortTableByPlayers = function () {
        updateCurrentSort(function (a, b) {
            return a.players.length > b.players.length ? -1 : 1;
        });
    };

    var currentSort;
    var updateCurrentSort = function (sorter) {
        currentSort = sorter;

        self.gamesTable.sort(sorter);
    };
    this.sortTableByName();

    this.search = function () {
        self.isSearching(true);

        $.ajax({
            url: '/api/players',
            data: {
                term: this.searchTerm()
            },
            complete: function () {
                self.isSearching(false);
            },
            success: function (data) {
                if (!data || !data.success || data.results.length == 0) {
                    alert('No results');
                    return;
                }

                var models = [];
                for (var x = 0; x < data.results.length; x++) {
                    models.push(new SearchResultModel(data.results[x]));
                }

                self.results(models);

                self.searchTerm('');
            }
        });
    };
};

var rootModel = new ViewModel();

ko.applyBindings(rootModel);

configureAjaxHandling();

var steamId = $.cookie('profile_id');
if (steamId) {
    addGamer(steamId, rootModel.isSearching)
}