var GameModel = function (result) {
    this.id = result.id;
    this.isValid = result.isValid;
    this.name = result.name;
    this.iconUrl = result.iconUrl;

    this.features = result.features;
    this.genres = result.genres;
};
