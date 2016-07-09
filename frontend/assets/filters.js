angular.module('PlexWatchSync').filter('json', JsonFilter);

function JsonFilter() {
    return function (input) {
        return JSON.stringify(input, undefined, 4);
    };
}
