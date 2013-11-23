var SelectableModel = function (feature) {
    this.name = feature;
    this.selected = ko.observable(false);

    this.selected.subscribe(function (newValue) {
        rootModel.recalculateGamesTable();
    });
};