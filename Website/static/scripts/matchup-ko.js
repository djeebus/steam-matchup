$.validator.methods.duplicate = function (value, element) {
    return this.optional(element) ||
        ko.utils.arrayFirst(matchupViewModel.gamers(), function (g) { return g.id == value; }) == null;
};

var $form = $('form#add-user');
$form.validate({
    errorElement: 'span',
    errorLabelContainer: $('.errors'),
    rules: {
        username: {
            required: true,
            duplicate: true
        }
    },
    messages: {
        username: {
            required: 'You must enter a username.',
            duplicate: 'This user has already been added.'
        }
    }
});

$('#players .user a.friends').live('click', function () {
    $(this).next('.friends-dialog').dialog({
        title: 'Friends',
        width: 145
    });
});

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
spinner.spin($('.loading')[0]);

var Gamer = function (user, friends, context) {
    this.id = user.Id;
    this.name = user.Username;
    this.iconUrl = user.IconUrl;
    this.url = user.CommunityUrl;
    this.stats = _.map(user.Stats, function (s) { return { name: s.Name, value: s.Value }; });

    this.friends = friends == null ? null : _.map(friends, function (f) {
        return new Gamer(f, null, context);
    });

    this.context = context;

    this.add = function () {
        this.context.addPlayer(this.id);

        $('[role=dialog]').hide();
    };

    this.remove = function () {
        this.context.removePlayer(this.id);
    };
};

var Game = function (g, context) {
    this.name = g.Name;
    this.iconUrl = g.IconUrl;
    this.url = g.SteamUrl;

    this.players = ko.observableArray([]);
};

function populateSelect(element, totalPlayers) {
    var $e = $(element);
    $e.empty();
    for (var x = 1; x <= totalPlayers; x++) {
        $e.append($('<option />').html(x).val(x));
    }
}

ko.bindingHandlers.playersList = {
    init: function (element, valueAccessor) {
        populateSelect(element, valueAccessor());
    },
    update: function (element, valueAccessor) {
        populateSelect(element, valueAccessor());
    }
};

var matchupViewModel = {
    newPlayerName: ko.observable(''),
    games: ko.observableArray([]),
    gamers: ko.observableArray([]),
    minimumInCommon: ko.observable(1),
    csvGamers: ko.observable(''),

    updateCsv: function () {
        var gamerIds = _.map(this.gamers(), function (g) { return g.id; });
        this.csvGamers(gamerIds.toString());
    },

    submitNewPlayer: function () {
        if (!$form.valid()) {
            return;
        }

        var username = this.newPlayerName();

        this.addPlayer(username);
    },

    addPlayer: function (username, killPrevious) {
        if (username == null || typeof username == 'undefined' || username.length == 0) {
            return;
        }

        killPrevious = typeof killPrevious == 'undefined' ? true : killPrevious;

        var existing = ko.utils.arrayFirst(this.gamers(), function (g) { return g.id == username; });
        if (existing != null) {
            return;
        }

        if (killPrevious) {
            if (this.userReq != null) {
                this.userReq.abort();
            }
        }

        this.userReq = $.ajax('/get', {
            context: this,
            data: {
                username: username
            },
            type: 'POST',

            beforeSend: function () {
                this.disableInputs();
            },
            success: function (data) {
                var gamer = this.handleUserInfo(username, data.User, data.Friends);

                this.handleGames(gamer, data.Games);
            },
            error: function () {
                alert('error pulling user information');
            },
            complete: function () {
                this.enableInputs();

                this.newPlayerName('');
            }
        });
    },

    removePlayer: function (id) {
        var gamers = this.gamers();

        var removed = null;

        for (var x = 0; x < gamers.length; x++) {
            if (gamers[x].id == id) {
                removed = this.gamers.splice(x, 1)[0];
                break;
            }
        }

        if (removed == null) {
            return; // didn't find anyone
        }

        var games = this.games();
        for (var x = 0; x < games.length; x++) {
            var game = games[x];
            var players = game.players();

            for (var y = 0; y < players.length; y++) {
                if (players[y].id == id) {
                    game.players.splice(y, 1);
                    break;
                }
            }
        }
    },
    disableInputs: function () {
        $form.find('input[type=text],button').attr('disabled', 'disabled');
        $form.find('.loading').fadeIn();
    },
    enableInputs: function () {
        $form.find('input[type=text],button').removeAttr('disabled');
        $form.find('.loading').fadeOut();
    },
    handleUserInfo: function (steamId, user, friends) {
        var gamer = null;

        var existing = _.filter(this.gamers(), function (g) { return g.id == steamId; });
        if (existing.length == 0) {
            gamer = new Gamer(user, friends, this);
            this.gamers.push(gamer);
        } else {
            gamer = existing[0];
        }

        return gamer;
    },
    handleGames: function (gamer, games) {
        var master = this.games();

        for (var x = 0; x < games.length; x++) {
            var game = new Game(games[x]);

            var existing = _.filter(master, function (g) { return g.url == game.url; });
            if (existing.length == 0) {
                master.push(game);
                existing[0] = game;
            }

            existing[0].players.push(gamer);
        }

        master.sort(function (g1, g2) {
            if (g1.name < g2.name)
                return -1;
            else if (g1.name > g2.name)
                return 1;
            else
                return 0;
        });

        this.games(master);
    },
    getPlayers_success: function (data) {
        var player = new Player(this.newPlayerName(), data);

        this.players.push(player);

        this.addGames(data);
    }
};
matchupViewModel.gamers.subscribe(function () {
    matchupViewModel.updateCsv();
});
matchupViewModel.csvGamers.subscribe(function (newValue) {
    if (newValue == null || typeof newValue == 'undefined') {
        return;
    }

    var gamerIds = newValue.split(',');

    for (var x = 0; x < gamerIds.length; x++) {
        matchupViewModel.addPlayer(gamerIds[x], false);
    }
});
ko.linkObservableToUrl(matchupViewModel.csvGamers, "gamers");

// doesn't work to reload state due to async callbacks
//ko.linkObservableToUrl(matchupViewModel.minimumInCommon, "min");

window.matchupViewModel = matchupViewModel;
ko.applyBindings(matchupViewModel);