<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

require 'Predis/Autoloader.php';

Predis\Autoloader::register();

function test_redis($host) {
    try {
        $client = new Predis\Client([
            'scheme' => 'tcp',
            'host'   => $host,
            'port'   => 6379,
        ]);
        $client->connect();
        return true;
    } catch (Exception $e) {
        return false;
    }
}

$master_host = 'redis-master';
$slave_host = 'redis-slave';
if (getenv('GET_HOSTS_FROM') == 'env') {
    $master_host = getenv('REDIS_MASTER_SERVICE_HOST');
    $slave_host = getenv('REDIS_SLAVE_SERVICE_HOST');
}

if (test_redis($master_host) && test_redis($slave_host)) {
    http_response_code(200);
} else {
    http_response_code(500);
}

?>
