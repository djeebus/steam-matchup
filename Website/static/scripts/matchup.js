(function ($) {
	$(document).ready(function () {
		$('form#add-user').submit(function () {
			if ($(this).valid()) {
				var username = $('#username').val();

				var exists = false;
				$.each(users, function () {
					if (this.username == username) {
						exists = true;
						return false;
					}
				});

				if (exists) {
					alert("This user is already being compared.");
				} else {
					addUser(username);
				}
			}

			return false;
		});

		$('form#add-user').validate();

		$('#show-missing').change(hideMissingPlayers);

		$('#friends .friend a.add').live('click', function () {
			var username = $(this).parents('.friend').attr('id');

			addUser(username);
		});

		$('.user a').live('click', function (e) {
			e.preventDefault();

			var index = $(this).data('user-index');

			removeUser(index);

			return false;
		});

		$('#options').accordion({
			collapsible: true,
			autoHeight: false,
			active: false
		});
	});

	function addUser(username) {
		addUserToComparison(username);

		addFriendsToContainer(username);
	}

	function removeUser(index) {
		users.splice(index, 1);
		friends.splice(index, 1);

		updatePlayers();
		updateFriends();
	}

	function hideMissingPlayers() {
		var minPlayers = $('#show-missing').val();

		for (var x = users.length; x > 0; x--) {
			var $games = $('.game.players-' + x);

			if (x >= minPlayers) {
				$games.show();
			} else {
				$games.hide();
			}
		}

		var total = $("<h3><span class='games-shown' /> games displayed</h3>");
		total.find('.games-shown').text($('.game:visible').length / users.length);

		$('#users').prepend(total);
	}

	var friends = [];
	function addFriendsToContainer(username) {
		$.ajax('/home/getfriends', {
			type: 'POST',
			data: {
				username: username
			},
			success: function (data) {
				data.username = username;

				friends[friends.length] = data;
                    
				updateFriends();
			},
			error: function (req, status) {
				// error will probably be shown when trying to get their games
				//alert(status + ': ' + req.responseText);
			}
		});
	}

	var users = [];
	function addUserToComparison(username) {
		$('input[type=submit]').attr('disabled', 'disabled');
		$.ajax('/home/getgames', {
			type: 'POST',
			data: {
				username: username
			},
			success: function (data) {
				data.username = username;
				users[users.length] = data;

				updatePlayers();

				$.each(friends, function (x) {
					if (this.id == username) {
						friends.splice(x, 1);
						return false;
					}
				});
			},
			error: function (req, status) {
				alert('error: this user does not exist, or does not have their profile set up.');
			},
			complete: function () {
				$('input[type=submit]').removeAttr('disabled');
			}
		});
	}

	function updateFriends() {
		var uniqueFriends = getUniqueFriends();

		sortByName(uniqueFriends);

		$('#friends').empty();
		var tmpl = $('#friend').tmpl(uniqueFriends);
		tmpl.appendTo('#friends');
	}

	function getUniqueFriends() {
		var unique = [];
		$.each(friends, function () {
			var oneUsersFriends = this;

			$.each(oneUsersFriends, function () {
				var userFriend = this;

				var exists = false;

				$.each(unique, function () {
					if (this.id == userFriend.CommunityId) {
						exists = true;
						return false;
					}
				});

				$.each(users, function () {
					if (this.username == userFriend.CommunityId) {
						exists = true;
						return false;
					}
				});

				if (!exists) {
					unique[unique.length] = {
						steam: this.CommunityUrl,
						icon: this.IconUrl,
						name: this.Name,
						id: this.CommunityId
					};
				}
			});
		});

		return unique;
	}

	function updatePlayers() {
		var games = mergeGamesArrays();

		sortByName(games);

		generateLists(games);

		hideMissingPlayers();
	}

	function generateLists(games) {
		$('#users').empty();

		updateMissingOption();

		for (var u = 0; u < users.length; u++) {
			var user = users[u];

			var container = $('<div class="user"><h2><span class="username" /><a class="remove" href="javascript:void(0)">remove</a></h2><h3><span class="mine" /> games</div>');
			container.find('.username').text(user.username);
			container.find('a').data('user-index', u);

			var total = 0, mine = 0;

			$.each(games, function () {
				total++;
				var game = this;
				var exists = false;

				$.each(user, function () {
					var userGame = this;
					if (userGame.SteamUrl == game.steam) {
						exists = true;
						return false;
					}
				});
				if (exists) { mine++; }
				$('#game').tmpl(game, { 'css': exists ? 'exists' : 'missing' }).appendTo(container);
			});

			container.find('.mine').text(user.length);

			$('#users').append(container);
		}
	}

	function updateMissingOption() {
		var $select = $('#show-missing');
		$select.empty();

		for (var x = users.length; x > 0; x--) {
			var $option = $('<option />');
			$option.text(x);
			$select.append($option);
		}

		if (users.length < 2) {
			$('.show-missing').hide();
		} else {
			$('.show-missing').show();
		}
	}

	function mergeGamesArrays() {
		var games = [];

		$.each(users, function () {
			var u = this;

			$.each(this, function () {
				var userGame = this;

				var g = null;

				$.each(games, function () {
					if (this.steam == userGame.SteamUrl) {
						g = this;
						return false;
					}
				});

				if (g === null) {
					g = {
						name: userGame.Name,
						icon: userGame.IconUrl,
						steam: userGame.SteamUrl,
						players: 0
					};

					games[games.length] = g;
				}

				g.players++;
			});
		});

		return games;
	}

	function sortByName(array) {
		array.sort(function (a, b) {
			var x = a.name.toLowerCase();
			var y = b.name.toLowerCase();
			if (x < y)
				return -1;
			else if (x > y)
				return 1;
			else
				return 0;
		});
	}
})(jQuery);