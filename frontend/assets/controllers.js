(function () {
    angular.module('PlexWatchSync')
    .controller('LoginController', ['$scope', '$sessionStorage', '$window', 'PlexService', 'PlexWatchService', LoginController]);

    function LoginController($scope, $sessionStorage, $window, plexService, plexWatchService) {
        $scope.loginForm = {
            username: '',
            password: '',
            working: false,
            error: [],
        };
        $scope.authForm = {
            working: false,
            error: [],
        };
        $scope.debug = false;

        $scope.session = $sessionStorage;

        $scope.loginAction = function () {
            delete $sessionStorage.plexData;
            $scope.loginForm.working = true;
            $scope.loginForm.error = [];
            plexService.login($scope.loginForm.username, $scope.loginForm.password
            ).then(function (data) {
                $scope.loginForm.working = false;
                $sessionStorage.plexData = data;
                $scope.loginForm.username = '';
                $scope.loginForm.password = '';
                checkRegistered();
            }, function (data) {
                $scope.loginForm.working = false;
                $scope.loginForm.error.push({ title: 'Error', error: data.error });
            });
        }

        $scope.authAction = function () {
            $scope.authForm.working = true;
            $scope.authForm.error = [];
            plexWatchService.auth($scope.session.plexData.authToken
            ).then(function (data) {
                $scope.authForm.working = false;
                $window.alert('Successfully registered!');
                $sessionStorage.plexData.registered = true;
            }, function (data) {
                $scope.authForm.working = false;
                $scope.authForm.error.push({ title: 'Error', error: data.error });
            });
        };

        var checkRegistered = function () {
            plexWatchService.userExists($scope.session.plexData.userId)
                .then(function (data) {
                    $scope.session.plexData.registered = true;
                }, function (data) {
                    $scope.session.plexData.registered = false;
                });
        };

        $scope.removeError = function (item) {
            var index = $scope.loginForm.error.indexOf(item);
            $scope.loginForm.error.splice(index, 1);
        }
        var init = function () {
            if ($scope.session.plexData && $scope.session.plexData.userId) {
                checkRegistered();
            }
        }
        init();
    }
})();