angular.module('PlexWatchSync')
    .controller('LoginController', ['$scope', '$http', '$log', LoginController]);

function LoginController($scope, $http, $log) {
    $scope.message = 'test';
    $scope.loginForm = {
        username: '',
        password: '',
        working: false,
        response: null
    }
    $scope.loginAction = function () {
        $scope.loginForm.working = true;
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
                'user[login]': $scope.loginForm.username,
                'user[password]': $scope.loginForm.password
            }
        }).then(function successCallback(response){
            $log.info(response);
            response.config = null;
            $scope.loginForm.response = JSON.stringify(response, undefined, 4);
            $scope.loginForm.working = false;
        }, function errorCallback(response){
            $log.error(response);
            response.config = null;
            $scope.loginForm.response = JSON.stringify(response, undefined, 4);
            $scope.loginForm.working = false;
        });
    }
}