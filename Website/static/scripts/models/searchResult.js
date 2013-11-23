var SearchResultModel = function (result) {
	var self = this;

	this.id = result.id;
	this.iconUrl = result.iconUrl;
	this.name = result.name;

	this.canSelect = ko.computed(function () {
		var existing = _.find(rootModel.gamers(), function (g) {
			return g.id == self.id;
		});

		return existing == null;
	}, self);

	this.addResult = function () {
		addGamer(this.id, rootModel.isSearching);
	};
};