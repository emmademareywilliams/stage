# PHP programming language 

PHP is one of the most commonly used languages to generate dynamic websites.

Here are some basic notions about the PHP language, to which I am totally 
new. For more information, see [this lecture](https://youtu.be/OK_JCtrrv-c)
about the PHP language. 


## Getting started  

PHP needs to be run on a web server. In order to create the server that will 
support the code, we must use the following command : 

```
php -S localhost:4000
```

The associated files will be found in the folder `/home/ludivine/www` (on the Linux machine). 

We must generate an HTML skeleton for the file in order for the PHP script to be read and integrated into the web server. 

To write PHP inside an HTML script, we need to use the PHP tag `<?php` at the start of the code and `?>` and the end. 

> At the end of each instruction, we MUST put `;` 


## Some basic functions 

#### echo 

*echo* enables the PHP code to be printed in the HTML file. We can even include HTML commands into a PHP tag. 

```
echo "test";  // same thing as echo("test")
echo "<p> this is a test </p>";
```


## Variables 

A variable in PHP is identified by a `$`. 

