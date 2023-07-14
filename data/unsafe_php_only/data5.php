<?$array = array();
$array[] = 'safe' ;
$array[] = $_GET['userData'] ;
$array[] = 'safe' ;
$tainted = $array[1] ;

$tainted = addslashes($tainted);

//flaw
echo "<".  $tainted ." href= \"/bob\" />" ;