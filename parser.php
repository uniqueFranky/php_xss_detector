<?php
require_once 'vendor/autoload.php';

use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;

$code = $argv[1];
$parser = (new ParserFactory)->create(ParserFactory::PREFER_PHP7);
try {
    $ast = $parser->parse($code);
    echo json_encode($ast, JSON_PRETTY_PRINT), "\n";
} catch (Error $error) {
    echo "Parse error: {$error->getMessage()}\n";
    return;
}
