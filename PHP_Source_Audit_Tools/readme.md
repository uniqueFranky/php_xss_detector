
## PHP_Source_Audit_Tools

  Just for Fun .
  
  去年写的白盒自动化审计工具,原理是定位到敏感函数之后,再对函数所使用的参数进行回溯,跟踪到$_GET $_REQUEST 这些可以控制的输入点,但是由于PHP 语法糖和代码的问题,导致分析结果会有所出入,测试效果不错,但是实战效果不佳,故开源它的源码,有机会的话写一篇文章来说说自动化源码漏洞挖掘分析
  
  原理
  
![sample.png](sample.png)
  
## Example

![mmexport1504837705156.jpg](mmexport1504837705156.jpg)
  
  
## USE

remember to use python2

```shell
python code_analysis.py test_php/test.php
```
