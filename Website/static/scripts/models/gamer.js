var GamerModel = function (result) {
	this.id = result.id;
	this.name = result.name;
	this.gameIds = result.gameIds;
	this.iconUrl = result.iconUrl;

	this.displayFriends = ko.observable(false);

	this.toggleFriends = function () {
		this.displayFriends(!this.displayFriends());
	};

	var friendModels = [];
    var sortedFriends = _.sortBy(result.friends, function (f) {
        return f.name;
    });
	for (var f = 0; f < sortedFriends.length; f++) {
		friendModels.push(new FriendModel(sortedFriends[f]));
	}

	this.friends = ko.observableArray(friendModels);

	this.remove = function () {
		var gamers = rootModel.gamers();

		var withoutMe = _.without(gamers, this);

		rootModel.gamers(withoutMe);
	};
};