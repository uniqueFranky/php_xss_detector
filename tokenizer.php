<?php
$tokens = PhpToken::tokenize($argv[1]);
foreach ($tokens as $token) {
    echo "{$token->text},";
}