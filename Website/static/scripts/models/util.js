if (typeof Spinner == 'function') {
    var spinner = new Spinner({
        lines: 12, // The number of lines to draw
        length: 7, // The length of each line
        width: 4, // The line thickness
        radius: 7, // The radius of the inner circle
        color: '#FFF', // #rgb or #rrggbb
        speed: 1, // Rounds per second
        trail: 60, // Afterglow percentage
        shadow: false // Whether to render a shadow
    });
    var $spinners = $('.loading');
    for (var x = 0; x < $spinners.length; x++) {
        spinner.spin($spinners[x]);
    }
}

function addGamer(gamerId, inProcessMarker) {
    inProcessMarker(true);

    var payload = {};
    if (gamerId != null) {
        payload.gamerIds = gamerId;
    }

    $.ajax({
        url: '/api/gamers',
        data: payload,
        complete: function () {
            inProcessMarker(false);
        },
        success: function (data) {
            if (!data || !data.success || data.results.length <= 0) {
                alert('Gamer does not exist');
                return;
            }

            var newGamers = [];
            for (var x = 0; x < data.results.length; x++) {
                var gamer = data.results[x];

                newGamers.push(new GamerModel(gamer));
            }

            rootModel.gamers.push.apply(rootModel.gamers, newGamers);
        }
    });
}

function updateSelectableList(source, games, mapper) {
	var currentSelectables = source();

	var selectables = _.map(games, mapper);

	selectables = _.flatten(selectables);

	selectables = _.uniq(selectables);

	selectables = _.filter(selectables, function (s) {
		return s != null && s.length && s.length > 0;
	});

	var selectables = _.map(selectables.sort(), function (f) {
		return new SelectableModel(f);
	});

	for (var x = 0; x < selectables.length; x++) {
		var newSelectable = selectables[x];
		var existing = _.find(currentSelectables, function (s) {
			return s.name == newSelectable.name;
		});

		if (existing != null) {
			newSelectable.selected(existing.selected());
		}
	}

	source(selectables);
}

function filterGamesBySelectables(source, games, target) {
	var selectedItems = _.filter(source(), function (f) {
		return f.selected();
	});

	selectedItems = _.map(selectedItems, function (f) {
		return f.name;
	});

	if (selectedItems.length > 0) {
	    games = _.filter(games, function (g) {
	        if (!g.isValid) {
	            return false;
	        }
	        var targetItems = target(g);
	        if (targetItems == null) {
	            return false;
	        }

	        var matchingItems = _.intersection(target(g), selectedItems);

	        return matchingItems.length == selectedItems.length;
	    });
	}

	return games;
};

Array.prototype.remove = function (from, to) {
	var rest = this.slice((to || from) + 1 || this.length);
	this.length = from < 0 ? this.length + from : from;
	return this.push.apply(this, rest);
};

var missingGameThreadId;
function checkForMissingGameMetadata() {
    if (missingGameThreadId) {
        // already running, escape
        return;
    }

    missingGameThreadId = setTimeout(function () {
        var start = new Date().getTime();
        do {
            var gamers = rootModel.gamers();

            var games = rootModel.games();

            var gameIdsFromGamers = _.pluck(gamers, 'gameIds');
            var neededGameIds = _.flatten(gameIdsFromGamers);
            var uniqueGameIds = _.uniq(neededGameIds);
            console.log('checking ' + uniqueGameIds.length + ' games to see if any haven\'t been downloaded');

            var missingGameIds = _.filter(uniqueGameIds, function (gameId) {
                return _.all(games, function (g) {
                    return g.id != gameId;
                });
            });
            console.log('' + missingGameIds.length + ' haven\'t been downloaded');

            if (missingGameIds.length == 0) {
                console.log('No missing games');
                break;
            }

            $('#status').html('Downloading ' + missingGameIds.length + ' games');

            var sliceLength = 20;
            for (var x = 0; x < missingGameIds.length; x += sliceLength) {
                var thisCheck = missingGameIds.slice(x, x + sliceLength);

                var result = getMissingGames(thisCheck);
                if (!result) {
                    return;
                }
            }
        } while (true);

        var stop = new Date().getTime();

        console.log('downloading games took ' + (stop - start) / 1000 + ' seconds');

        missingGameThreadId = null;
    });
}

function getMissingGames(missingGameIds) {
    if (!missingGameIds || !(missingGameIds instanceof Array) || missingGameIds.length == 0) {
        console.log('No missing games');
        return false;
    }

    console.log('Searching for games ... ');

    var payload = '';
    for (var x = 0; x < missingGameIds.length; x++) {
        payload += 'gameIds=' + missingGameIds[x] + '&';
    }

    var result = false;

    $.ajax({
        async: false,
        url: '/api/games',
        data: payload,
        error: function () {
            result = false;
        },
        success: function (data) {
            if (!data || !data.success || data.results.length <= 0) {
                result = false;
            }

            //var games = rootModel.games();
            var g = [];
            for (var x = 0; x < data.results.length; x++) {
                var model = new GameModel(data.results[x]);
                g.push(model);
            }
            rootModel.games.push.apply(rootModel.games, g);

            result = true;
        }
    });

    return result;
}