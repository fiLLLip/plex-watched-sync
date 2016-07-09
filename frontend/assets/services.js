(function () {
    angular.module('PlexWatchSync').service('PlexService', ['$http', '$log', '$q', PlexService]).service('PlexWatchService', ['$http', '$log', '$q', PlexWathService]);

    function PlexService($http, $log, $q) {
        var login = function (username, password) {
            return $q(function (resolve, reject) {
                $http({
                    method: 'POST',
                    url: 'https://plex.tv/users/sign_in.json',
                    headers: {
                        'X-Plex-Product': 'PlexWatchSync',
                        'X-Plex-Version': '0.1',
                        'X-Plex-Client-Identifier': 'PlexWatchSync',
                        'Content-Type': 'multipart/form-data'
                    },
                    params: {
                        'user[login]': username,
                        'user[password]': password
                    }
                }).then(function successCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.info(response);
                    resolve({
                        userId: response.data.user.id,
                        authToken: response.data.user.authToken
                    });
                }, function errorCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.error(response);
                    reject({ error: response.data.error });
                });
            });
        }

        return {
            login: login
        };
    }

    function PlexWathService($http, $log, $q) {
        var baseUrl = 'http://plexsync.filllip.net:8080/api';
        var auth = function (authToken) {
            return $q(function (resolve, reject) {
                $http({
                    method: 'POST',
                    url: baseUrl + '/user/login',
                    headers: {
                        'X-token': authToken
                    }
                }).then(function successCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.info(response);
                    resolve();
                }, function errorCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.error(response);
                    reject({ title: response.data.title, error: response.data.description });
                });
            });
        }

        var userExists = function (accountId) {
            return $q(function (resolve, reject) {
                $http({
                    method: 'GET',
                    url: baseUrl + '/user/' + accountId
                }).then(function successCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.info(response);
                    resolve();
                }, function errorCallback(response) {
                    response.config = null; // Don't show request (with cleartext password) in log
                    $log.error(response);
                    reject({ title: 'Error', error: 'User ' + accountId + ' is not registered with Plex Watched Sync' });
                });
            });
        }

        return {
            auth: auth,
            userExists: userExists
        };
    }
})();