<?php
require 'D:\CTFtools\web\phpstudyv8.1\phpstudy_pro\Extensions\composer1.8.5\vendor\autoload.php';
use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;

//$files = glob("./safe_php_only/*.php"); // 获取safe文件夹下的所有PHP文件
$files = glob("./unsafe_php_only/*.php"); // 获取unsafe文件夹下的所有PHP文件

$parser = (new ParserFactory)->create(ParserFactory::PREFER_PHP7);
$dumper = new NodeDumper;

foreach ($files as $file) {
    $code = file_get_contents($file);

    try {
        $ast = $parser->parse($code);
    } catch (Error $error) {
        echo "Parse error in file $file: {$error->getMessage()}\n";
        continue;
    }

    $result = $dumper->dump($ast) . "\n";
    $filename = basename($file);
    //$outputFile = "./safe_ast/$filename"; // 保存处理结果的文件路径
    $outputFile = "./unsafe_ast/$filename"; // 保存处理结果的文件路径


    file_put_contents($outputFile, $result); // 将处理结果写入文件

    echo "Processed file $file\n";
}
