<?
$array = array();
$array[] = 'safe' ;
$array[] = $_GET['userData'] ;
$array[] = 'safe' ;
$tainted = $array[1] ;


class CWE_79_XSS__arrayGETfunc_addslashesUnsafe_use_untrusted_dataattribute_Name_class1{
	private $_data;
	public function __construct($data){
		$this->setData($data);
	}
	public function setData($data){
		$this->_data = $data;
	}
	public function a(){
		$tainted = $this->_data;
		$tainted = addslashes($tainted);
		return $tainted;
	}
}
$a = new CWE_79_XSS__arrayGETfunc_addslashesUnsafe_use_untrusted_dataattribute_Name_class1($tainted);
$tainted = $a->a();


//flaw
echo "<div ". $tainted ."= bob />" ;